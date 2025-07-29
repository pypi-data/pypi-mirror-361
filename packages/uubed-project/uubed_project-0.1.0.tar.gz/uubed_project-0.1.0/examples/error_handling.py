#!/usr/bin/env python3
"""
Error handling examples for uubed.

This module demonstrates robust error handling patterns for production use,
including:
- Common error scenarios and recovery
- Custom error handlers
- Logging and monitoring integration
- Graceful degradation strategies
- Error reporting and debugging

Requirements:
    - uubed (core library)
    - numpy
    - logging (standard library)
"""

import logging
import time
import json
import numpy as np
from typing import Optional, List, Dict, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass
from contextlib import contextmanager
import traceback
import warnings

from uubed import (
    encode, decode, batch_encode,
    validate_embedding_input, validate_encoding_method,
    UubedError, UubedValidationError, UubedEncodingError,
    UubedDecodingError, UubedResourceError, UubedConnectionError,
    UubedConfigurationError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for handling strategies."""
    CRITICAL = "critical"  # System should stop
    HIGH = "high"         # Requires immediate attention
    MEDIUM = "medium"     # Can retry or use fallback
    LOW = "low"          # Can be ignored or logged


@dataclass
class ErrorContext:
    """Context information for error handling."""
    error_type: type
    error_message: str
    severity: ErrorSeverity
    timestamp: float
    context_data: Dict[str, Any]
    stack_trace: Optional[str] = None
    retry_count: int = 0
    recovery_action: Optional[str] = None


class ErrorHandler:
    """Comprehensive error handler for uubed operations."""
    
    def __init__(self, 
                 log_errors: bool = True,
                 raise_on_critical: bool = True,
                 max_retries: int = 3):
        self.log_errors = log_errors
        self.raise_on_critical = raise_on_critical
        self.max_retries = max_retries
        self.error_history: List[ErrorContext] = []
        self.error_counts: Dict[str, int] = {}
    
    def handle_error(self, 
                    error: Exception,
                    context: Dict[str, Any] = None,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> Optional[Any]:
        """Central error handling logic."""
        # Create error context
        error_ctx = ErrorContext(
            error_type=type(error),
            error_message=str(error),
            severity=severity,
            timestamp=time.time(),
            context_data=context or {},
            stack_trace=traceback.format_exc()
        )
        
        # Log error
        if self.log_errors:
            self._log_error(error_ctx)
        
        # Track error
        self._track_error(error_ctx)
        
        # Determine action based on severity
        if severity == ErrorSeverity.CRITICAL and self.raise_on_critical:
            raise error
        
        # Try recovery
        recovery_result = self._attempt_recovery(error_ctx)
        if recovery_result is not None:
            error_ctx.recovery_action = "recovered"
            return recovery_result
        
        # Return None if cannot recover
        return None
    
    def _log_error(self, error_ctx: ErrorContext):
        """Log error with appropriate level."""
        log_levels = {
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.LOW: logging.INFO
        }
        
        level = log_levels.get(error_ctx.severity, logging.WARNING)
        logger.log(
            level,
            f"{error_ctx.error_type.__name__}: {error_ctx.error_message}",
            extra={"context": error_ctx.context_data}
        )
    
    def _track_error(self, error_ctx: ErrorContext):
        """Track error for analysis."""
        self.error_history.append(error_ctx)
        
        error_key = f"{error_ctx.error_type.__name__}:{error_ctx.severity.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def _attempt_recovery(self, error_ctx: ErrorContext) -> Optional[Any]:
        """Attempt to recover from error."""
        # Recovery strategies based on error type
        if isinstance(error_ctx.error_type, UubedValidationError):
            return self._recover_from_validation_error(error_ctx)
        elif isinstance(error_ctx.error_type, UubedResourceError):
            return self._recover_from_resource_error(error_ctx)
        
        return None
    
    def _recover_from_validation_error(self, error_ctx: ErrorContext) -> Optional[Any]:
        """Recover from validation errors."""
        # Try to fix common validation issues
        if "dtype" in error_ctx.error_message:
            # Wrong dtype - try conversion
            logger.info("Attempting dtype conversion recovery")
            return "dtype_conversion_needed"
        elif "shape" in error_ctx.error_message:
            # Wrong shape - suggest reshape
            logger.info("Shape mismatch detected")
            return "reshape_needed"
        
        return None
    
    def _recover_from_resource_error(self, error_ctx: ErrorContext) -> Optional[Any]:
        """Recover from resource errors."""
        if "memory" in error_ctx.error_message.lower():
            logger.info("Memory error - suggesting batch size reduction")
            return "reduce_batch_size"
        
        return None
    
    def get_error_report(self) -> Dict[str, Any]:
        """Generate error report."""
        return {
            "total_errors": len(self.error_history),
            "error_counts": self.error_counts,
            "recent_errors": [
                {
                    "type": err.error_type.__name__,
                    "message": err.error_message,
                    "severity": err.severity.value,
                    "timestamp": err.timestamp
                }
                for err in self.error_history[-10:]  # Last 10 errors
            ]
        }


def common_error_scenarios():
    """
    Demonstrate handling of common error scenarios.
    
    Shows typical errors and recovery strategies.
    """
    print("=== Common Error Scenarios ===")
    
    error_handler = ErrorHandler()
    
    # Scenario 1: Wrong data type
    print("\n1. Wrong data type error:")
    try:
        # Float64 instead of uint8
        wrong_dtype = np.random.rand(384).astype(np.float64)
        encoded = encode(wrong_dtype, method="shq64")
    except UubedValidationError as e:
        result = error_handler.handle_error(
            e, 
            context={"data_type": str(wrong_dtype.dtype)},
            severity=ErrorSeverity.MEDIUM
        )
        
        if result == "dtype_conversion_needed":
            # Fix and retry
            print("  Converting dtype and retrying...")
            fixed_data = (wrong_dtype * 255).clip(0, 255).astype(np.uint8)
            encoded = encode(fixed_data, method="shq64")
            print(f"  Success! Encoded length: {len(encoded)}")
    
    # Scenario 2: Invalid method
    print("\n2. Invalid encoding method:")
    try:
        data = np.random.randint(0, 256, 384, dtype=np.uint8)
        encoded = encode(data, method="invalid_method")
    except UubedError as e:
        result = error_handler.handle_error(
            e,
            context={"requested_method": "invalid_method"},
            severity=ErrorSeverity.LOW
        )
        
        # Fallback to default method
        print("  Falling back to default method...")
        encoded = encode(data, method="shq64")
        print(f"  Success with fallback! Encoded length: {len(encoded)}")
    
    # Scenario 3: Memory issues with large batch
    print("\n3. Memory error simulation:")
    try:
        # Simulate very large batch
        huge_batch = np.random.randint(0, 256, (100000, 2048), dtype=np.uint8)
        # In real scenario, this might cause memory error
        print("  Processing large batch...")
        
        # Simulate memory error
        raise UubedResourceError("Insufficient memory for batch encoding")
        
    except UubedResourceError as e:
        result = error_handler.handle_error(
            e,
            context={"batch_size": 100000, "embedding_dim": 2048},
            severity=ErrorSeverity.HIGH
        )
        
        if result == "reduce_batch_size":
            print("  Reducing batch size and processing in chunks...")
            # Process in smaller chunks
            chunk_size = 1000
            for i in range(0, 5000, chunk_size):  # Process subset
                chunk = np.random.randint(0, 256, (chunk_size, 2048), dtype=np.uint8)
                encoded_chunk = batch_encode(chunk, method="shq64")
            print("  Success with chunked processing!")
    
    # Show error report
    print("\nError Report:")
    report = error_handler.get_error_report()
    print(f"  Total errors: {report['total_errors']}")
    print(f"  Error types: {report['error_counts']}")
    print()


def custom_error_handlers():
    """
    Demonstrate custom error handling strategies.
    
    Shows how to build application-specific error handlers.
    """
    print("=== Custom Error Handlers ===")
    
    class RetryHandler:
        """Handler with exponential backoff retry logic."""
        
        def __init__(self, max_retries: int = 3, base_delay: float = 0.1):
            self.max_retries = max_retries
            self.base_delay = base_delay
        
        def encode_with_retry(self, 
                            data: np.ndarray, 
                            method: str = "auto") -> Optional[str]:
            """Encode with automatic retry on failure."""
            last_error = None
            
            for attempt in range(self.max_retries):
                try:
                    # Validate before encoding
                    validate_embedding_input(data, method=method)
                    
                    # Attempt encoding
                    result = encode(data, method=method)
                    
                    if attempt > 0:
                        logger.info(f"Succeeded after {attempt + 1} attempts")
                    
                    return result
                    
                except UubedError as e:
                    last_error = e
                    delay = self.base_delay * (2 ** attempt)
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
            
            logger.error(f"All {self.max_retries} attempts failed")
            raise last_error
    
    class FallbackHandler:
        """Handler with method fallback chain."""
        
        def __init__(self, fallback_chain: List[str] = None):
            self.fallback_chain = fallback_chain or ["shq64", "t8q64", "zoq64", "eq64"]
        
        def encode_with_fallback(self, data: np.ndarray) -> Tuple[str, str]:
            """Encode with fallback to alternative methods."""
            errors = []
            
            for method in self.fallback_chain:
                try:
                    logger.info(f"Trying method: {method}")
                    result = encode(data, method=method)
                    return result, method
                    
                except UubedError as e:
                    errors.append((method, str(e)))
                    logger.warning(f"Method {method} failed: {e}")
            
            # All methods failed
            error_summary = "; ".join([f"{m}: {e}" for m, e in errors])
            raise UubedError(f"All encoding methods failed: {error_summary}")
    
    # Test retry handler
    print("\n1. Testing retry handler:")
    retry_handler = RetryHandler(max_retries=3, base_delay=0.05)
    
    # Simulate intermittent failures
    class IntermittentEncoder:
        def __init__(self, failure_rate: float = 0.5):
            self.failure_rate = failure_rate
            self.call_count = 0
        
        def encode(self, data: np.ndarray, method: str) -> str:
            self.call_count += 1
            if np.random.rand() < self.failure_rate and self.call_count < 3:
                raise UubedEncodingError("Simulated transient error")
            return encode(data, method=method)
    
    # Test with good data
    test_data = np.random.randint(0, 256, 512, dtype=np.uint8)
    try:
        result = retry_handler.encode_with_retry(test_data, method="shq64")
        print(f"  Success! Encoded length: {len(result)}")
    except Exception as e:
        print(f"  Failed after retries: {e}")
    
    # Test fallback handler
    print("\n2. Testing fallback handler:")
    fallback_handler = FallbackHandler()
    
    # Create data that might fail with some methods
    special_data = np.zeros(100, dtype=np.uint8)  # All zeros might be problematic
    
    try:
        result, used_method = fallback_handler.encode_with_fallback(special_data)
        print(f"  Success with method: {used_method}")
        print(f"  Encoded length: {len(result)}")
    except Exception as e:
        print(f"  All methods failed: {e}")
    
    print()


def error_context_managers():
    """
    Demonstrate context managers for error handling.
    
    Shows clean error handling patterns using context managers.
    """
    print("=== Error Context Managers ===")
    
    @contextmanager
    def safe_encoding_context(method: str = "auto", 
                            fallback_method: str = "eq64"):
        """Context manager for safe encoding with automatic fallback."""
        start_time = time.time()
        success = False
        used_method = method
        
        try:
            yield {"method": method}
            success = True
            
        except UubedValidationError as e:
            logger.warning(f"Validation error with {method}: {e}")
            logger.info(f"Attempting fallback to {fallback_method}")
            
            # Set fallback
            used_method = fallback_method
            yield {"method": fallback_method, "fallback": True}
            success = True
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
            
        finally:
            elapsed = time.time() - start_time
            logger.info(
                f"Encoding {'succeeded' if success else 'failed'} "
                f"with {used_method} in {elapsed:.3f}s"
            )
    
    @contextmanager
    def batch_processing_guard(max_memory_mb: float = 1000):
        """Guard against excessive memory usage in batch processing."""
        import psutil
        
        if not psutil:
            yield
            return
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024**2)
        
        try:
            yield
            
        finally:
            final_memory = process.memory_info().rss / (1024**2)
            memory_used = final_memory - initial_memory
            
            if memory_used > max_memory_mb:
                warnings.warn(
                    f"Batch processing used {memory_used:.1f}MB "
                    f"(limit: {max_memory_mb}MB)",
                    ResourceWarning
                )
    
    # Example 1: Safe encoding
    print("\n1. Safe encoding with context manager:")
    test_data = np.random.rand(768).astype(np.float32)  # Wrong dtype
    
    with safe_encoding_context(method="shq64", fallback_method="eq64") as ctx:
        # First attempt might fail due to dtype
        try:
            if not ctx.get("fallback"):
                # This will fail
                result = encode(test_data, method=ctx["method"])
        except:
            # Convert and retry with fallback
            test_data_uint8 = (test_data * 255).astype(np.uint8)
            result = encode(test_data_uint8, method=ctx["method"])
            print(f"  Encoded successfully with {ctx['method']}")
    
    # Example 2: Memory guard
    print("\n2. Batch processing with memory guard:")
    with batch_processing_guard(max_memory_mb=100):
        # Process batches
        for i in range(5):
            batch = np.random.randint(0, 256, (1000, 1536), dtype=np.uint8)
            encoded = batch_encode(batch, method="shq64")
            print(f"  Processed batch {i+1}: {len(encoded)} embeddings")
    
    print()


def logging_and_monitoring():
    """
    Demonstrate integration with logging and monitoring systems.
    
    Shows structured logging and metrics collection.
    """
    print("=== Logging and Monitoring Integration ===")
    
    class MonitoredEncoder:
        """Encoder with built-in monitoring capabilities."""
        
        def __init__(self, 
                     name: str = "production_encoder",
                     metrics_interval: float = 60.0):
            self.name = name
            self.metrics_interval = metrics_interval
            self.metrics = {
                "total_requests": 0,
                "successful_encodings": 0,
                "failed_encodings": 0,
                "total_bytes_processed": 0,
                "error_types": {},
                "method_usage": {},
                "latencies": []
            }
            self.last_metrics_time = time.time()
            
            # Setup structured logger
            self.logger = logging.getLogger(f"uubed.{name}")
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(extra)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        def encode_monitored(self, 
                           data: np.ndarray, 
                           method: str = "auto",
                           request_id: str = None) -> Optional[str]:
            """Encode with full monitoring."""
            start_time = time.time()
            request_id = request_id or f"req_{int(time.time()*1000)}"
            
            # Log request
            self.logger.info(
                "Encoding request received",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "data_shape": data.shape,
                    "data_dtype": str(data.dtype)
                }
            )
            
            self.metrics["total_requests"] += 1
            self.metrics["method_usage"][method] = \
                self.metrics["method_usage"].get(method, 0) + 1
            
            try:
                # Validate
                validate_embedding_input(data, method=method)
                
                # Encode
                result = encode(data, method=method)
                
                # Update metrics
                latency = (time.time() - start_time) * 1000
                self.metrics["successful_encodings"] += 1
                self.metrics["total_bytes_processed"] += data.nbytes
                self.metrics["latencies"].append(latency)
                
                # Keep only recent latencies
                if len(self.metrics["latencies"]) > 1000:
                    self.metrics["latencies"] = self.metrics["latencies"][-1000:]
                
                # Log success
                self.logger.info(
                    "Encoding successful",
                    extra={
                        "request_id": request_id,
                        "latency_ms": latency,
                        "output_size": len(result)
                    }
                )
                
                # Check if metrics should be reported
                self._maybe_report_metrics()
                
                return result
                
            except Exception as e:
                # Update error metrics
                self.metrics["failed_encodings"] += 1
                error_type = type(e).__name__
                self.metrics["error_types"][error_type] = \
                    self.metrics["error_types"].get(error_type, 0) + 1
                
                # Log error
                self.logger.error(
                    f"Encoding failed: {e}",
                    extra={
                        "request_id": request_id,
                        "error_type": error_type,
                        "error_details": str(e)
                    },
                    exc_info=True
                )
                
                return None
        
        def _maybe_report_metrics(self):
            """Report metrics if interval has passed."""
            current_time = time.time()
            if current_time - self.last_metrics_time >= self.metrics_interval:
                self._report_metrics()
                self.last_metrics_time = current_time
        
        def _report_metrics(self):
            """Report current metrics."""
            # Calculate summary statistics
            if self.metrics["latencies"]:
                latency_stats = {
                    "p50": np.percentile(self.metrics["latencies"], 50),
                    "p95": np.percentile(self.metrics["latencies"], 95),
                    "p99": np.percentile(self.metrics["latencies"], 99),
                    "mean": np.mean(self.metrics["latencies"])
                }
            else:
                latency_stats = {}
            
            success_rate = (
                self.metrics["successful_encodings"] / 
                self.metrics["total_requests"]
                if self.metrics["total_requests"] > 0 else 0
            )
            
            # Log metrics
            self.logger.info(
                "Metrics report",
                extra={
                    "total_requests": self.metrics["total_requests"],
                    "success_rate": success_rate,
                    "bytes_processed": self.metrics["total_bytes_processed"],
                    "latency_stats": latency_stats,
                    "error_breakdown": self.metrics["error_types"],
                    "method_usage": self.metrics["method_usage"]
                }
            )
            
            # In production, send to monitoring system
            # send_to_prometheus(self.metrics)
            # send_to_cloudwatch(self.metrics)
    
    # Create monitored encoder
    encoder = MonitoredEncoder(
        name="example_encoder",
        metrics_interval=5.0  # Report every 5 seconds for demo
    )
    
    print("Processing requests with monitoring...")
    
    # Simulate various requests
    for i in range(20):
        # Mix of successful and failing requests
        if i % 5 == 0:
            # Wrong dtype - will fail
            data = np.random.rand(384).astype(np.float64)
        else:
            # Correct dtype
            data = np.random.randint(0, 256, 384, dtype=np.uint8)
        
        method = ["shq64", "t8q64", "zoq64"][i % 3]
        
        result = encoder.encode_monitored(
            data,
            method=method,
            request_id=f"test_req_{i}"
        )
        
        if result:
            print(f"  Request {i}: Success (length={len(result)})")
        else:
            print(f"  Request {i}: Failed")
        
        time.sleep(0.3)  # Simulate request spacing
    
    # Force final metrics report
    encoder._report_metrics()
    print()


def debugging_tools():
    """
    Demonstrate debugging tools and techniques.
    
    Shows how to diagnose and fix encoding issues.
    """
    print("=== Debugging Tools ===")
    
    class EncodingDebugger:
        """Debugging utilities for encoding issues."""
        
        @staticmethod
        def analyze_embedding(data: np.ndarray) -> Dict[str, Any]:
            """Analyze embedding for potential issues."""
            analysis = {
                "shape": data.shape,
                "dtype": str(data.dtype),
                "size_bytes": data.nbytes,
                "min_value": float(np.min(data)),
                "max_value": float(np.max(data)),
                "mean_value": float(np.mean(data)),
                "std_value": float(np.std(data)),
                "unique_values": len(np.unique(data)),
                "zero_count": int(np.sum(data == 0)),
                "issues": []
            }
            
            # Check for common issues
            if data.dtype != np.uint8:
                analysis["issues"].append(f"Wrong dtype: {data.dtype} (expected uint8)")
            
            if len(data.shape) != 1:
                analysis["issues"].append(f"Wrong shape: {data.shape} (expected 1D)")
            
            if analysis["min_value"] < 0 or analysis["max_value"] > 255:
                analysis["issues"].append(
                    f"Values out of range: [{analysis['min_value']}, {analysis['max_value']}]"
                )
            
            if analysis["unique_values"] < 10:
                analysis["issues"].append(
                    f"Low diversity: only {analysis['unique_values']} unique values"
                )
            
            return analysis
        
        @staticmethod
        def suggest_fixes(analysis: Dict[str, Any]) -> List[str]:
            """Suggest fixes based on analysis."""
            suggestions = []
            
            for issue in analysis["issues"]:
                if "dtype" in issue:
                    suggestions.append(
                        "Convert to uint8: data = (data * 255).clip(0, 255).astype(np.uint8)"
                    )
                elif "shape" in issue:
                    suggestions.append(
                        "Flatten array: data = data.flatten()"
                    )
                elif "out of range" in issue:
                    suggestions.append(
                        "Clip values: data = np.clip(data, 0, 255).astype(np.uint8)"
                    )
                elif "Low diversity" in issue:
                    suggestions.append(
                        "Check if data is properly normalized or consider different encoding"
                    )
            
            return suggestions
        
        @staticmethod
        def test_encoding_methods(data: np.ndarray) -> Dict[str, Any]:
            """Test all encoding methods and report results."""
            methods = ["eq64", "shq64", "t8q64", "zoq64"]
            results = {}
            
            for method in methods:
                try:
                    start = time.time()
                    encoded = encode(data, method=method)
                    elapsed = time.time() - start
                    
                    results[method] = {
                        "success": True,
                        "encoded_length": len(encoded),
                        "encoding_time": elapsed,
                        "compression_ratio": data.nbytes / len(encoded)
                    }
                    
                except Exception as e:
                    results[method] = {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
            
            return results
    
    debugger = EncodingDebugger()
    
    # Example 1: Debug problematic embedding
    print("\n1. Debugging problematic embedding:")
    problematic_data = np.array([0.1, 0.2, 300.5, -10.0], dtype=np.float32)
    
    analysis = debugger.analyze_embedding(problematic_data)
    print(f"  Analysis: {json.dumps(analysis, indent=2)}")
    
    if analysis["issues"]:
        print("\n  Issues found:")
        for issue in analysis["issues"]:
            print(f"    - {issue}")
        
        suggestions = debugger.suggest_fixes(analysis)
        print("\n  Suggested fixes:")
        for suggestion in suggestions:
            print(f"    - {suggestion}")
    
    # Example 2: Test all methods
    print("\n2. Testing all encoding methods:")
    test_data = np.random.randint(0, 256, 512, dtype=np.uint8)
    
    method_results = debugger.test_encoding_methods(test_data)
    print("\n  Method compatibility:")
    for method, result in method_results.items():
        if result["success"]:
            print(f"    {method}: ✓ Success (length={result['encoded_length']}, "
                  f"ratio={result['compression_ratio']:.2f}x)")
        else:
            print(f"    {method}: ✗ Failed ({result['error_type']})")
    
    print()


if __name__ == "__main__":
    print("UUBED Error Handling Examples")
    print("=" * 50)
    
    # Run all examples
    common_error_scenarios()
    custom_error_handlers()
    error_context_managers()
    logging_and_monitoring()
    debugging_tools()
    
    print("\nAll error handling examples completed!")