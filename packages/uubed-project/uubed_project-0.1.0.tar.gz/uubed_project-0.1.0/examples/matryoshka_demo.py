#!/usr/bin/env python3
"""
Matryoshka (Mq64) encoding demo for uubed.

This module demonstrates the future Mq64 encoding method that provides
multi-resolution embeddings inspired by Matryoshka dolls:
- Hierarchical encoding with multiple granularities
- Progressive decoding capabilities
- Adaptive precision based on use case
- Efficient storage with quality levels

Note: This is a conceptual demonstration. Full Mq64 implementation is planned
for future releases.

Requirements:
    - uubed (core library)
    - numpy
"""

import numpy as np
import time
import json
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from uubed import encode, decode, UubedError


class MatryoshkaLevel(Enum):
    """Quality levels for Matryoshka encoding."""
    NANO = "nano"          # Ultra-compressed (4 chars)
    MICRO = "micro"        # Highly compressed (8 chars)
    MINI = "mini"          # Compressed (16 chars)
    STANDARD = "standard"  # Standard quality (32 chars)
    HIGH = "high"         # High quality (64 chars)
    ULTRA = "ultra"       # Ultra quality (128 chars)


@dataclass
class MatryoshkaEncoding:
    """Container for multi-level Matryoshka encoding."""
    levels: Dict[MatryoshkaLevel, str]
    metadata: Dict[str, Any]
    source_dim: int
    encoding_time_ms: float
    
    def get_level(self, level: MatryoshkaLevel) -> str:
        """Get encoding at specific quality level."""
        return self.levels.get(level, "")
    
    def get_progressive_levels(self) -> List[Tuple[MatryoshkaLevel, str]]:
        """Get all levels in progressive order."""
        ordered_levels = [
            MatryoshkaLevel.NANO,
            MatryoshkaLevel.MICRO,
            MatryoshkaLevel.MINI,
            MatryoshkaLevel.STANDARD,
            MatryoshkaLevel.HIGH,
            MatryoshkaLevel.ULTRA
        ]
        return [(level, self.levels[level]) 
                for level in ordered_levels 
                if level in self.levels]


