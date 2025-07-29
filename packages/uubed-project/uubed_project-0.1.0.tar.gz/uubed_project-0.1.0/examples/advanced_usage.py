#!/usr/bin/env python3
"""
Advanced usage examples for uubed encoding library.

This module demonstrates advanced encoding techniques and performance optimization
strategies, including:
- Custom encoding configurations
- Memory-efficient processing
- Parallel encoding
- Advanced parameter tuning
- Performance profiling

Requirements:
    - uubed (core library)
    - numpy
    - concurrent.futures (standard library)
    - psutil (optional, for memory monitoring)
"""

import time
import numpy as np
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Note: Install psutil for memory monitoring features")

from uubed import (
    encode, decode, batch_encode,
    validate_embedding_input, estimate_memory_usage,
    get_config, set_setting,
    UubedError, UubedValidationError
)


def advanced_configuration_example():
    """
    Demonstrate advanced configuration options for optimal performance.
    
    Shows how to tune the encoder for specific use cases and hardware.
    """
    print("=== Advanced Configuration Example ===")
    
    # Get current configuration
    config = get_config()
    print(f"Current configuration: {config}")
    
    # Optimize for batch processing
    set_setting("batch_size", 1000)
    set_setting("num_threads", mp.cpu_count())
    set_setting("memory_limit_mb", 4096)
    
    # Create test data
    embeddings = np.random.rand(1000, 1536).astype(np.float32)
    embeddings_uint8 = (embeddings * 255).astype(np.uint8)
    
    # Encode with optimized settings
    start = time.time()
    encoded = batch_encode(embeddings_uint8, method="shq64")
    elapsed = time.time() - start
    
    print(f"Encoded {len(embeddings)} embeddings in {elapsed:.3f}s")
    print(f"Throughput: {len(embeddings)/elapsed:.1f} embeddings/sec")
    print()


def memory_efficient_processing():
    """
    Demonstrate memory-efficient processing of large datasets.
    
    Shows techniques for processing data that doesn't fit in memory.
    """
    print("=== Memory-Efficient Processing ===")
    
    # Estimate memory usage
    embedding_dim = 1536
    num_embeddings = 10000
    memory_estimate = estimate_memory_usage(
        num_embeddings=num_embeddings,
        embedding_dim=embedding_dim,
        method="eq64"
    )
    
    print(f"Estimated memory usage: {memory_estimate / 1024 / 1024:.2f} MB")
    
    # Process in chunks to manage memory
    chunk_size = 1000
    total_processed = 0
    
    if PSUTIL_AVAILABLE:
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
    
    for chunk_idx in range(0, num_embeddings, chunk_size):
        # Generate chunk (in real scenario, this would be loaded from disk)
        chunk = np.random.rand(
            min(chunk_size, num_embeddings - chunk_idx), 
            embedding_dim
        ).astype(np.float32)
        chunk_uint8 = (chunk * 255).astype(np.uint8)
        
        # Process chunk
        encoded_chunk = batch_encode(chunk_uint8, method="shq64")
        total_processed += len(encoded_chunk)
        
        # Clear chunk from memory
        del chunk, chunk_uint8
    
    if PSUTIL_AVAILABLE:
        final_memory = process.memory_info().rss / 1024 / 1024
        print(f"Memory usage: {initial_memory:.1f} MB -> {final_memory:.1f} MB")
    
    print(f"Processed {total_processed} embeddings in chunks")
    print()


def parallel_encoding_example():
    """
    Demonstrate parallel encoding for maximum throughput.
    
    Compares thread-based vs process-based parallelization.
    """
    print("=== Parallel Encoding Example ===")
    
    # Create test data
    num_embeddings = 5000
    embeddings = np.random.rand(num_embeddings, 768).astype(np.float32)
    embeddings_uint8 = (embeddings * 255).astype(np.uint8)
    
    # Single-threaded baseline
    start = time.time()
    baseline = [encode(emb, method="t8q64") for emb in embeddings_uint8]
    baseline_time = time.time() - start
    print(f"Single-threaded: {baseline_time:.3f}s")
    
    # Thread-based parallelization
    def encode_wrapper(emb):
        return encode(emb, method="t8q64")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        start = time.time()
        threaded = list(executor.map(encode_wrapper, embeddings_uint8))
        threaded_time = time.time() - start
    print(f"Thread pool (4 workers): {threaded_time:.3f}s ({baseline_time/threaded_time:.2f}x speedup)")
    
    # Process-based parallelization (for CPU-bound tasks)
    with ProcessPoolExecutor(max_workers=4) as executor:
        start = time.time()
        process_based = list(executor.map(encode_wrapper, embeddings_uint8))
        process_time = time.time() - start
    print(f"Process pool (4 workers): {process_time:.3f}s ({baseline_time/process_time:.2f}x speedup)")
    print()


