#!/usr/bin/env python3
"""
Streaming encoder examples for uubed.

This module demonstrates real-time streaming encoding capabilities for
various use cases:
- Real-time embedding generation and encoding
- WebSocket streaming
- Kafka integration
- Low-latency encoding pipelines
- Backpressure handling

Requirements:
    - uubed (core library)
    - numpy
    - asyncio
    - Optional: websockets, kafka-python, aiohttp
"""

import asyncio
import time
import json
import numpy as np
from typing import AsyncIterator, List, Dict, Any, Optional, Callable
from collections import deque
from dataclasses import dataclass
from datetime import datetime
import threading
import queue

from uubed import (
    encode, decode, batch_encode,
    encode_stream, StreamingEncoder,
    UubedError
)

# Optional imports
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Note: Install websockets for WebSocket examples")

try:
    from kafka import KafkaProducer, KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("Note: Install kafka-python for Kafka examples")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("Note: Install aiohttp for HTTP streaming examples")


@dataclass
class StreamingMetrics:
    """Metrics for streaming performance monitoring."""
    messages_processed: int = 0
    bytes_processed: int = 0
    encoding_time_ms: float = 0
    throughput_msg_per_sec: float = 0
    latency_p50_ms: float = 0
    latency_p95_ms: float = 0
    latency_p99_ms: float = 0
    backpressure_events: int = 0
    
    def update_latencies(self, latencies: List[float]):
        """Update percentile latencies."""
        if not latencies:
            return
        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)
        self.latency_p50_ms = sorted_latencies[int(n * 0.5)]
        self.latency_p95_ms = sorted_latencies[int(n * 0.95)]
        self.latency_p99_ms = sorted_latencies[int(n * 0.99)]


class AsyncStreamingEncoder:
    """Asynchronous streaming encoder with backpressure handling."""
    
    def __init__(self, 
                 encoding_method: str = "shq64",
                 buffer_size: int = 1000,
                 batch_size: int = 50):
        self.encoding_method = encoding_method
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.buffer = asyncio.Queue(maxsize=buffer_size)
        self.metrics = StreamingMetrics()
        self.latencies = deque(maxlen=1000)  # Keep last 1000 latencies
        self._running = False
    
    async def start(self):
        """Start the streaming encoder."""
        self._running = True
        asyncio.create_task(self._process_loop())
    
    async def stop(self):
        """Stop the streaming encoder."""
        self._running = False
        await self.buffer.join()
    
    async def encode_one(self, embedding: np.ndarray) -> str:
        """Encode a single embedding with metrics tracking."""
        start_time = time.time()
        
        try:
            # Convert to uint8 if needed
            if embedding.dtype != np.uint8:
                embedding = (embedding * 255).clip(0, 255).astype(np.uint8)
            
            # Encode
            encoded = encode(embedding, method=self.encoding_method)
            
            # Update metrics
            latency = (time.time() - start_time) * 1000
            self.latencies.append(latency)
            self.metrics.messages_processed += 1
            self.metrics.bytes_processed += len(encoded)
            self.metrics.encoding_time_ms += latency
            
            return encoded
            
        except UubedError as e:
            print(f"Encoding error: {e}")
            return ""
    
    async def submit(self, embedding: np.ndarray) -> bool:
        """Submit embedding for encoding with backpressure handling."""
        try:
            self.buffer.put_nowait(embedding)
            return True
        except asyncio.QueueFull:
            self.metrics.backpressure_events += 1
            return False
    
    async def _process_loop(self):
        """Main processing loop."""
        batch = []
        last_metrics_update = time.time()
        
        while self._running:
            try:
                # Collect batch with timeout
                deadline = time.time() + 0.1  # 100ms batch window
                
                while len(batch) < self.batch_size and time.time() < deadline:
                    try:
                        timeout = max(0, deadline - time.time())
                        embedding = await asyncio.wait_for(
                            self.buffer.get(), 
                            timeout=timeout
                        )
                        batch.append(embedding)
                    except asyncio.TimeoutError:
                        break
                
                # Process batch if we have items
                if batch:
                    # Batch encode
                    batch_array = np.array(batch)
                    encoded_batch = batch_encode(batch_array, method=self.encoding_method)
                    
                    # Update metrics
                    for encoded in encoded_batch:
                        self.metrics.bytes_processed += len(encoded)
                    
                    batch.clear()
                
                # Update throughput metrics periodically
                if time.time() - last_metrics_update > 1.0:
                    elapsed = time.time() - last_metrics_update
                    self.metrics.throughput_msg_per_sec = (
                        self.metrics.messages_processed / elapsed
                    )
                    self.metrics.update_latencies(list(self.latencies))
                    last_metrics_update = time.time()
                    
            except Exception as e:
                print(f"Processing error: {e}")
                await asyncio.sleep(0.1)


