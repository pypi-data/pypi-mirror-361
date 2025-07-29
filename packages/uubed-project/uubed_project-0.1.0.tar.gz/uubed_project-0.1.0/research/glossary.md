# uubed Glossary

A living glossary of terms, concepts, and technical definitions used throughout the uubed project.

## Core Concepts

### QuadB64
The family of position-safe Base64 encoding variants developed for the uubed project. Unlike standard Base64, QuadB64 encodings preserve locality and avoid substring pollution in search engines.

### Substring Pollution
The problem where encoded data fragments appear as false positives in search results because they match partial queries. Standard Base64 encoding is particularly susceptible to this issue.

### Position-Safe Encoding
An encoding scheme where the position of a character within the encoded string affects its value, preventing arbitrary substrings from being valid encodings.

## Encoding Variants

### Eq64 (Embeddings QuadB64)
The primary encoding scheme for full embedding vectors. Uses dot separators every 4 characters to ensure position safety. Optimized for dense vector representations.

### Shq64 (SimHash QuadB64)
A variant designed for SimHash fingerprints and other binary hash representations. Provides compact encoding while maintaining searchability properties.

### T8q64 (Top-k QuadB64)
Specialized encoding for top-k sparse representations where only the indices and values of the k largest components are stored.

### Zoq64 (Z-order QuadB64)
Encoding variant using Z-order (Morton) encoding for spatial data and multi-dimensional indices. Preserves locality across dimensions.

## Technical Terms

### SIMD (Single Instruction, Multiple Data)
Parallel processing technique used in uubed for accelerating encoding/decoding operations. Implementations include AVX2, AVX-512, and NEON.

### FFI (Foreign Function Interface)
The interface layer that allows the Rust core to be called from other languages, primarily Python via PyO3.

### Locality Preservation
The property of an encoding scheme where similar inputs produce similar encoded outputs, maintaining neighborhood relationships.

### Matryoshka Embeddings
Nested embedding representations where earlier dimensions contain more important information. Future uubed versions will support specialized encoding for these structures.

## Performance Terms

### Vectorization
The process of converting sequential operations into parallel SIMD operations for improved performance.

### Zero-Copy Operations
Data processing techniques that avoid unnecessary memory allocations and copies, crucial for high-performance encoding.

### Batch Processing
Encoding or decoding multiple vectors simultaneously to amortize overhead and improve throughput.

## Implementation Details

### PyO3
The Rust library used to create Python bindings for the uubed-rs core implementation.

### Base Encoding Alphabet
The 64-character set used for encoding: `A-Z`, `a-z`, `0-9`, `+`, `/` (with `=` for padding in standard Base64).

### Chunk Size
The number of bytes processed as a unit during encoding. QuadB64 uses 4-character chunks with position markers.

## Search and Retrieval

### Vector Database
Specialized databases (Pinecone, Weaviate, Qdrant) optimized for storing and searching high-dimensional vectors, primary use case for uubed encodings.

### Cosine Similarity
Common similarity metric for comparing embedding vectors, preserved by uubed's locality-preserving encodings.

### Approximate Nearest Neighbor (ANN)
Search algorithms that find similar vectors efficiently, benefiting from uubed's locality preservation properties.

---

*This glossary is continuously updated as the project evolves. Contributions and clarifications are welcome via pull requests.*