class MatryoshkaEncoder:
    """
    Conceptual Matryoshka encoder demonstrating hierarchical encoding.
    
    Note: This is a simulation of the future Mq64 encoding method.
    """
    
    def __init__(self):
        self.level_configs = {
            MatryoshkaLevel.NANO: {
                "compression_ratio": 128,
                "feature_retention": 0.1,
                "char_length": 4
            },
            MatryoshkaLevel.MICRO: {
                "compression_ratio": 64,
                "feature_retention": 0.2,
                "char_length": 8
            },
            MatryoshkaLevel.MINI: {
                "compression_ratio": 32,
                "feature_retention": 0.4,
                "char_length": 16
            },
            MatryoshkaLevel.STANDARD: {
                "compression_ratio": 16,
                "feature_retention": 0.6,
                "char_length": 32
            },
            MatryoshkaLevel.HIGH: {
                "compression_ratio": 8,
                "feature_retention": 0.8,
                "char_length": 64
            },
            MatryoshkaLevel.ULTRA: {
                "compression_ratio": 4,
                "feature_retention": 0.95,
                "char_length": 128
            }
        }
    
    def encode_matryoshka(self, 
                         embedding: np.ndarray,
                         levels: List[MatryoshkaLevel] = None) -> MatryoshkaEncoding:
        """
        Encode embedding at multiple quality levels.
        
        This is a conceptual demonstration showing how Mq64 would work.
        """
        start_time = time.time()
        
        if levels is None:
            levels = list(MatryoshkaLevel)
        
        # Ensure uint8
        if embedding.dtype != np.uint8:
            embedding = (embedding * 255).clip(0, 255).astype(np.uint8)
        
        encoded_levels = {}
        
        for level in levels:
            # Simulate hierarchical encoding
            encoded = self._encode_at_level(embedding, level)
            encoded_levels[level] = encoded
        
        encoding_time = (time.time() - start_time) * 1000
        
        return MatryoshkaEncoding(
            levels=encoded_levels,
            metadata={
                "encoding_method": "mq64_simulation",
                "timestamp": time.time()
            },
            source_dim=len(embedding),
            encoding_time_ms=encoding_time
        )
    
    def _encode_at_level(self, embedding: np.ndarray, level: MatryoshkaLevel) -> str:
        """
        Simulate encoding at a specific quality level.
        
        In the real Mq64 implementation, this would use sophisticated
        dimensionality reduction and progressive encoding.
        """
        config = self.level_configs[level]
        
        # Simulate feature selection based on importance
        feature_count = int(len(embedding) * config["feature_retention"])
        
        # Select most important features (simulated by taking top values)
        top_indices = np.argsort(embedding)[-feature_count:]
        selected_features = embedding[top_indices]
        
        # Compress selected features
        compressed = self._compress_features(
            selected_features, 
            config["char_length"]
        )
        
        return compressed
    
    def _compress_features(self, features: np.ndarray, target_length: int) -> str:
        """Compress features to target string length."""
        # This is a simplified simulation
        # Real Mq64 would use advanced compression
        
        # Use different methods based on target length
        if target_length <= 8:
            # Ultra-high compression - use SimHash-like approach
            return encode(features[:min(len(features), 128)], method="shq64")[:target_length]
        elif target_length <= 32:
            # High compression - use top-k approach
            return encode(features[:min(len(features), 256)], method="t8q64")[:target_length]
        else:
            # Moderate compression
            return encode(features, method="eq64")[:target_length]
    
    def decode_progressive(self, 
                          matryoshka: MatryoshkaEncoding,
                          target_dim: int) -> List[Tuple[MatryoshkaLevel, np.ndarray]]:
        """
        Simulate progressive decoding from Matryoshka encoding.
        
        Shows how different quality levels provide different reconstructions.
        """
        results = []
        
        for level, encoded in matryoshka.get_progressive_levels():
            # Simulate reconstruction at this level
            config = self.level_configs[level]
            
            # Create reconstructed embedding
            # In real Mq64, this would use learned decoders
            reconstructed = self._reconstruct_at_level(
                encoded, 
                target_dim, 
                config["feature_retention"]
            )
            
            results.append((level, reconstructed))
        
        return results
    
    def _reconstruct_at_level(self, 
                            encoded: str, 
                            target_dim: int,
                            feature_retention: float) -> np.ndarray:
        """Simulate reconstruction from encoded data."""
        # This is a placeholder - real Mq64 would have sophisticated reconstruction
        
        # Create base reconstruction
        reconstructed = np.zeros(target_dim, dtype=np.uint8)
        
        # Fill with pattern based on encoding
        # In reality, would use learned decoder
        pattern_length = len(encoded)
        for i in range(target_dim):
            # Use encoding characters to generate values
            char_idx = i % pattern_length
            reconstructed[i] = ord(encoded[char_idx]) % 256
        
        # Add noise inversely proportional to quality
        noise_level = (1 - feature_retention) * 50
        noise = np.random.randint(-noise_level, noise_level, target_dim)
        reconstructed = np.clip(reconstructed + noise, 0, 255).astype(np.uint8)
        
        return reconstructed


def basic_matryoshka_demo():
    """
    Demonstrate basic Matryoshka encoding concepts.
    
    Shows hierarchical encoding and quality levels.
    """
    print("=== Basic Matryoshka Demo ===")
    
    encoder = MatryoshkaEncoder()
    
    # Create test embedding
    embedding_dim = 1536  # Common embedding size
    embedding = np.random.rand(embedding_dim).astype(np.float32)
    embedding = (embedding * 255).astype(np.uint8)
    
    print(f"Original embedding: {embedding_dim} dimensions")
    
    # Encode at all levels
    print("\nEncoding at multiple quality levels...")
    matryoshka = encoder.encode_matryoshka(embedding)
    
    print(f"Encoding time: {matryoshka.encoding_time_ms:.2f}ms")
    print("\nEncoded sizes by level:")
    
    for level, encoded in matryoshka.get_progressive_levels():
        compression_ratio = embedding_dim / len(encoded)
        print(f"  {level.value:>10}: {len(encoded):>3} chars "
              f"(compression: {compression_ratio:.1f}x)")
    
    # Show actual encodings
    print("\nSample encodings:")
    for level in [MatryoshkaLevel.NANO, MatryoshkaLevel.MINI, MatryoshkaLevel.HIGH]:
        encoded = matryoshka.get_level(level)
        print(f"  {level.value}: {encoded[:50]}{'...' if len(encoded) > 50 else ''}")
    
    print()