async def websocket_streaming_example():
    """
    Demonstrate WebSocket-based streaming encoding.
    
    Shows real-time encoding for web applications.
    """
    if not WEBSOCKETS_AVAILABLE:
        print("=== WebSocket Streaming (Simulated) ===")
        print("websockets library not available.")
        return
    
    print("=== WebSocket Streaming Example ===")
    
    async def embedding_server(websocket, path):
        """WebSocket server that encodes received embeddings."""
        encoder = AsyncStreamingEncoder(encoding_method="shq64")
        await encoder.start()
        
        print(f"Client connected from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                # Parse incoming embedding
                data = json.loads(message)
                embedding = np.array(data['embedding'], dtype=np.float32)
                
                # Encode
                encoded = await encoder.encode_one(embedding)
                
                # Send response
                response = {
                    'id': data.get('id', 'unknown'),
                    'encoded': encoded,
                    'method': encoder.encoding_method,
                    'timestamp': time.time()
                }
                
                await websocket.send(json.dumps(response))
                
                # Send metrics periodically
                if encoder.metrics.messages_processed % 100 == 0:
                    metrics_msg = {
                        'type': 'metrics',
                        'data': {
                            'processed': encoder.metrics.messages_processed,
                            'throughput': encoder.metrics.throughput_msg_per_sec,
                            'latency_p50': encoder.metrics.latency_p50_ms
                        }
                    }
                    await websocket.send(json.dumps(metrics_msg))
                    
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:
            await encoder.stop()
    
    # Simulate WebSocket interaction
    print("WebSocket server example (not running actual server)")
    print("Server would handle:")
    print("  - Real-time embedding encoding")
    print("  - Streaming metrics")
    print("  - Backpressure handling")
    print()


async def kafka_streaming_example():
    """
    Demonstrate Kafka-based streaming pipeline.
    
    Shows integration with message queue systems.
    """
    if not KAFKA_AVAILABLE:
        print("=== Kafka Streaming (Simulated) ===")
        print("kafka-python not available.")
    else:
        print("=== Kafka Streaming Example ===")
    
    class KafkaStreamingEncoder:
        def __init__(self, 
                     input_topic: str,
                     output_topic: str,
                     encoding_method: str = "t8q64"):
            self.input_topic = input_topic
            self.output_topic = output_topic
            self.encoder = AsyncStreamingEncoder(encoding_method=encoding_method)
            self.running = False
        
        async def process_messages(self):
            """Process messages from Kafka."""
            # In real implementation:
            # consumer = KafkaConsumer(self.input_topic, ...)
            # producer = KafkaProducer(...)
            
            print(f"Processing from {self.input_topic} to {self.output_topic}")
            
            # Simulate message processing
            message_count = 0
            
            while self.running and message_count < 100:
                # Simulate receiving message
                embedding = np.random.rand(768).astype(np.float32)
                message_id = f"msg_{message_count}"
                
                # Encode
                encoded = await self.encoder.encode_one(embedding)
                
                # Simulate sending to output topic
                output_message = {
                    'id': message_id,
                    'encoded': encoded,
                    'encoding_method': self.encoder.encoding_method,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # producer.send(self.output_topic, output_message)
                
                message_count += 1
                
                # Show progress
                if message_count % 25 == 0:
                    print(f"  Processed {message_count} messages")
                    print(f"  Throughput: {self.encoder.metrics.throughput_msg_per_sec:.1f} msg/s")
                
                await asyncio.sleep(0.01)  # Simulate message arrival rate
            
            print(f"Completed processing {message_count} messages")
    
    # Create Kafka encoder
    kafka_encoder = KafkaStreamingEncoder(
        input_topic="embeddings-raw",
        output_topic="embeddings-encoded",
        encoding_method="shq64"
    )
    
    # Simulate processing
    kafka_encoder.running = True
    await kafka_encoder.encoder.start()
    await kafka_encoder.process_messages()
    await kafka_encoder.encoder.stop()
    
    # Show final metrics
    metrics = kafka_encoder.encoder.metrics
    print(f"\nKafka streaming metrics:")
    print(f"  Messages processed: {metrics.messages_processed}")
    print(f"  Bytes encoded: {metrics.bytes_processed}")
    print(f"  Avg latency: {metrics.encoding_time_ms / metrics.messages_processed:.2f}ms")
    print()


async def http_streaming_example():
    """
    Demonstrate HTTP streaming with Server-Sent Events.
    
    Shows integration with web APIs.
    """
    print("=== HTTP Streaming Example ===")
    
    class HTTPStreamingEncoder:
        def __init__(self, encoding_method: str = "shq64"):
            self.encoder = AsyncStreamingEncoder(encoding_method=encoding_method)
            self.active_streams = set()
        
        async def handle_stream(self, request_id: str) -> AsyncIterator[str]:
            """Generate Server-Sent Events stream."""
            self.active_streams.add(request_id)
            
            try:
                # Send initial connection event
                yield f"event: connected\ndata: {json.dumps({'request_id': request_id})}\n\n"
                
                # Process embeddings
                for i in range(50):  # Simulate 50 embeddings
                    # Generate embedding
                    embedding = np.random.rand(512).astype(np.float32)
                    
                    # Encode
                    encoded = await self.encoder.encode_one(embedding)
                    
                    # Create SSE event
                    event_data = {
                        'index': i,
                        'encoded': encoded,
                        'timestamp': time.time()
                    }
                    
                    yield f"event: embedding\ndata: {json.dumps(event_data)}\n\n"
                    
                    # Send metrics every 10 embeddings
                    if i % 10 == 0:
                        metrics_data = {
                            'processed': self.encoder.metrics.messages_processed,
                            'latency_p50': self.encoder.metrics.latency_p50_ms
                        }
                        yield f"event: metrics\ndata: {json.dumps(metrics_data)}\n\n"
                    
                    await asyncio.sleep(0.1)  # Simulate processing time
                
                # Send completion event
                yield f"event: complete\ndata: {json.dumps({'total': 50})}\n\n"
                
            finally:
                self.active_streams.remove(request_id)
    
    # Create HTTP encoder
    http_encoder = HTTPStreamingEncoder(encoding_method="zoq64")
    await http_encoder.encoder.start()
    
    # Simulate SSE stream
    print("Simulating Server-Sent Events stream...")
    request_id = "req_12345"
    
    event_count = 0
    async for event in http_encoder.handle_stream(request_id):
        event_count += 1
        if event_count <= 5:  # Show first few events
            print(f"Event {event_count}:")
            print(event[:100] + "..." if len(event) > 100 else event)
    
    await http_encoder.encoder.stop()
    
    print(f"\nGenerated {event_count} SSE events")
    print(f"Active streams: {len(http_encoder.active_streams)}")
    print()


async def low_latency_pipeline():
    """
    Demonstrate ultra-low latency encoding pipeline.
    
    Shows optimization techniques for minimal latency.
    """
    print("=== Low-Latency Pipeline Example ===")
    
    class LowLatencyEncoder:
        def __init__(self, 
                     encoding_method: str = "shq64",
                     prefetch_size: int = 10):
            self.encoding_method = encoding_method
            self.prefetch_size = prefetch_size
            self.encoder_pool = []
            self.ready_queue = asyncio.Queue()
            
            # Pre-initialize encoders
            for _ in range(prefetch_size):
                encoder = StreamingEncoder(
                    method=encoding_method,
                    batch_size=1  # Single item for lowest latency
                )
                self.encoder_pool.append(encoder)
        
        async def encode_ultra_low_latency(self, embedding: np.ndarray) -> Tuple[str, float]:
            """Encode with minimal latency."""
            start_time = time.perf_counter()
            
            # Get pre-warmed encoder
            encoder = self.encoder_pool.pop(0)
            
            # Encode immediately
            if embedding.dtype != np.uint8:
                embedding = (embedding * 255).clip(0, 255).astype(np.uint8)
            
            encoded = encode(embedding, method=self.encoding_method)
            
            # Return encoder to pool
            self.encoder_pool.append(encoder)
            
            # Calculate precise latency
            latency_us = (time.perf_counter() - start_time) * 1_000_000
            
            return encoded, latency_us
        
        async def benchmark_latencies(self, num_samples: int = 1000):
            """Benchmark encoding latencies."""
            latencies = []
            
            print(f"Benchmarking {num_samples} encodings...")
            
            for i in range(num_samples):
                # Generate embedding
                embedding = np.random.rand(384).astype(np.float32)
                
                # Encode and measure
                _, latency = await self.encode_ultra_low_latency(embedding)
                latencies.append(latency)
                
                # Minimal delay to simulate real conditions
                await asyncio.sleep(0.001)
            
            # Calculate statistics
            latencies.sort()
            return {
                'min': latencies[0],
                'p50': latencies[len(latencies)//2],
                'p95': latencies[int(len(latencies)*0.95)],
                'p99': latencies[int(len(latencies)*0.99)],
                'max': latencies[-1],
                'mean': sum(latencies) / len(latencies)
            }
    
    # Test different encoding methods
    methods = ["shq64", "t8q64", "zoq64"]
    
    for method in methods:
        print(f"\nTesting {method} encoding:")
        encoder = LowLatencyEncoder(encoding_method=method)
        
        # Warm up
        for _ in range(100):
            embedding = np.random.rand(384).astype(np.float32)
            await encoder.encode_ultra_low_latency(embedding)
        
        # Benchmark
        stats = await encoder.benchmark_latencies(num_samples=1000)
        
        print(f"  Latency statistics (microseconds):")
        print(f"    Min:  {stats['min']:.1f} μs")
        print(f"    P50:  {stats['p50']:.1f} μs")
        print(f"    P95:  {stats['p95']:.1f} μs")
        print(f"    P99:  {stats['p99']:.1f} μs")
        print(f"    Max:  {stats['max']:.1f} μs")
        print(f"    Mean: {stats['mean']:.1f} μs")
    print()


async def backpressure_handling_example():
    """
    Demonstrate backpressure handling in streaming systems.
    
    Shows how to handle varying load gracefully.
    """
    print("=== Backpressure Handling Example ===")
    
    class BackpressureAwareEncoder:
        def __init__(self, 
                     encoding_method: str = "shq64",
                     max_buffer_size: int = 100,
                     high_watermark: float = 0.8,
                     low_watermark: float = 0.2):
            self.encoder = AsyncStreamingEncoder(
                encoding_method=encoding_method,
                buffer_size=max_buffer_size
            )
            self.max_buffer_size = max_buffer_size
            self.high_watermark = high_watermark
            self.low_watermark = low_watermark
            self.is_accepting = True
            self.dropped_count = 0
        
        async def submit_with_backpressure(self, embedding: np.ndarray) -> bool:
            """Submit embedding with backpressure control."""
            buffer_usage = self.encoder.buffer.qsize() / self.max_buffer_size
            
            # Update acceptance state based on watermarks
            if buffer_usage >= self.high_watermark:
                self.is_accepting = False
            elif buffer_usage <= self.low_watermark:
                self.is_accepting = True
            
            # Handle based on state
            if self.is_accepting:
                success = await self.encoder.submit(embedding)
                if not success:
                    self.dropped_count += 1
                return success
            else:
                # Apply backpressure
                self.dropped_count += 1
                return False
        
        async def simulate_variable_load(self):
            """Simulate variable load patterns."""
            await self.encoder.start()
            
            # Load patterns: (duration_seconds, rate_per_second)
            load_patterns = [
                (2.0, 50),   # Normal load
                (2.0, 200),  # High load
                (2.0, 500),  # Overload
                (2.0, 50),   # Recovery
            ]
            
            print("Simulating variable load patterns...")
            total_submitted = 0
            
            for duration, rate in load_patterns:
                print(f"\n  Load: {rate} msg/s for {duration}s")
                start_time = time.time()
                pattern_submitted = 0
                pattern_accepted = 0
                
                while time.time() - start_time < duration:
                    # Generate embedding
                    embedding = np.random.rand(256).astype(np.float32)
                    
                    # Submit with backpressure
                    accepted = await self.submit_with_backpressure(embedding)
                    
                    pattern_submitted += 1
                    if accepted:
                        pattern_accepted += 1
                    
                    # Control rate
                    await asyncio.sleep(1.0 / rate)
                    
                    # Show status
                    if pattern_submitted % 50 == 0:
                        buffer_usage = self.encoder.buffer.qsize() / self.max_buffer_size
                        print(f"    Buffer: {buffer_usage:.0%}, "
                              f"Accepting: {self.is_accepting}, "
                              f"Dropped: {self.dropped_count}")
                
                acceptance_rate = pattern_accepted / pattern_submitted if pattern_submitted > 0 else 0
                print(f"    Submitted: {pattern_submitted}, "
                      f"Accepted: {pattern_accepted} ({acceptance_rate:.1%})")
                
                total_submitted += pattern_submitted
            
            await self.encoder.stop()
            
            print(f"\nFinal statistics:")
            print(f"  Total submitted: {total_submitted}")
            print(f"  Total dropped: {self.dropped_count}")
            print(f"  Total processed: {self.encoder.metrics.messages_processed}")
    
    # Create encoder with backpressure
    bp_encoder = BackpressureAwareEncoder(
        encoding_method="shq64",
        max_buffer_size=100,
        high_watermark=0.8,
        low_watermark=0.2
    )
    
    # Run simulation
    await bp_encoder.simulate_variable_load()
    print()


async def main():
    """Run all streaming examples."""
    print("UUBED Streaming Encoder Examples")
    print("=" * 50)
    
    # Run async examples
    await websocket_streaming_example()
    await kafka_streaming_example()
    await http_streaming_example()
    await low_latency_pipeline()
    await backpressure_handling_example()
    
    print("\nAll streaming examples completed!")


if __name__ == "__main__":
    # Run async examples
    asyncio.run(main())