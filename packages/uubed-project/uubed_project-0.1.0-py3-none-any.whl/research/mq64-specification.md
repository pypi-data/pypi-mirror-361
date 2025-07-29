# Mq64 Encoding Specification
## Matryoshka Position-Safe Encoding for Hierarchical Embeddings

**Version**: 1.0.0-draft  
**Status**: Specification Draft  
**Target Implementation**: uubed v2.0.0

## Abstract

Mq64 (Matryoshka QuadB64) is a position-safe encoding scheme designed specifically for hierarchical embeddings that follow the Matryoshka Representation Learning (MRL) pattern. It extends the QuadB64 family to support progressive decoding at multiple dimensional resolutions while maintaining substring pollution protection.

## 1. Background and Motivation

### 1.1 Matryoshka Embeddings Overview

Matryoshka embeddings organize semantic information hierarchically, with the most important features concentrated in the first dimensions. This allows for:

- **Progressive refinement**: Start with low-dimensional approximations, refine with higher dimensions
- **Adaptive quality**: Choose dimension count based on computational/storage constraints
- **Backward compatibility**: Truncated embeddings remain semantically meaningful

### 1.2 Position Safety Requirements

Standard Base64 encoding causes substring pollution in search engines. Mq64 must maintain position safety across all hierarchical levels to prevent false matches when encoded embeddings are indexed in search systems.

### 1.3 Design Goals

1. **Hierarchical Position Safety**: Prevent substring matches across and within hierarchy levels
2. **Progressive Decodability**: Support decoding at any hierarchy level (64, 128, 256, 512, 1024+ dimensions)
3. **Compression Efficiency**: Leverage redundancy between hierarchy levels
4. **Universal Compatibility**: Work with any Matryoshka-trained embedding model
5. **Performance**: Maintain encoding/decoding performance comparable to existing QuadB64 schemes

## 2. Technical Specification

### 2.1 Hierarchical Alphabet System

Mq64 uses nested position-safe alphabets with hierarchy-aware character mapping:

```
Level 1 (dims 1-64):    ABCDEFGHIJKLMNOP (positions 0,4,8,12,...)
                        QRSTUVWXYZabcdef (positions 1,5,9,13,...)
                        ghijklmnopqrstuv (positions 2,6,10,14,...)
                        wxyz0123456789-_ (positions 3,7,11,15,...)

Level 2 (dims 65-128):  ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠ (positions 0,4,8,12,...)
                        ΡΣΤΥΦΧΨΩαβγδεζητ (positions 1,5,9,13,...)
                        θικλμνξοπρστυφχψ (positions 2,6,10,14,...)
                        ωάέήίόύώΐΰ₀₁₂₃₄₅ (positions 3,7,11,15,...)

Level 3 (dims 129-256): АБВГДЕЁЖЗИЙКЛМНОПα (positions 0,4,8,12,...)
                        РСТУФХЦЧШЩЪЫЬЭЮЯаб (positions 1,5,9,13,...)
                        вгдеёжзийклмнопрс (positions 2,6,10,14,...)
                        туфхцчшщъыьэюя∆∇∂∏ (positions 3,7,11,15,...)

Level 4+ (dims 257+):   Extended Unicode mathematical symbols
```

**Hierarchy Markers:**
- `:` (colon) - Separates major hierarchy levels (every 64 dimensions)
- `.` (dot) - Separates chunks within levels (every 4 characters, as in standard QuadB64)

### 2.2 Encoding Format Structure

```
Mq64 Encoding Format:
[Level1]:[Level2]:[Level3]:[Level4+]

Where each level contains:
[chunk1.chunk2.chunk3.chunk4....]

Example for 256-dimensional embedding:
ABcd.EFgh.IJkl.MNop:ΑΒγδ.ΕΖηθ.ΙΚλμ.ΝΞοπ:АБвг.ДЕёж.ЗИйк.ЛМнп
^--- Level 1 (64 dims) ---^--- Level 2 (128 dims) ---^--- Level 3 (256 dims) ---^
```