def progressive_quality_demo():
    """
    Demonstrate progressive quality in Matryoshka encoding.
    
    Shows how different levels preserve different amounts of information.
    """
    print("=== Progressive Quality Demo ===")
    
    encoder = MatryoshkaEncoder()
    
    # Create structured embedding with clear patterns
    embedding_dim = 768
    
    # Create embedding with multiple frequency components
    t = np.linspace(0, 10, embedding_dim)
    embedding = (
        np.sin(t) * 50 +           # Low frequency
        np.sin(t * 10) * 30 +      # Medium frequency
        np.sin(t * 50) * 20 +      # High frequency
        128                         # Offset
    ).astype(np.uint8)
    
    print("Created structured embedding with multiple frequencies")
    
    # Encode
    matryoshka = encoder.encode_matryoshka(embedding)
    
    # Decode at different levels
    print("\nProgressive reconstruction quality:")
    reconstructions = encoder.decode_progressive(matryoshka, embedding_dim)
    
    for level, reconstructed in reconstructions:
        # Calculate reconstruction error
        mse = np.mean((embedding.astype(float) - reconstructed.astype(float)) ** 2)
        rmse = np.sqrt(mse)
        
        # Calculate correlation
        correlation = np.corrcoef(embedding, reconstructed)[0, 1]
        
        print(f"\n  {level.value}:")
        print(f"    RMSE: {rmse:.2f}")
        print(f"    Correlation: {correlation:.3f}")
        print(f"    Size: {len(matryoshka.get_level(level))} chars")
    
    print()


def adaptive_precision_demo():
    """
    Demonstrate adaptive precision selection based on use case.
    
    Shows how to choose appropriate quality levels dynamically.
    """
    print("=== Adaptive Precision Demo ===")
    
    class AdaptiveMatryoshkaEncoder(MatryoshkaEncoder):
        """Encoder with adaptive precision selection."""
        
        def select_optimal_level(self,
                               embedding: np.ndarray,
                               constraints: Dict[str, Any]) -> MatryoshkaLevel:
            """Select optimal encoding level based on constraints."""
            max_size = constraints.get("max_size_chars", float('inf'))
            min_quality = constraints.get("min_quality", 0.0)
            latency_budget_ms = constraints.get("latency_budget_ms", float('inf'))
            
            # Analyze embedding characteristics
            entropy = self._estimate_entropy(embedding)
            
            # Select level based on constraints and characteristics
            if max_size <= 4:
                return MatryoshkaLevel.NANO
            elif max_size <= 8 or latency_budget_ms < 0.1:
                return MatryoshkaLevel.MICRO
            elif max_size <= 16 or (entropy < 0.5 and min_quality < 0.5):
                return MatryoshkaLevel.MINI
            elif max_size <= 32 or min_quality < 0.7:
                return MatryoshkaLevel.STANDARD
            elif max_size <= 64 or min_quality < 0.9:
                return MatryoshkaLevel.HIGH
            else:
                return MatryoshkaLevel.ULTRA
        
        def _estimate_entropy(self, embedding: np.ndarray) -> float:
            """Estimate information entropy of embedding."""
            # Simple entropy estimation
            hist, _ = np.histogram(embedding, bins=16)
            hist = hist / hist.sum()
            hist = hist[hist > 0]  # Remove zeros
            entropy = -np.sum(hist * np.log2(hist))
            return entropy / np.log2(16)  # Normalize
    
    encoder = AdaptiveMatryoshkaEncoder()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Real-time search",
            "constraints": {
                "max_size_chars": 16,
                "latency_budget_ms": 0.5,
                "min_quality": 0.4
            }
        },
        {
            "name": "High-quality archival",
            "constraints": {
                "max_size_chars": 128,
                "min_quality": 0.9
            }
        },
        {
            "name": "Mobile application",
            "constraints": {
                "max_size_chars": 8,
                "latency_budget_ms": 0.1
            }
        },
        {
            "name": "Balanced web service",
            "constraints": {
                "max_size_chars": 32,
                "min_quality": 0.6,
                "latency_budget_ms": 1.0
            }
        }
    ]
    
    # Test each scenario
    test_embedding = np.random.rand(1024).astype(np.float32)
    test_embedding = (test_embedding * 255).astype(np.uint8)
    
    print("Testing adaptive precision selection:\n")
    
    for scenario in scenarios:
        print(f"{scenario['name']}:")
        print(f"  Constraints: {scenario['constraints']}")
        
        # Select optimal level
        optimal_level = encoder.select_optimal_level(
            test_embedding, 
            scenario['constraints']
        )
        
        # Encode at selected level
        matryoshka = encoder.encode_matryoshka(
            test_embedding, 
            levels=[optimal_level]
        )
        
        encoded = matryoshka.get_level(optimal_level)
        print(f"  Selected level: {optimal_level.value}")
        print(f"  Encoded size: {len(encoded)} chars")
        print(f"  Encoding time: {matryoshka.encoding_time_ms:.2f}ms")
        print()


