#!/usr/bin/env python3
"""
Benchmarking examples for uubed.

This module demonstrates comprehensive benchmarking of uubed encoding methods,
including:
- Performance comparison across methods
- Memory usage profiling
- Scalability testing
- Hardware-specific optimization
- Comparative analysis with other encoding libraries

Requirements:
    - uubed (core library)
    - numpy
    - matplotlib (optional, for visualization)
    - psutil (optional, for system monitoring)
    - memory_profiler (optional, for detailed memory analysis)
"""

import time
import gc
import json
import numpy as np
from typing import List, Dict, Any, Tuple, Callable
from dataclasses import dataclass, asdict
import statistics
import platform
import multiprocessing as mp
from pathlib import Path

from uubed import (
    encode, decode, batch_encode,
    estimate_memory_usage,
    UubedError
)

# Optional imports
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Note: Install matplotlib for visualization")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Note: Install psutil for system monitoring")

try:
    from memory_profiler import memory_usage
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False
    print("Note: Install memory_profiler for detailed memory analysis")


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    method: str
    dimension: int
    num_samples: int
    encoding_time_ms: float
    decoding_time_ms: float
    throughput_per_sec: float
    memory_usage_mb: float
    compression_ratio: float
    encoded_size_bytes: int
    cpu_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BenchmarkSuite:
    """Comprehensive benchmarking suite for uubed."""
    
    def __init__(self, output_dir: str = "./benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Collect system information."""
        info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": mp.cpu_count(),
        }
        
        if PSUTIL_AVAILABLE:
            info.update({
                "total_memory_gb": psutil.virtual_memory().total / (1024**3),
                "available_memory_gb": psutil.virtual_memory().available / (1024**3),
            })
        
        return info
    
    def benchmark_single_method(self,
                              method: str,
                              embeddings: np.ndarray,
                              warmup_runs: int = 10) -> BenchmarkResult:
        """Benchmark a single encoding method."""
        print(f"Benchmarking {method}...")
        
        # Warmup
        for _ in range(warmup_runs):
            encode(embeddings[0], method=method)
        
        # Memory tracking
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / (1024**2)
            initial_cpu = process.cpu_percent()
        else:
            initial_memory = 0
            initial_cpu = 0
        
        # Encoding benchmark
        gc.collect()
        encoding_times = []
        encoded_samples = []
        
        for emb in embeddings:
            start = time.perf_counter()
            encoded = encode(emb, method=method)
            encoding_times.append(time.perf_counter() - start)
            encoded_samples.append(encoded)
        
        # Decoding benchmark (only for eq64)
        decoding_times = []
        if method == "eq64":
            for encoded in encoded_samples[:100]:  # Test subset
                start = time.perf_counter()
                decoded = decode(encoded)
                decoding_times.append(time.perf_counter() - start)
        
        # Calculate metrics
        avg_encoding_time = statistics.mean(encoding_times) * 1000  # ms
        avg_decoding_time = statistics.mean(decoding_times) * 1000 if decoding_times else 0
        throughput = len(embeddings) / sum(encoding_times)
        
        # Memory and compression metrics
        if PSUTIL_AVAILABLE:
            final_memory = process.memory_info().rss / (1024**2)
            final_cpu = process.cpu_percent()
            memory_used = final_memory - initial_memory
            cpu_used = final_cpu - initial_cpu
        else:
            memory_used = 0
            cpu_used = 0
        
        # Compression ratio
        original_size = embeddings[0].nbytes
        encoded_size = statistics.mean([len(e) for e in encoded_samples])
        compression_ratio = original_size / encoded_size
        
        return BenchmarkResult(
            method=method,
            dimension=len(embeddings[0]),
            num_samples=len(embeddings),
            encoding_time_ms=avg_encoding_time,
            decoding_time_ms=avg_decoding_time,
            throughput_per_sec=throughput,
            memory_usage_mb=memory_used,
            compression_ratio=compression_ratio,
            encoded_size_bytes=int(encoded_size),
            cpu_percent=cpu_used
        )