### 2.3 Progressive Decoding Algorithm

```python
def decode_mq64(encoded: str, target_dims: Optional[int] = None) -> bytes:
    """
    Decode Mq64 string progressively up to target_dims.
    
    Args:
        encoded: Mq64-encoded string
        target_dims: Target dimensions (None = full decoding)
    
    Returns:
        Decoded bytes representing embedding up to target_dims
    """
    levels = encoded.split(':')
    
    if target_dims is None:
        # Decode all levels
        decoded_parts = []
        for level in levels:
            decoded_parts.append(decode_level(level))
        return b''.join(decoded_parts)
    
    # Progressive decoding up to target_dims
    target_level = (target_dims - 1) // 64  # 0-indexed level
    target_remainder = target_dims % 64
    
    decoded_parts = []
    
    # Decode complete levels
    for i in range(target_level):
        if i < len(levels):
            decoded_parts.append(decode_level(levels[i]))
    
    # Decode partial level if needed
    if target_remainder > 0 and target_level < len(levels):
        partial_chunks = target_remainder // 16  # 16 bytes per chunk
        chunks = levels[target_level].split('.')
        
        for i in range(partial_chunks):
            if i < len(chunks):
                decoded_parts.append(decode_chunk(chunks[i], level=target_level))
        
        # Handle remaining bytes in partial chunk
        remaining_bytes = target_remainder % 16
        if remaining_bytes > 0 and partial_chunks < len(chunks):
            partial_chunk = decode_chunk(chunks[partial_chunks], level=target_level)
            decoded_parts.append(partial_chunk[:remaining_bytes])
    
    return b''.join(decoded_parts)
```

### 2.4 Compression Strategy

#### 2.4.1 Hierarchical Redundancy Reduction

Matryoshka embeddings often exhibit decreasing information density in higher dimensions. Mq64 exploits this through:

1. **Adaptive Quantization**: Higher levels may use reduced precision (8-bit → 6-bit → 4-bit)
2. **Sparse Encoding**: Near-zero values in higher dimensions compressed more aggressively
3. **Delta Encoding**: Higher levels store differences from lower-level predictions

#### 2.4.2 Level-Specific Optimization

```python
def adaptive_encode_level(data: bytes, level: int) -> str:
    """
    Apply level-specific encoding optimizations.
    
    Level 0 (dims 1-64):    Full precision, optimized for accuracy
    Level 1 (dims 65-128):  Reduced precision, optimized for similarity
    Level 2+ (dims 129+):   Aggressive compression, optimized for size
    """
    if level == 0:
        return standard_q64_encode(data)
    elif level == 1:
        return reduced_precision_encode(data, bits=6)
    else:
        return sparse_delta_encode(data, reference_level=level-1)
```

### 2.5 Error Detection and Correction

#### 2.5.1 Hierarchical Checksums

Each level includes a position-safe checksum to detect corruption:

```
Level Format: [data_chunks][checksum_chunk]
Example: ABcd.EFgh.IJkl.MNop.XYzw
                               ^--- checksum
```

#### 2.5.2 Progressive Validation

Validation can occur at any hierarchy level:

```python
def validate_mq64(encoded: str, level: Optional[int] = None) -> bool:
    """
    Validate Mq64 encoding integrity.
    
    Args:
        encoded: Mq64 string
        level: Specific level to validate (None = all levels)
    
    Returns:
        True if valid, False if corrupted
    """
    levels = encoded.split(':')
    
    target_levels = [level] if level is not None else range(len(levels))
    
    for lvl in target_levels:
        if lvl >= len(levels):
            return False
        
        chunks = levels[lvl].split('.')
        if len(chunks) < 2:  # Need at least data + checksum
            return False
        
        data_chunks = chunks[:-1]
        checksum_chunk = chunks[-1]
        
        computed_checksum = compute_level_checksum(data_chunks, lvl)
        if checksum_chunk != computed_checksum:
            return False
    
    return True
```

