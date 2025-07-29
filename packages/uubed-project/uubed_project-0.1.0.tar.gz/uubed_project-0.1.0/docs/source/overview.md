# Overview

## What is uubed?

uubed (pronounced "you-you-bed") is a high-performance library for encoding embedding vectors into position-safe strings. It solves a critical problem in modern search systems: **substring pollution**.

## The Problem: Substring Pollution

When embedding vectors are encoded as simple base64 strings, they can create false matches in search engines:

```python
# Traditional encoding creates substring pollution
embedding1 = "dGhlIHF1aWNr..."  # "the quick brown fox"
embedding2 = "YnJvd24gZm94..."  # "brown fox jumps"

# Search for embedding2 might match embedding1 due to substring "brown fox"
```

## The Solution: Position-Safe Encoding

uubed uses the QuadB64 encoding family, which employs position-dependent alphabets:

- **Position 0**: Uses uppercase letters (A-Z)
- **Position 1**: Uses lowercase letters (a-z)  
- **Position 2**: Uses mixed case
- **Position 3**: Uses digits and symbols

This ensures that no encoded string can be a substring of another, eliminating false matches.

## Encoding Methods

uubed provides four encoding methods optimized for different use cases:

### 1. Eq64 (Full Precision)
- Preserves complete embedding information
- Best for: Exact similarity search
- Output size: ~71 characters per 32 dimensions

### 2. Shq64 (SimHash)
- Locality-sensitive hashing
- Best for: Approximate nearest neighbor search
- Output size: 16 characters

### 3. T8q64 (Top-k)
- Encodes top-8 feature indices
- Best for: Sparse embeddings, feature analysis
- Output size: 16 characters

### 4. Zoq64 (Z-order)
- Spatial encoding using Morton codes
- Best for: Multi-dimensional range queries
- Output size: 8 characters

## Performance

With native Rust acceleration, uubed achieves:

- **40-105x speedup** for full precision encoding
- **>230 MB/s throughput** on modern hardware
- **60-1600x faster** Z-order encoding
- **Minimal memory overhead**

## Use Cases

- **Vector Databases**: Store embeddings as searchable strings
- **Search Engines**: Index embeddings without substring pollution
- **Caching Systems**: Use encoded strings as cache keys
- **Data Pipelines**: Efficient embedding serialization