def storage_efficiency_analysis():
    """
    Analyze storage efficiency of Matryoshka encoding.
    
    Shows space savings for different use cases.
    """
    print("=== Storage Efficiency Analysis ===")
    
    encoder = MatryoshkaEncoder()
    
    # Simulate different embedding collections
    collections = [
        {
            "name": "Text embeddings (BERT)",
            "count": 10000,
            "dim": 768
        },
        {
            "name": "Image embeddings (CLIP)",
            "count": 50000,
            "dim": 512
        },
        {
            "name": "Large embeddings (GPT)",
            "count": 5000,
            "dim": 1536
        }
    ]
    
    print("Storage requirements for different collections:\n")
    
    for collection in collections:
        print(f"{collection['name']}:")
        print(f"  Collection size: {collection['count']:,} embeddings")
        print(f"  Embedding dimension: {collection['dim']}")
        
        # Calculate baseline storage
        baseline_mb = (collection['count'] * collection['dim'] * 1) / (1024 * 1024)
        print(f"  Baseline storage (uint8): {baseline_mb:.1f} MB")
        
        # Calculate Matryoshka storage for different strategies
        print("\n  Matryoshka storage by strategy:")
        
        strategies = [
            ("Single level (MINI)", [MatryoshkaLevel.MINI]),
            ("Two levels (NANO+STANDARD)", [MatryoshkaLevel.NANO, MatryoshkaLevel.STANDARD]),
            ("Progressive (NANO+MINI+HIGH)", 
             [MatryoshkaLevel.NANO, MatryoshkaLevel.MINI, MatryoshkaLevel.HIGH]),
            ("Full hierarchy", list(MatryoshkaLevel))
        ]
        
        for strategy_name, levels in strategies:
            total_chars = 0
            for level in levels:
                config = encoder.level_configs[level]
                total_chars += config["char_length"]
            
            strategy_mb = (collection['count'] * total_chars) / (1024 * 1024)
            savings = (baseline_mb - strategy_mb) / baseline_mb * 100
            
            print(f"    {strategy_name:30} {strategy_mb:>8.1f} MB ({savings:>5.1f}% savings)")
        
        print()