## 3. Implementation Guidelines

### 3.1 API Design

#### 3.1.1 Core Functions

```python
# Core encoding/decoding
def mq64_encode(embedding: Union[np.ndarray, List[float]], 
                levels: Optional[List[int]] = None) -> str:
    """Encode embedding with Mq64 at specified dimensional levels."""

def mq64_decode(encoded: str, 
                target_dims: Optional[int] = None) -> np.ndarray:
    """Decode Mq64 string up to target dimensions."""

# Progressive operations
def mq64_get_levels(encoded: str) -> List[int]:
    """Get available dimensional levels in encoded string."""

def mq64_truncate(encoded: str, max_dims: int) -> str:
    """Truncate encoded string to maximum dimensions."""

def mq64_extend(encoded: str, additional_data: bytes) -> str:
    """Extend encoded string with additional dimensional data."""
```

#### 3.1.2 Auto-Detection

```python
def detect_matryoshka_structure(embedding: np.ndarray) -> Optional[List[int]]:
    """
    Detect if embedding follows Matryoshka pattern.
    
    Returns suggested hierarchy levels or None if not Matryoshka-compatible.
    """
    # Analyze information density across dimensions
    # Detect natural breakpoints at 64, 128, 256, 512, 1024
    # Return recommended level structure
```

### 3.2 Performance Considerations

#### 3.2.1 Streaming Support

```python
class Mq64StreamEncoder:
    """Stream large datasets with progressive encoding."""
    
    def __init__(self, levels: List[int], buffer_size: int = 1024):
        self.levels = levels
        self.buffer_size = buffer_size
    
    def encode_batch(self, embeddings: Iterable[np.ndarray]) -> Iterator[str]:
        """Encode embeddings in batches for memory efficiency."""
        
    def encode_with_progress(self, embeddings: Iterable[np.ndarray], 
                           callback: Callable[[int], None]) -> Iterator[str]:
        """Encode with progress reporting."""
```

#### 3.2.2 SIMD Optimization

- **Level-Parallel Processing**: Encode multiple hierarchy levels simultaneously
- **Vectorized Alphabet Lookup**: Use SIMD for character mapping across levels
- **Batch Checksum Computation**: Vectorized error detection calculations

### 3.3 Quality Assurance

#### 3.3.1 Test Coverage Requirements

```python
# Roundtrip tests
def test_mq64_roundtrip(dims: int, levels: List[int]):
    """Verify encoding -> decoding produces original data."""

# Progressive decoding tests  
def test_progressive_decoding(dims: int):
    """Verify partial decoding at each level produces correct subsets."""

# Position safety tests
def test_position_safety():
    """Verify no substring matches across hierarchy levels."""

# Performance regression tests
def test_performance_benchmarks():
    """Ensure performance meets specification requirements."""
```

#### 3.3.2 Compatibility Testing

- **Matryoshka Model Compatibility**: Test with OpenAI, Nomic, Alibaba GTE models
- **Cross-Platform Validation**: Ensure consistent results across architectures
- **Unicode Handling**: Verify proper Unicode alphabet handling

## 4. Migration and Adoption Strategy

### 4.1 Backward Compatibility

Mq64 maintains compatibility with existing QuadB64 schemes:

```python
def auto_detect_encoding(encoded: str) -> str:
    """
    Automatically detect encoding scheme.
    
    Returns: 'eq64', 'shq64', 't8q64', 'zoq64', 'mq64', or 'unknown'
    """
    if ':' in encoded:
        return 'mq64'  # Hierarchy markers indicate Mq64
    elif '.' in encoded and len(encoded) > 20:
        return 'eq64'  # Dots with length suggest Eq64
    # ... other detection logic
```

### 4.2 Integration Examples

#### 4.2.1 OpenAI text-embedding-3