def performance_comparison():
    """
    Compare performance across all encoding methods.
    
    Tests different dimensions and batch sizes.
    """
    print("=== Performance Comparison ===")
    
    suite = BenchmarkSuite()
    
    # Test configurations
    dimensions = [128, 384, 768, 1536]
    num_samples = 1000
    methods = ["eq64", "shq64", "t8q64", "zoq64"]
    
    # Run benchmarks
    all_results = []
    
    for dim in dimensions:
        print(f"\nTesting dimension: {dim}")
        
        # Generate test data
        embeddings = np.random.rand(num_samples, dim).astype(np.float32)
        embeddings_uint8 = (embeddings * 255).astype(np.uint8)
        
        # Benchmark each method
        for method in methods:
            try:
                result = suite.benchmark_single_method(method, embeddings_uint8)
                all_results.append(result)
                suite.results.append(result)
                
                print(f"  {method}: {result.throughput_per_sec:.0f} emb/s, "
                      f"compression: {result.compression_ratio:.2f}x")
                      
            except UubedError as e:
                print(f"  {method}: Error - {e}")
    
    # Generate summary table
    print("\n" + "="*80)
    print("Performance Summary")
    print("="*80)
    print(f"{'Method':>8} {'Dim':>6} {'Throughput':>12} {'Encode(ms)':>12} "
          f"{'Compress':>10} {'Size(B)':>10}")
    print("-"*80)
    
    for r in all_results:
        print(f"{r.method:>8} {r.dimension:>6} {r.throughput_per_sec:>11.0f}/s "
              f"{r.encoding_time_ms:>11.3f} {r.compression_ratio:>9.2f}x "
              f"{r.encoded_size_bytes:>10}")
    
    # Save results
    results_file = suite.output_dir / "performance_comparison.json"
    with open(results_file, 'w') as f:
        json.dump({
            'system_info': suite.system_info,
            'results': [r.to_dict() for r in all_results]
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    # Visualize if matplotlib available
    if MATPLOTLIB_AVAILABLE:
        visualize_performance_comparison(all_results, suite.output_dir)
    
    print()


def memory_usage_profiling():
    """
    Profile memory usage patterns for different workloads.
    
    Analyzes memory efficiency and identifies optimization opportunities.
    """
    print("=== Memory Usage Profiling ===")
    
    if not MEMORY_PROFILER_AVAILABLE and not PSUTIL_AVAILABLE:
        print("Memory profiling libraries not available.")
        return
    
    def memory_test_encode(method: str, num_embeddings: int, dim: int):
        """Function to profile for memory usage."""
        embeddings = np.random.rand(num_embeddings, dim).astype(np.float32)
        embeddings_uint8 = (embeddings * 255).astype(np.uint8)
        
        encoded = batch_encode(embeddings_uint8, method=method)
        return len(encoded)
    
    # Test configurations
    test_cases = [
        ("Small batch", 100, 384),
        ("Medium batch", 1000, 768),
        ("Large batch", 5000, 1536),
    ]
    
    methods = ["eq64", "shq64", "t8q64", "zoq64"]
    
    print("\nMemory usage by workload:")
    print(f"{'Workload':>15} {'Method':>8} {'Peak MB':>10} {'Estimated MB':>13}")
    print("-"*50)
    
    for name, num_emb, dim in test_cases:
        for method in methods:
            # Estimate memory usage
            estimated = estimate_memory_usage(
                num_embeddings=num_emb,
                embedding_dim=dim,
                method=method
            ) / (1024**2)
            
            if MEMORY_PROFILER_AVAILABLE:
                # Measure actual memory usage
                mem_usage = memory_usage(
                    (memory_test_encode, (method, num_emb, dim)),
                    interval=0.1,
                    timeout=30
                )
                peak_memory = max(mem_usage) - min(mem_usage)
            else:
                # Fallback to basic measurement
                gc.collect()
                if PSUTIL_AVAILABLE:
                    process = psutil.Process()
                    before = process.memory_info().rss / (1024**2)
                    memory_test_encode(method, num_emb, dim)
                    after = process.memory_info().rss / (1024**2)
                    peak_memory = after - before
                else:
                    peak_memory = 0
            
            print(f"{name:>15} {method:>8} {peak_memory:>9.1f} {estimated:>12.1f}")
    
    print()


def scalability_testing():
    """
    Test scalability with increasing data sizes.
    
    Identifies performance bottlenecks and scaling characteristics.
    """
    print("=== Scalability Testing ===")
    
    suite = BenchmarkSuite()
    
    # Test with increasing batch sizes
    base_dim = 768
    batch_sizes = [10, 50, 100, 500, 1000, 5000, 10000]
    method = "shq64"  # Use consistent method
    
    print(f"Testing scalability with {method} encoding (dim={base_dim}):")
    
    results = []
    
    for batch_size in batch_sizes:
        print(f"\n  Batch size: {batch_size}")
        
        # Generate data
        embeddings = np.random.rand(batch_size, base_dim).astype(np.float32)
        embeddings_uint8 = (embeddings * 255).astype(np.uint8)
        
        # Time batch encoding
        gc.collect()
        start = time.time()
        encoded = batch_encode(embeddings_uint8, method=method)
        elapsed = time.time() - start
        
        # Calculate metrics
        throughput = batch_size / elapsed
        time_per_item = elapsed / batch_size * 1000  # ms
        
        results.append({
            'batch_size': batch_size,
            'total_time': elapsed,
            'throughput': throughput,
            'time_per_item_ms': time_per_item,
            'scaling_efficiency': throughput / (batch_size / batch_sizes[0])
        })
        
        print(f"    Time: {elapsed:.3f}s, Throughput: {throughput:.0f} emb/s")
        print(f"    Per-item: {time_per_item:.3f}ms")
    
    # Analyze scaling
    print("\n" + "="*60)
    print("Scalability Analysis")
    print("="*60)
    print(f"{'Batch':>8} {'Time(s)':>10} {'Throughput':>12} {'Per-item(ms)':>13}")
    print("-"*60)
    
    for r in results:
        print(f"{r['batch_size']:>8} {r['total_time']:>10.3f} "
              f"{r['throughput']:>11.0f}/s {r['time_per_item_ms']:>13.3f}")
    
    # Check if performance scales linearly
    first_efficiency = results[0]['time_per_item_ms']
    last_efficiency = results[-1]['time_per_item_ms']
    scaling_quality = first_efficiency / last_efficiency
    
    print(f"\nScaling quality: {scaling_quality:.2f}x")
    print("(1.0 = perfect linear scaling)")
    
    print()


def hardware_optimization_benchmark():
    """
    Benchmark hardware-specific optimizations.
    
    Tests SIMD, cache efficiency, and parallelization.
    """
    print("=== Hardware Optimization Benchmark ===")
    
    # Test different memory layouts
    def test_memory_layout(layout: str, size: int = 10000, dim: int = 768):
        """Test encoding performance with different memory layouts."""
        if layout == "contiguous":
            data = np.random.rand(size, dim).astype(np.float32)
        elif layout == "fortran":
            data = np.asfortranarray(np.random.rand(size, dim).astype(np.float32))
        elif layout == "strided":
            # Create strided array by slicing
            temp = np.random.rand(size * 2, dim * 2).astype(np.float32)
            data = temp[::2, ::2]
        else:
            raise ValueError(f"Unknown layout: {layout}")
        
        data_uint8 = (data * 255).astype(np.uint8)
        
        # Benchmark
        start = time.perf_counter()
        encoded = batch_encode(data_uint8, method="shq64")
        elapsed = time.perf_counter() - start
        
        return elapsed, len(encoded)
    
    print("Memory layout performance:")
    layouts = ["contiguous", "fortran", "strided"]
    
    for layout in layouts:
        elapsed, count = test_memory_layout(layout)
        throughput = count / elapsed
        print(f"  {layout:>12}: {elapsed:.3f}s ({throughput:.0f} emb/s)")
    
    # Test cache-friendly access patterns
    print("\nCache efficiency test:")
    
    def test_cache_pattern(pattern: str, num_items: int = 5000):
        """Test different access patterns."""
        embeddings = np.random.rand(num_items, 1536).astype(np.float32)
        embeddings_uint8 = (embeddings * 255).astype(np.uint8)
        
        if pattern == "sequential":
            # Process in order
            indices = list(range(num_items))
        elif pattern == "random":
            # Random access
            indices = np.random.permutation(num_items).tolist()
        elif pattern == "blocked":
            # Block-wise access (cache-friendly)
            block_size = 64
            indices = []
            for i in range(0, num_items, block_size):
                indices.extend(range(i, min(i + block_size, num_items)))
        
        # Time encoding with access pattern
        start = time.perf_counter()
        results = []
        for idx in indices:
            encoded = encode(embeddings_uint8[idx], method="t8q64")
            results.append(encoded)
        elapsed = time.perf_counter() - start
        
        return elapsed, len(results)
    
    patterns = ["sequential", "random", "blocked"]
    
    for pattern in patterns:
        elapsed, count = test_cache_pattern(pattern)
        throughput = count / elapsed
        print(f"  {pattern:>12}: {elapsed:.3f}s ({throughput:.0f} emb/s)")
    
    # Test parallel efficiency
    print("\nParallel processing efficiency:")
    
    def parallel_encode_test(num_workers: int):
        """Test parallel encoding efficiency."""
        from concurrent.futures import ProcessPoolExecutor
        
        embeddings = np.random.rand(10000, 768).astype(np.float32)
        embeddings_uint8 = (embeddings * 255).astype(np.uint8)
        
        # Split work
        chunk_size = len(embeddings_uint8) // num_workers
        chunks = [
            embeddings_uint8[i:i+chunk_size]
            for i in range(0, len(embeddings_uint8), chunk_size)
        ]
        
        # Time parallel encoding
        start = time.time()
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(batch_encode, chunk, method="shq64")
                for chunk in chunks
            ]
            results = [f.result() for f in futures]
        
        elapsed = time.time() - start
        
        # Flatten results
        all_encoded = []
        for batch in results:
            all_encoded.extend(batch)
        
        return elapsed, len(all_encoded)
    
    worker_counts = [1, 2, 4, mp.cpu_count()]
    baseline_time = None
    
    for workers in worker_counts:
        elapsed, count = parallel_encode_test(workers)
        throughput = count / elapsed
        
        if baseline_time is None:
            baseline_time = elapsed
            speedup = 1.0
        else:
            speedup = baseline_time / elapsed
        
        print(f"  {workers} workers: {elapsed:.3f}s "
              f"({throughput:.0f} emb/s, {speedup:.2f}x speedup)")
    
    print()


def comparative_analysis():
    """
    Compare uubed with alternative encoding approaches.
    
    Shows advantages and trade-offs.
    """
    print("=== Comparative Analysis ===")
    
    # Simulate alternative encoding methods
    def base64_encode(data: np.ndarray) -> str:
        """Standard base64 encoding."""
        import base64
        return base64.b64encode(data.tobytes()).decode('ascii')
    
    def hex_encode(data: np.ndarray) -> str:
        """Hexadecimal encoding."""
        return data.tobytes().hex()
    
    def custom_ascii_encode(data: np.ndarray) -> str:
        """Simple ASCII encoding (for comparison)."""
        # Map to printable ASCII range
        ascii_data = (data / 4) + 32  # Map 0-255 to 32-95
        return ''.join(chr(int(x)) for x in ascii_data)
    
    # Test data
    dimensions = [384, 768, 1536]
    num_samples = 100
    
    print("Comparison with alternative encodings:")
    print(f"{'Method':>15} {'Dim':>6} {'Size(B)':>10} {'Time(ms)':>10} "
          f"{'Unique':>8} {'Density':>10}")
    print("-"*70)
    
    for dim in dimensions:
        # Generate test embedding
        embedding = np.random.rand(dim).astype(np.float32)
        embedding_uint8 = (embedding * 255).astype(np.uint8)
        
        # Test each encoding method
        methods = [
            ("uubed-eq64", lambda d: encode(d, method="eq64")),
            ("uubed-shq64", lambda d: encode(d, method="shq64")),
            ("base64", base64_encode),
            ("hex", hex_encode),
            ("ascii", custom_ascii_encode),
        ]
        
        for name, encoder in methods:
            # Time encoding
            start = time.perf_counter()
            encoded = encoder(embedding_uint8)
            elapsed = (time.perf_counter() - start) * 1000
            
            # Analyze encoding properties
            unique_chars = len(set(encoded))
            density = dim / len(encoded) if len(encoded) > 0 else 0
            
            print(f"{name:>15} {dim:>6} {len(encoded):>10} "
                  f"{elapsed:>9.3f} {unique_chars:>8} {density:>10.3f}")
    
    # Special properties comparison
    print("\n\nSpecial Properties Comparison:")
    print(f"{'Property':>30} {'UUBED':>10} {'Base64':>10} {'Hex':>10}")
    print("-"*60)
    
    properties = [
        ("Position-dependent encoding", "Yes", "No", "No"),
        ("Substring-safe", "Yes", "No", "No"),
        ("Fixed output size", "Varies", "No", "Yes"),
        ("Compression", "Yes*", "No", "No"),
        ("Reversible", "Yes**", "Yes", "Yes"),
    ]
    
    for prop, uubed, base64, hex_val in properties:
        print(f"{prop:>30} {uubed:>10} {base64:>10} {hex_val:>10}")
    
    print("\n* Compression varies by method (shq64, t8q64, zoq64)")
    print("** Only eq64 is fully reversible")
    print()


def visualize_performance_comparison(results: List[BenchmarkResult], 
                                   output_dir: Path):
    """Visualize benchmark results."""
    if not MATPLOTLIB_AVAILABLE:
        return
    
    # Group results by dimension
    dims = sorted(set(r.dimension for r in results))
    methods = sorted(set(r.method for r in results))
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('UUBED Performance Comparison', fontsize=16)
    
    # 1. Throughput comparison
    ax1 = axes[0, 0]
    for method in methods:
        method_results = [r for r in results if r.method == method]
        x = [r.dimension for r in method_results]
        y = [r.throughput_per_sec for r in method_results]
        ax1.plot(x, y, marker='o', label=method)
    
    ax1.set_xlabel('Embedding Dimension')
    ax1.set_ylabel('Throughput (embeddings/sec)')
    ax1.set_title('Encoding Throughput')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Compression ratio
    ax2 = axes[0, 1]
    for method in methods:
        method_results = [r for r in results if r.method == method]
        x = [r.dimension for r in method_results]
        y = [r.compression_ratio for r in method_results]
        ax2.plot(x, y, marker='s', label=method)
    
    ax2.set_xlabel('Embedding Dimension')
    ax2.set_ylabel('Compression Ratio')
    ax2.set_title('Compression Efficiency')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Encoding time
    ax3 = axes[1, 0]
    for method in methods:
        method_results = [r for r in results if r.method == method]
        x = [r.dimension for r in method_results]
        y = [r.encoding_time_ms for r in method_results]
        ax3.plot(x, y, marker='^', label=method)
    
    ax3.set_xlabel('Embedding Dimension')
    ax3.set_ylabel('Encoding Time (ms)')
    ax3.set_title('Single Encoding Latency')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Output size
    ax4 = axes[1, 1]
    width = 0.2
    x = np.arange(len(dims))
    
    for i, method in enumerate(methods):
        method_results = [r for r in results if r.method == method]
        sizes = [r.encoded_size_bytes for r in method_results]
        ax4.bar(x + i*width, sizes, width, label=method)
    
    ax4.set_xlabel('Embedding Dimension')
    ax4.set_ylabel('Encoded Size (bytes)')
    ax4.set_title('Output Size Comparison')
    ax4.set_xticks(x + width * 1.5)
    ax4.set_xticklabels(dims)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save figure
    output_file = output_dir / 'performance_comparison.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_file}")
    
    plt.close()


if __name__ == "__main__":
    print("UUBED Benchmarking Suite")
    print("=" * 50)
    
    # Run all benchmarks
    performance_comparison()
    memory_usage_profiling()
    scalability_testing()
    hardware_optimization_benchmark()
    comparative_analysis()
    
    print("\nAll benchmarks completed!")
    print("Check ./benchmark_results/ for detailed results and visualizations.")