def quality_vs_size_tradeoff():
    """
    Demonstrate quality vs size tradeoffs in Matryoshka encoding.
    
    Shows how to balance quality and storage requirements.
    """
    print("=== Quality vs Size Tradeoff Analysis ===")
    
    encoder = MatryoshkaEncoder()
    
    # Create test embeddings with known properties
    embedding_types = [
        {
            "name": "Random noise",
            "data": np.random.randint(0, 256, 1024, dtype=np.uint8)
        },
        {
            "name": "Smooth gradient",
            "data": np.linspace(0, 255, 1024).astype(np.uint8)
        },
        {
            "name": "Sparse features",
            "data": np.zeros(1024, dtype=np.uint8)
        }
    ]
    
    # Add some non-zero values to sparse
    embedding_types[2]["data"][::50] = 255
    
    print("Quality metrics for different embedding types:\n")
    
    # Headers
    print(f"{'Type':>15} {'Level':>10} {'Size':>6} {'Quality':>8} {'Efficiency':>11}")
    print("-" * 60)
    
    for emb_type in embedding_types:
        embedding = emb_type["data"]
        
        # Encode at all levels
        matryoshka = encoder.encode_matryoshka(embedding)
        reconstructions = encoder.decode_progressive(matryoshka, len(embedding))
        
        for level, reconstructed in reconstructions:
            # Calculate quality metric (correlation)
            quality = np.corrcoef(embedding, reconstructed)[0, 1]
            if np.isnan(quality):
                quality = 0.0
            
            # Calculate efficiency (quality per char)
            size = len(matryoshka.get_level(level))
            efficiency = quality / size if size > 0 else 0
            
            print(f"{emb_type['name']:>15} {level.value:>10} "
                  f"{size:>6} {quality:>8.3f} {efficiency:>11.4f}")
        
        print()  # Separator between types
    
    print("\nKey insights:")
    print("- Random noise: Difficult to compress, needs higher levels")
    print("- Smooth gradient: Compresses well, good quality at lower levels")
    print("- Sparse features: Excellent compression, minimal quality loss")
    print()


def future_features_preview():
    """
    Preview planned features for the full Mq64 implementation.
    
    Shows what's coming in future releases.
    """
    print("=== Future Mq64 Features Preview ===")
    
    print("\nPlanned features for full Mq64 implementation:")
    
    features = [
        {
            "name": "Learned Compression",
            "description": "Neural network-based encoding/decoding for optimal quality",
            "benefit": "Better reconstruction quality at all levels"
        },
        {
            "name": "Dynamic Level Selection",
            "description": "Automatic selection of encoding levels based on content",
            "benefit": "Optimal storage without manual configuration"
        },
        {
            "name": "Incremental Encoding",
            "description": "Add higher quality levels without re-encoding",
            "benefit": "Flexible quality upgrades as needed"
        },
        {
            "name": "Hardware Acceleration",
            "description": "SIMD and GPU support for fast encoding/decoding",
            "benefit": "Real-time processing of large embedding batches"
        },
        {
            "name": "Streaming Support",
            "description": "Progressive transmission of quality levels",
            "benefit": "Low-latency retrieval with quality improvement over time"
        },
        {
            "name": "Cross-Modal Alignment",
            "description": "Consistent encoding across different embedding types",
            "benefit": "Unified storage for multimodal systems"
        }
    ]
    
    for feature in features:
        print(f"\n{feature['name']}:")
        print(f"  {feature['description']}")
        print(f"  → {feature['benefit']}")
    
    print("\n" + "="*60)
    print("Mq64 Roadmap:")
    print("  - Phase 1: Core hierarchical encoding (demonstrated here)")
    print("  - Phase 2: Learned compression models")
    print("  - Phase 3: Hardware acceleration")
    print("  - Phase 4: Advanced features (streaming, cross-modal)")
    print()


if __name__ == "__main__":
    print("UUBED Matryoshka (Mq64) Encoding Demo")
    print("=" * 50)
    print("Note: This is a conceptual demonstration of future Mq64 features.")
    print("Full implementation is planned for upcoming releases.")
    print("=" * 50)
    print()
    
    # Run demos
    basic_matryoshka_demo()
    progressive_quality_demo()
    adaptive_precision_demo()
    storage_efficiency_analysis()
    quality_vs_size_tradeoff()
    future_features_preview()
    
    print("\nMatryoshka demo completed!")
    print("Stay tuned for the full Mq64 implementation in future uubed releases!")