```python
import openai
from uubed import mq64_encode

# Get Matryoshka embedding from OpenAI
response = openai.embeddings.create(
    model="text-embedding-3-large",
    input="Example text",
    dimensions=1024  # Full dimensions
)

embedding = response.data[0].embedding

# Encode with Mq64 at multiple levels
encoded = mq64_encode(embedding, levels=[64, 128, 256, 512, 1024])

# Progressive retrieval: start with 64 dims, refine to 1024
quick_match = mq64_decode(encoded, target_dims=64)
refined_match = mq64_decode(encoded, target_dims=1024)
```

#### 4.2.2 Vector Database Integration

```python
# Pinecone with progressive search
def progressive_search(query_embedding, index):
    """Search using progressive refinement."""
    
    # Encode query at multiple levels
    query_encoded = mq64_encode(query_embedding, levels=[64, 256, 1024])
    
    # Coarse search with 64 dimensions
    coarse_results = index.query(
        vector=mq64_decode(query_encoded, target_dims=64),
        top_k=100,
        include_metadata=True
    )
    
    # Refine with full 1024 dimensions
    refined_results = []
    for result in coarse_results.matches:
        full_embedding = mq64_decode(result.metadata['mq64_code'])
        refined_score = cosine_similarity(
            mq64_decode(query_encoded),
            full_embedding
        )
        refined_results.append((result.id, refined_score))
    
    return sorted(refined_results, key=lambda x: x[1], reverse=True)[:10]
```

## 5. Performance Specifications

### 5.1 Encoding Performance Targets

| Operation | Target Performance | Baseline (Eq64) | Improvement |
|-----------|-------------------|------------------|-------------|
| Level 1 (64 dims) | 250+ MB/s | 234 MB/s | 1.1x |
| Level 2 (128 dims) | 200+ MB/s | N/A | New |
| Level 3 (256 dims) | 180+ MB/s | N/A | New |
| Full (1024 dims) | 150+ MB/s | N/A | New |
| Progressive Decode | 300+ MB/s | N/A | New |

### 5.2 Memory Efficiency Targets

| Metric | Target | Benefit |
|--------|--------|---------|
| Storage Reduction | 2-5x vs separate level storage | Space efficiency |
| Memory Overhead | < 5% vs single-level encoding | Memory efficiency |
| Streaming Support | Constant memory usage | Scalability |

### 5.3 Quality Metrics

| Metric | Target | Verification |
|--------|--------|-------------|
| Position Safety | 100% substring pollution prevention | Automated testing |
| Roundtrip Accuracy | 100% bit-perfect reconstruction | Unit tests |
| Progressive Accuracy | > 99% semantic similarity at each level | Similarity benchmarks |
| Error Detection | > 99.9% corruption detection rate | Fuzzing tests |

## 6. Future Extensions

### 6.1 Advanced Compression

- **Neural Compression**: Train neural networks to predict higher levels from lower levels
- **Context-Aware Encoding**: Adapt compression based on embedding content patterns
- **Multi-Modal Extensions**: Support for image-text Matryoshka embeddings (CLIP-style)

### 6.2 Query Optimization

- **Adaptive Search**: Automatically choose optimal dimensional level for queries
- **Index Structures**: Specialized index structures for hierarchical embeddings
- **Caching Strategies**: Multi-level caching for frequently accessed embeddings

### 6.3 Ecosystem Integration

- **Database Native Support**: Native Mq64 support in vector databases
- **Framework Integration**: Direct support in embedding frameworks (LangChain, LlamaIndex)
- **Hardware Acceleration**: GPU/TPU optimized implementations

## 7. Conclusion

Mq64 represents a significant advancement in position-safe encoding for hierarchical embeddings. By combining the substring pollution protection of QuadB64 with the progressive refinement capabilities of Matryoshka embeddings, it enables new patterns of efficient, scalable vector search.

The specification provides a foundation for implementation across multiple programming languages and integration with existing vector search infrastructure, positioning uubed as the leading solution for next-generation embedding encoding challenges.

---

**Document Status**: Draft v1.0.0  
**Next Review**: After prototype implementation  
**Implementation Target**: Q2 2025