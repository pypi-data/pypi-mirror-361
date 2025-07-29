#!/usr/bin/env python3
"""
Basic usage examples for uubed encoding library.

This script demonstrates the fundamental operations of the uubed library,
including encoding embeddings with different methods and decoding them back.
"""

import numpy as np
from uubed import encode, decode


def example_basic_encoding():
    """
    Demonstrate basic encoding of an embedding vector.
    
    This example shows how to:
    1. Create a sample embedding vector
    2. Convert it to the required uint8 format
    3. Encode it using the automatic method selection
    """
    print("=== Basic Encoding Example ===")
    
    # Create a sample embedding (e.g., from OpenAI ada-002)
    embedding_dim = 1536
    embedding = np.random.rand(embedding_dim).astype(np.float32)
    
    # Normalize to [0, 1] range (if needed)
    embedding = (embedding - embedding.min()) / (embedding.max() - embedding.min())
    
    # Convert to uint8 [0, 255]
    embedding_uint8 = (embedding * 255).astype(np.uint8)
    
    # Encode with automatic method selection
    encoded = encode(embedding_uint8, method="auto")
    
    print(f"Original embedding shape: {embedding_uint8.shape}")
    print(f"Encoded string length: {len(encoded)}")
    print(f"First 50 characters: {encoded[:50]}...")
    print()


def example_encoding_methods():
    """
    Compare different encoding methods and their characteristics.
    
    This example demonstrates:
    - Eq64: Full precision encoding
    - Shq64: SimHash for similarity preservation
    - T8q64: Top-k feature encoding
    - Zoq64: Z-order spatial encoding
    """
    print("=== Encoding Methods Comparison ===")
    
    # Create a sample embedding
    embedding = np.random.rand(384).astype(np.float32)
    embedding_uint8 = (embedding * 255).astype(np.uint8)
    
    methods = {
        "eq64": "Full precision with dots",
        "shq64": "SimHash (16 chars)",
        "t8q64": "Top-8 features (16 chars)", 
        "zoq64": "Z-order spatial (8 chars)"
    }
    
    for method, description in methods.items():
        encoded = encode(embedding_uint8, method=method)
        print(f"{method:6} - {description:30} Length: {len(encoded):3} | {encoded[:40]}...")
    print()


def example_round_trip():
    """
    Demonstrate round-trip encoding and decoding.
    
    Note: Only Eq64 supports exact round-trip conversion.
    This example verifies that the decoded data matches the original.
    """
    print("=== Round-trip Encoding/Decoding ===")
    
    # Create test data
    original = np.random.randint(0, 256, size=128, dtype=np.uint8)
    
    # Encode
    encoded = encode(original, method="eq64")
    print(f"Encoded: {encoded[:50]}...")
    
    # Decode
    decoded_bytes = decode(encoded)
    decoded_array = np.frombuffer(decoded_bytes, dtype=np.uint8)
    
    # Verify
    is_equal = np.array_equal(original, decoded_array)
    print(f"Round-trip successful: {is_equal}")
    print(f"Max difference: {np.max(np.abs(original.astype(int) - decoded_array.astype(int)))}")
    print()


def example_similarity_preservation():
    """
    Show how SimHash encoding preserves similarity relationships.
    
    This example creates similar embeddings and shows that their
    SimHash encodings are also similar or identical.
    """
    print("=== Similarity Preservation with SimHash ===")
    
    # Create base embedding
    base = np.random.rand(384).astype(np.float32)
    
    # Create similar embeddings with small perturbations
    similar1 = base + np.random.normal(0, 0.01, 384)
    similar2 = base + np.random.normal(0, 0.01, 384)
    different = np.random.rand(384).astype(np.float32)
    
    # Convert to uint8
    embeddings = {
        "base": (base * 255).clip(0, 255).astype(np.uint8),
        "similar1": (similar1 * 255).clip(0, 255).astype(np.uint8),
        "similar2": (similar2 * 255).clip(0, 255).astype(np.uint8),
        "different": (different * 255).clip(0, 255).astype(np.uint8),
    }
    
    # Encode with SimHash
    encoded = {name: encode(emb, method="shq64") for name, emb in embeddings.items()}
    
    # Compare encodings
    print("SimHash encodings:")
    for name, enc in encoded.items():
        print(f"  {name:9}: {enc}")
    
    print("\nSimilarity analysis:")
    print(f"  base == similar1: {encoded['base'] == encoded['similar1']}")
    print(f"  base == similar2: {encoded['base'] == encoded['similar2']}")
    print(f"  base == different: {encoded['base'] == encoded['different']}")
    print()


def example_batch_processing():
    """
    Demonstrate efficient batch processing of multiple embeddings.
    
    This example shows how to process many embeddings efficiently,
    which is common in production scenarios.
    """
    print("=== Batch Processing Example ===")
    
    # Create batch of embeddings
    batch_size = 100
    embedding_dim = 384
    embeddings = np.random.rand(batch_size, embedding_dim).astype(np.float32)
    embeddings_uint8 = (embeddings * 255).astype(np.uint8)
    
    # Process batch
    import time
    start_time = time.time()
    
    encoded_batch = [encode(emb, method="shq64") for emb in embeddings_uint8]
    
    elapsed = time.time() - start_time
    
    print(f"Processed {batch_size} embeddings in {elapsed:.3f} seconds")
    print(f"Average time per embedding: {elapsed/batch_size*1000:.2f} ms")
    print(f"Throughput: {batch_size/elapsed:.1f} embeddings/second")
    print()


if __name__ == "__main__":
    # Run all examples
    example_basic_encoding()
    example_encoding_methods()
    example_round_trip()
    example_similarity_preservation()
    example_batch_processing()
    
    print("All examples completed successfully!")