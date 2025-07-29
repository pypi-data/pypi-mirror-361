#!/usr/bin/env python3
"""
Batch processing examples for uubed.

This module demonstrates efficient batch processing techniques for large datasets,
including:
- Memory-efficient chunked processing
- Parallel batch encoding
- Progress tracking and resumability
- Error handling and recovery
- Performance optimization strategies

Requirements:
    - uubed (core library)
    - numpy
    - tqdm (optional, for progress bars)
    - h5py (optional, for HDF5 support)
"""

import os
import time
import json
import numpy as np
from typing import Iterator, List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import partial
import tempfile
import pickle

from uubed import (
    encode, batch_encode, 
    validate_embedding_input, estimate_memory_usage,
    UubedError
)

# Optional imports
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Simple progress bar fallback
    def tqdm(iterable, total=None, desc=None):
        return iterable

try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False
    print("Note: Install h5py for HDF5 dataset support")


class BatchProcessor:
    """Base class for batch processing embeddings with uubed."""
    
    def __init__(self, 
                 encoding_method: str = "shq64",
                 batch_size: int = 1000,
                 num_workers: int = None,
                 checkpoint_dir: str = None):
        self.encoding_method = encoding_method
        self.batch_size = batch_size
        self.num_workers = num_workers or os.cpu_count()
        self.checkpoint_dir = checkpoint_dir or tempfile.mkdtemp()
        
        # Processing statistics
        self.stats = {
            "total_processed": 0,
            "total_errors": 0,
            "processing_time": 0,
            "checkpoints_saved": 0,
            "batches_processed": 0
        }
        
        # Ensure checkpoint directory exists
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self, batch_idx: int, state: Dict[str, Any]):
        """Save processing checkpoint for resumability."""
        checkpoint_path = Path(self.checkpoint_dir) / f"checkpoint_{batch_idx}.pkl"
        with open(checkpoint_path, 'wb') as f:
            pickle.dump({
                "batch_idx": batch_idx,
                "stats": self.stats,
                "state": state,
                "timestamp": time.time()
            }, f)
        self.stats["checkpoints_saved"] += 1
    
    def load_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Load the most recent checkpoint."""
        checkpoint_files = list(Path(self.checkpoint_dir).glob("checkpoint_*.pkl"))
        if not checkpoint_files:
            return None
        
        latest = max(checkpoint_files, key=lambda p: p.stat().st_mtime)
        with open(latest, 'rb') as f:
            return pickle.load(f)
    
    def process_batch(self, batch: np.ndarray) -> List[str]:
        """Process a single batch of embeddings."""
        try:
            # Validate batch
            for emb in batch:
                validate_embedding_input(emb, method=self.encoding_method)
            
            # Encode batch
            encoded = batch_encode(batch, method=self.encoding_method)
            return encoded
            
        except UubedError as e:
            print(f"Error processing batch: {e}")
            self.stats["total_errors"] += len(batch)
            return [""] * len(batch)  # Return empty strings for failed items


def chunked_file_processing():
    """
    Process large embedding files in memory-efficient chunks.
    
    Demonstrates loading and processing embeddings from various file formats.
    """
    print("=== Chunked File Processing ===")
    
    class ChunkedFileProcessor(BatchProcessor):
        def process_numpy_file(self, filepath: str, output_file: str):
            """Process large NumPy file in chunks."""
            print(f"Processing NumPy file: {filepath}")
            
            # Memory-map the file for efficient access
            mmap_array = np.memmap(filepath, dtype='float32', mode='r')
            total_embeddings = mmap_array.shape[0] // 768  # Assuming 768-dim embeddings
            mmap_array = mmap_array.reshape(total_embeddings, 768)
            
            results = []
            
            # Process in chunks
            for i in tqdm(range(0, total_embeddings, self.batch_size), 
                         desc="Processing chunks"):
                chunk = mmap_array[i:i+self.batch_size]
                
                # Convert to uint8
                chunk_uint8 = (chunk * 255).clip(0, 255).astype(np.uint8)
                
                # Process chunk
                encoded = self.process_batch(chunk_uint8)
                results.extend(encoded)
                
                # Save intermediate results
                if (i // self.batch_size) % 10 == 0:
                    self.save_checkpoint(i, {"results_so_far": len(results)})
            
            # Save results
            with open(output_file, 'w') as f:
                json.dump(results, f)
            
            print(f"Processed {total_embeddings} embeddings")
            return results
        
        def process_csv_chunks(self, filepath: str, embedding_cols: List[int]):
            """Process CSV file with embeddings in chunks."""
            import csv
            
            print(f"Processing CSV file: {filepath}")
            results = []
            batch = []
            
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header
                
                for row_idx, row in enumerate(tqdm(reader, desc="Processing rows")):
                    # Extract embedding values
                    embedding = np.array([float(row[i]) for i in embedding_cols])
                    embedding_uint8 = (embedding * 255).clip(0, 255).astype(np.uint8)
                    
                    batch.append(embedding_uint8)
                    
                    # Process batch when full
                    if len(batch) >= self.batch_size:
                        encoded = self.process_batch(np.array(batch))
                        results.extend(encoded)
                        batch = []
                        
                        # Checkpoint every 10 batches
                        if (row_idx // self.batch_size) % 10 == 0:
                            self.save_checkpoint(row_idx, {"rows_processed": row_idx})
                
                # Process remaining
                if batch:
                    encoded = self.process_batch(np.array(batch))
                    results.extend(encoded)
            
            return results
    
    # Create processor
    processor = ChunkedFileProcessor(
        encoding_method="shq64",
        batch_size=500
    )
    
    # Example 1: Process NumPy file
    print("\n1. NumPy file processing:")
    # Create sample file
    sample_embeddings = np.random.rand(5000, 768).astype(np.float32)
    temp_file = tempfile.NamedTemporaryFile(suffix='.npy', delete=False)
    sample_embeddings.tofile(temp_file.name)
    
    output_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    processor.process_numpy_file(temp_file.name, output_file.name)
    
    # Cleanup
    os.unlink(temp_file.name)
    os.unlink(output_file.name)
    
    print(f"Stats: {processor.stats}")
    print()


def parallel_batch_processing():
    """
    Demonstrate parallel processing strategies for maximum throughput.
    
    Compares different parallelization approaches.
    """
    print("=== Parallel Batch Processing ===")
    
    def encode_batch_wrapper(args):
        """Wrapper for parallel encoding."""
        batch, method = args
        try:
            return batch_encode(batch, method=method)
        except Exception as e:
            return [f"ERROR: {str(e)}"] * len(batch)
    
    class ParallelBatchProcessor(BatchProcessor):
        def process_parallel_threads(self, embeddings: np.ndarray) -> List[str]:
            """Process using thread pool (good for I/O bound tasks)."""
            print(f"Processing {len(embeddings)} embeddings with {self.num_workers} threads")
            
            results = []
            batches = [
                embeddings[i:i+self.batch_size]
                for i in range(0, len(embeddings), self.batch_size)
            ]
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                # Submit all batches
                futures = [
                    executor.submit(encode_batch_wrapper, (batch, self.encoding_method))
                    for batch in batches
                ]
                
                # Collect results with progress
                for future in tqdm(as_completed(futures), total=len(futures), 
                                 desc="Thread processing"):
                    result = future.result()
                    results.extend(result)
            
            elapsed = time.time() - start_time
            throughput = len(embeddings) / elapsed
            
            print(f"Thread pool completed in {elapsed:.2f}s ({throughput:.0f} emb/s)")
            return results
        
        def process_parallel_processes(self, embeddings: np.ndarray) -> List[str]:
            """Process using process pool (good for CPU bound tasks)."""
            print(f"Processing {len(embeddings)} embeddings with {self.num_workers} processes")
            
            results = []
            batches = [
                (embeddings[i:i+self.batch_size], self.encoding_method)
                for i in range(0, len(embeddings), self.batch_size)
            ]
            
            start_time = time.time()
            
            with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                # Map batches to workers
                batch_results = list(tqdm(
                    executor.map(encode_batch_wrapper, batches),
                    total=len(batches),
                    desc="Process pool"
                ))
                
                # Flatten results
                for batch_result in batch_results:
                    results.extend(batch_result)
            
            elapsed = time.time() - start_time
            throughput = len(embeddings) / elapsed
            
            print(f"Process pool completed in {elapsed:.2f}s ({throughput:.0f} emb/s)")
            return results
        
        def process_adaptive(self, embeddings: np.ndarray) -> List[str]:
            """Adaptively choose best parallelization strategy."""
            print("Analyzing workload for adaptive processing...")
            
            # Estimate computation complexity
            embedding_dim = embeddings.shape[1]
            is_cpu_bound = self.encoding_method in ["eq64", "zoq64"]
            
            # Choose strategy
            if is_cpu_bound and len(embeddings) > 1000:
                print("Selected: Process pool (CPU-bound workload)")
                return self.process_parallel_processes(embeddings)
            else:
                print("Selected: Thread pool (I/O-bound or small workload)")
                return self.process_parallel_threads(embeddings)
    
    # Create processor
    processor = ParallelBatchProcessor(
        encoding_method="t8q64",
        batch_size=250,
        num_workers=4
    )
    
    # Generate test data
    test_embeddings = np.random.rand(10000, 768).astype(np.float32)
    test_embeddings_uint8 = (test_embeddings * 255).astype(np.uint8)
    
    # Compare strategies
    print("\nComparing parallelization strategies:")
    
    # Sequential baseline
    print("\n1. Sequential processing:")
    start = time.time()
    sequential_results = []
    for i in range(0, len(test_embeddings_uint8), processor.batch_size):
        batch = test_embeddings_uint8[i:i+processor.batch_size]
        sequential_results.extend(batch_encode(batch, method=processor.encoding_method))
    sequential_time = time.time() - start
    print(f"Sequential: {sequential_time:.2f}s")
    
    # Thread pool
    print("\n2. Thread pool processing:")
    thread_results = processor.process_parallel_threads(test_embeddings_uint8)
    
    # Process pool
    print("\n3. Process pool processing:")
    process_results = processor.process_parallel_processes(test_embeddings_uint8)
    
    # Adaptive
    print("\n4. Adaptive processing:")
    adaptive_results = processor.process_adaptive(test_embeddings_uint8)
    
    print(f"\nSpeedup vs sequential:")
    print(f"  Thread pool: {sequential_time / processor.stats['processing_time']:.2f}x")
    print()


def streaming_batch_processor():
    """
    Process continuous streams of embeddings in batches.
    
    Useful for real-time systems and data pipelines.
    """
    print("=== Streaming Batch Processor ===")
    
    class StreamingBatchProcessor(BatchProcessor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.buffer = []
            self.last_flush_time = time.time()
            self.flush_interval = 5.0  # seconds
        
        def process_stream(self, 
                          embedding_generator: Iterator[np.ndarray],
                          output_callback: Callable[[List[str]], None],
                          max_items: int = None):
            """Process streaming embeddings with automatic batching."""
            print("Starting streaming processor...")
            
            items_processed = 0
            
            try:
                for embedding in embedding_generator:
                    # Add to buffer
                    self.buffer.append(embedding)
                    
                    # Check if we should process batch
                    should_process = (
                        len(self.buffer) >= self.batch_size or
                        (time.time() - self.last_flush_time) >= self.flush_interval
                    )
                    
                    if should_process:
                        self._flush_buffer(output_callback)
                    
                    items_processed += 1
                    if max_items and items_processed >= max_items:
                        break
                    
                    # Show progress
                    if items_processed % 1000 == 0:
                        print(f"  Processed {items_processed} items, "
                              f"buffer size: {len(self.buffer)}")
                
                # Final flush
                if self.buffer:
                    self._flush_buffer(output_callback)
                    
            except KeyboardInterrupt:
                print("\nStream interrupted, flushing buffer...")
                if self.buffer:
                    self._flush_buffer(output_callback)
            
            print(f"Stream processing complete. Total: {items_processed} items")
        
        def _flush_buffer(self, output_callback: Callable):
            """Process and flush the current buffer."""
            if not self.buffer:
                return
            
            batch = np.array(self.buffer)
            encoded = self.process_batch(batch)
            
            # Send to output
            output_callback(encoded)
            
            # Update stats
            self.stats["batches_processed"] += 1
            self.stats["total_processed"] += len(self.buffer)
            
            # Clear buffer
            self.buffer.clear()
            self.last_flush_time = time.time()
    
    # Example: Stream generator
    def embedding_stream_generator(rate_per_second: int = 100):
        """Simulate streaming embeddings."""
        while True:
            # Generate random embedding
            embedding = np.random.rand(384).astype(np.float32)
            embedding_uint8 = (embedding * 255).astype(np.uint8)
            yield embedding_uint8
            
            # Control rate
            time.sleep(1.0 / rate_per_second)
    
    # Output handler
    encoded_results = []
    def handle_output(batch_results: List[str]):
        encoded_results.extend(batch_results)
        print(f"  Received batch of {len(batch_results)} encoded embeddings")
    
    # Create processor
    processor = StreamingBatchProcessor(
        encoding_method="shq64",
        batch_size=50
    )
    
    # Process stream
    print("\nProcessing embedding stream (10 seconds)...")
    stream = embedding_stream_generator(rate_per_second=100)
    processor.process_stream(
        stream, 
        handle_output,
        max_items=1000  # Process 1000 items
    )
    
    print(f"\nStreaming stats: {processor.stats}")
    print()


def fault_tolerant_processing():
    """
    Demonstrate fault-tolerant batch processing with error recovery.
    
    Shows how to handle errors gracefully and ensure data integrity.
    """
    print("=== Fault-Tolerant Batch Processing ===")
    
    class FaultTolerantProcessor(BatchProcessor):
        def __init__(self, *args, max_retries: int = 3, **kwargs):
            super().__init__(*args, **kwargs)
            self.max_retries = max_retries
            self.error_log = []
        
        def process_with_recovery(self, 
                                 embeddings: np.ndarray,
                                 simulate_errors: bool = False) -> Dict[str, Any]:
            """Process embeddings with error recovery and detailed reporting."""
            print(f"Processing {len(embeddings)} embeddings with fault tolerance")
            
            results = []
            failed_indices = []
            retry_counts = {}
            
            # Process in batches
            for batch_idx in tqdm(range(0, len(embeddings), self.batch_size), 
                                desc="Processing batches"):
                batch = embeddings[batch_idx:batch_idx+self.batch_size]
                batch_success = False
                
                # Try processing with retries
                for retry in range(self.max_retries):
                    try:
                        # Simulate random errors
                        if simulate_errors and np.random.rand() < 0.1:
                            raise UubedError("Simulated encoding error")
                        
                        # Process batch
                        encoded = self.process_batch(batch)
                        results.extend(encoded)
                        batch_success = True
                        break
                        
                    except Exception as e:
                        error_info = {
                            "batch_idx": batch_idx,
                            "retry": retry,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        self.error_log.append(error_info)
                        
                        if retry < self.max_retries - 1:
                            print(f"\n  Retry {retry + 1}/{self.max_retries} for batch {batch_idx}")
                            time.sleep(0.5 * (retry + 1))  # Exponential backoff
                
                if not batch_success:
                    # Mark failed items
                    for i in range(len(batch)):
                        failed_indices.append(batch_idx + i)
                        results.append("")  # Placeholder
                
                # Save checkpoint periodically
                if batch_idx % (self.batch_size * 10) == 0:
                    self.save_checkpoint(batch_idx, {
                        "results_count": len(results),
                        "failed_count": len(failed_indices)
                    })
            
            # Generate report
            report = {
                "total_items": len(embeddings),
                "successful": len(embeddings) - len(failed_indices),
                "failed": len(failed_indices),
                "success_rate": (len(embeddings) - len(failed_indices)) / len(embeddings),
                "error_summary": self._summarize_errors(),
                "failed_indices": failed_indices[:100]  # First 100
            }
            
            return {
                "results": results,
                "report": report
            }
        
        def _summarize_errors(self) -> Dict[str, int]:
            """Summarize errors by type."""
            error_counts = {}
            for error in self.error_log:
                error_type = error["error"].split(":")[0]
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            return error_counts
        
        def recover_from_checkpoint(self, embeddings: np.ndarray) -> Dict[str, Any]:
            """Resume processing from last checkpoint."""
            checkpoint = self.load_latest_checkpoint()
            
            if not checkpoint:
                print("No checkpoint found, starting from beginning")
                return self.process_with_recovery(embeddings)
            
            print(f"Resuming from checkpoint: batch {checkpoint['batch_idx']}")
            
            # Skip already processed
            start_idx = checkpoint["batch_idx"]
            remaining = embeddings[start_idx:]
            
            # Process remaining
            return self.process_with_recovery(remaining)
    
    # Create processor
    processor = FaultTolerantProcessor(
        encoding_method="eq64",
        batch_size=100,
        max_retries=3
    )
    
    # Generate test data
    test_embeddings = np.random.rand(1000, 512).astype(np.float32)
    test_embeddings_uint8 = (test_embeddings * 255).astype(np.uint8)
    
    # Process with simulated errors
    print("\nProcessing with simulated errors:")
    result = processor.process_with_recovery(
        test_embeddings_uint8,
        simulate_errors=True
    )
    
    # Show report
    report = result["report"]
    print(f"\nProcessing Report:")
    print(f"  Total items: {report['total_items']}")
    print(f"  Successful: {report['successful']}")
    print(f"  Failed: {report['failed']}")
    print(f"  Success rate: {report['success_rate']:.1%}")
    print(f"  Error types: {report['error_summary']}")
    
    # Demonstrate checkpoint recovery
    print("\n\nDemonstrating checkpoint recovery:")
    processor2 = FaultTolerantProcessor(
        encoding_method="eq64",
        batch_size=100,
        checkpoint_dir=processor.checkpoint_dir
    )
    
    # Simulate interruption and recovery
    remaining_result = processor2.recover_from_checkpoint(test_embeddings_uint8)
    print()


def optimized_hdf5_processing():
    """
    Process embeddings stored in HDF5 format efficiently.
    
    HDF5 is commonly used for large scientific datasets.
    """
    if not H5PY_AVAILABLE:
        print("=== HDF5 Processing (Simulated) ===")
        print("h5py not available. Showing example structure.")
        return
    
    print("=== Optimized HDF5 Processing ===")
    
    class HDF5Processor(BatchProcessor):
        def process_hdf5_dataset(self, 
                                filepath: str,
                                dataset_name: str = "embeddings",
                                output_file: str = None) -> Dict[str, Any]:
            """Process embeddings from HDF5 file."""
            print(f"Processing HDF5 file: {filepath}")
            
            with h5py.File(filepath, 'r') as f:
                if dataset_name not in f:
                    raise ValueError(f"Dataset '{dataset_name}' not found")
                
                dataset = f[dataset_name]
                total_embeddings = dataset.shape[0]
                embedding_dim = dataset.shape[1]
                
                print(f"Dataset shape: {dataset.shape}")
                print(f"Dataset dtype: {dataset.dtype}")
                
                # Estimate memory usage
                memory_estimate = estimate_memory_usage(
                    num_embeddings=self.batch_size,
                    embedding_dim=embedding_dim,
                    method=self.encoding_method
                )
                print(f"Estimated memory per batch: {memory_estimate / 1024 / 1024:.2f} MB")
                
                # Process in chunks
                results = []
                
                for i in tqdm(range(0, total_embeddings, self.batch_size),
                            desc="Processing HDF5 chunks"):
                    # Load chunk
                    chunk = dataset[i:i+self.batch_size]
                    
                    # Convert to uint8
                    if chunk.dtype != np.uint8:
                        chunk = (chunk * 255).clip(0, 255).astype(np.uint8)
                    
                    # Process
                    encoded = self.process_batch(chunk)
                    results.extend(encoded)
                
                # Save results
                if output_file:
                    if output_file.endswith('.h5'):
                        # Save as HDF5
                        with h5py.File(output_file, 'w') as out_f:
                            # Convert strings to fixed-length for HDF5
                            max_len = max(len(s) for s in results)
                            dt = h5py.special_dtype(vlen=str)
                            
                            out_f.create_dataset(
                                'encoded_embeddings',
                                data=results,
                                dtype=dt
                            )
                            
                            # Add metadata
                            out_f.attrs['encoding_method'] = self.encoding_method
                            out_f.attrs['source_file'] = filepath
                            out_f.attrs['processing_stats'] = json.dumps(self.stats)
                    else:
                        # Save as JSON
                        with open(output_file, 'w') as f:
                            json.dump({
                                'encoded_embeddings': results,
                                'metadata': {
                                    'encoding_method': self.encoding_method,
                                    'source_file': filepath,
                                    'stats': self.stats
                                }
                            }, f)
                
                return {
                    'total_processed': total_embeddings,
                    'output_file': output_file,
                    'stats': self.stats
                }
    
    # Create sample HDF5 file
    sample_file = tempfile.NamedTemporaryFile(suffix='.h5', delete=False)
    with h5py.File(sample_file.name, 'w') as f:
        # Create dataset
        embeddings = np.random.rand(5000, 768).astype(np.float32)
        f.create_dataset('embeddings', data=embeddings, chunks=(100, 768))
        
        # Add metadata
        f.attrs['created_by'] = 'uubed_example'
        f.attrs['description'] = 'Sample embeddings for testing'
    
    # Process file
    processor = HDF5Processor(
        encoding_method="shq64",
        batch_size=500
    )
    
    output_file = tempfile.NamedTemporaryFile(suffix='.h5', delete=False)
    result = processor.process_hdf5_dataset(
        sample_file.name,
        dataset_name='embeddings',
        output_file=output_file.name
    )
    
    print(f"\nProcessing complete:")
    print(f"  Total processed: {result['total_processed']}")
    print(f"  Output file: {result['output_file']}")
    print(f"  Stats: {result['stats']}")
    
    # Verify output
    with h5py.File(output_file.name, 'r') as f:
        print(f"\nOutput file contents:")
        print(f"  Dataset: {list(f.keys())}")
        print(f"  Attributes: {dict(f.attrs)}")
    
    # Cleanup
    os.unlink(sample_file.name)
    os.unlink(output_file.name)
    print()


if __name__ == "__main__":
    print("UUBED Batch Processing Examples")
    print("=" * 50)
    
    # Run examples
    chunked_file_processing()
    parallel_batch_processing()
    streaming_batch_processor()
    fault_tolerant_processing()
    optimized_hdf5_processing()
    
    print("\nAll batch processing examples completed!")