def custom_encoding_pipeline():
    """
    Build a custom encoding pipeline with pre/post-processing.
    
    Shows how to integrate uubed into a larger ML pipeline.
    """
    print("=== Custom Encoding Pipeline ===")
    
    class EncodingPipeline:
        def __init__(self, method: str = "auto", normalize: bool = True):
            self.method = method
            self.normalize = normalize
            self.stats = {"processed": 0, "errors": 0}
        
        def preprocess(self, embedding: np.ndarray) -> np.ndarray:
            """Normalize and validate embedding."""
            if self.normalize:
                # L2 normalization
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
            
            # Scale to uint8 range
            embedding = np.clip(embedding, 0, 1)
            return (embedding * 255).astype(np.uint8)
        
        def encode_with_metadata(self, embedding: np.ndarray, 
                                metadata: Dict) -> Dict:
            """Encode embedding with associated metadata."""
            try:
                # Validate input
                validate_embedding_input(embedding, method=self.method)
                
                # Preprocess
                processed = self.preprocess(embedding)
                
                # Encode
                encoded = encode(processed, method=self.method)
                
                # Package result
                result = {
                    "encoded": encoded,
                    "method": self.method,
                    "timestamp": time.time(),
                    "metadata": metadata,
                    "dimension": len(embedding)
                }
                
                self.stats["processed"] += 1
                return result
                
            except (UubedError, UubedValidationError) as e:
                self.stats["errors"] += 1
                return {"error": str(e), "metadata": metadata}
        
        def get_stats(self) -> Dict:
            """Get processing statistics."""
            return self.stats.copy()
    
    # Use the pipeline
    pipeline = EncodingPipeline(method="shq64", normalize=True)
    
    # Process embeddings with metadata
    embeddings = [
        (np.random.rand(384).astype(np.float32), {"doc_id": f"doc_{i}", "type": "text"})
        for i in range(10)
    ]
    
    results = []
    for emb, meta in embeddings:
        result = pipeline.encode_with_metadata(emb, meta)
        results.append(result)
    
    # Show results
    print(f"Pipeline stats: {pipeline.get_stats()}")
    print(f"Sample result: {results[0]}")
    print()


def adaptive_method_selection():
    """
    Demonstrate adaptive encoding method selection based on data characteristics.
    
    Shows how to choose the optimal encoding method dynamically.
    """
    print("=== Adaptive Method Selection ===")
    
    def analyze_embedding(embedding: np.ndarray) -> Dict:
        """Analyze embedding characteristics."""
        return {
            "dimension": len(embedding),
            "sparsity": np.sum(embedding == 0) / len(embedding),
            "entropy": -np.sum(embedding * np.log2(embedding + 1e-10)),
            "variance": np.var(embedding),
            "max_value": np.max(embedding),
            "mean_value": np.mean(embedding)
        }
    
    def select_optimal_method(characteristics: Dict) -> str:
        """Select encoding method based on embedding characteristics."""
        dim = characteristics["dimension"]
        sparsity = characteristics["sparsity"]
        
        if dim >= 1536:
            # Large embeddings: use compression
            if sparsity > 0.5:
                return "t8q64"  # Top-k for sparse data
            else:
                return "shq64"  # SimHash for dense data
        elif dim <= 512:
            # Small embeddings: preserve precision
            return "eq64"
        else:
            # Medium embeddings: use Z-order for spatial properties
            return "zoq64"
    
    # Test with different embedding types
    test_cases = [
        ("Large dense", np.random.rand(2048).astype(np.float32)),
        ("Large sparse", np.random.rand(2048).astype(np.float32) * (np.random.rand(2048) > 0.7)),
        ("Small dense", np.random.rand(256).astype(np.float32)),
        ("Medium spatial", np.random.rand(768).astype(np.float32))
    ]
    
    for name, embedding in test_cases:
        # Normalize to [0, 1]
        embedding = (embedding - embedding.min()) / (embedding.max() - embedding.min() + 1e-10)
        characteristics = analyze_embedding(embedding)
        selected_method = select_optimal_method(characteristics)
        
        # Encode with selected method
        embedding_uint8 = (embedding * 255).astype(np.uint8)
        encoded = encode(embedding_uint8, method=selected_method)
        
        print(f"{name:15} -> {selected_method:6} (dim={len(embedding)}, "
              f"sparsity={characteristics['sparsity']:.2f}, len={len(encoded)})")
    print()


def performance_profiling_example():
    """
    Profile encoding performance across different configurations.
    
    Helps identify bottlenecks and optimization opportunities.
    """
    print("=== Performance Profiling ===")
    
    import cProfile
    import pstats
    from io import StringIO
    
    def profile_encoding_batch(size: int, dim: int, method: str):
        """Profile batch encoding operation."""
        embeddings = np.random.rand(size, dim).astype(np.float32)
        embeddings_uint8 = (embeddings * 255).astype(np.uint8)
        
        # Profile the encoding
        profiler = cProfile.Profile()
        profiler.enable()
        
        encoded = batch_encode(embeddings_uint8, method=method)
        
        profiler.disable()
        
        # Get stats
        s = StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 functions
        
        return len(encoded), s.getvalue()
    
    # Profile different configurations
    configs = [
        (100, 384, "shq64"),
        (1000, 768, "t8q64"),
        (10, 1536, "eq64")
    ]
    
    for size, dim, method in configs:
        count, profile_output = profile_encoding_batch(size, dim, method)
        print(f"\nProfile for {size} embeddings of dim {dim} with {method}:")
        print(f"Encoded {count} items")
        # Show only key statistics
        lines = profile_output.split('\n')
        for line in lines[4:8]:  # Show top few functions
            if line.strip():
                print(f"  {line}")
    print()


def error_recovery_patterns():
    """
    Demonstrate robust error handling and recovery patterns.
    
    Shows how to handle various error conditions gracefully.
    """
    print("=== Error Recovery Patterns ===")
    
    def safe_encode_with_fallback(embedding: np.ndarray, 
                                  preferred_method: str = "auto",
                                  fallback_methods: List[str] = None) -> Optional[str]:
        """Encode with automatic fallback on errors."""
        if fallback_methods is None:
            fallback_methods = ["eq64", "shq64", "t8q64", "zoq64"]
        
        methods_to_try = [preferred_method] + fallback_methods
        last_error = None
        
        for method in methods_to_try:
            try:
                # Validate before encoding
                validate_embedding_input(embedding, method=method)
                return encode(embedding, method=method)
            except UubedValidationError as e:
                last_error = e
                print(f"  Validation failed for {method}: {e}")
                continue
            except UubedError as e:
                last_error = e
                print(f"  Encoding failed for {method}: {e}")
                continue
        
        print(f"  All methods failed. Last error: {last_error}")
        return None
    
    # Test with various problematic inputs
    test_cases = [
        ("Valid embedding", np.random.randint(0, 256, 384, dtype=np.uint8)),
        ("Wrong dtype", np.random.rand(384).astype(np.float64)),
        ("Wrong shape", np.random.randint(0, 256, (10, 10), dtype=np.uint8)),
        ("Empty array", np.array([], dtype=np.uint8))
    ]
    
    for name, data in test_cases:
        print(f"\nTesting: {name}")
        result = safe_encode_with_fallback(data, preferred_method="auto")
        if result:
            print(f"  Success! Encoded length: {len(result)}")
    print()


if __name__ == "__main__":
    print("UUBED Advanced Usage Examples")
    print("=" * 50)
    
    # Run all examples
    advanced_configuration_example()
    memory_efficient_processing()
    parallel_encoding_example()
    custom_encoding_pipeline()
    adaptive_method_selection()
    performance_profiling_example()
    error_recovery_patterns()
    
    print("\nAll advanced examples completed!")