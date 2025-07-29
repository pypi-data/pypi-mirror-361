# uubed - High-Performance Position-Safe Embeddings

[![Orchestrate Builds](https://github.com/twardoch/uubed/actions/workflows/orchestrate-builds.yml/badge.svg)](https://github.com/twardoch/uubed/actions/workflows/orchestrate-builds.yml)
[![PyPI](https://img.shields.io/pypi/v/uubed.svg)](https://pypi.org/project/uubed/)
[![Crates.io](https://img.shields.io/crates/v/uubed.svg)](https://crates.io/crates/uubed)
[![Python Version](https://img.shields.io/pypi/pyversions/uubed.svg)](https://pypi.org/project/uubed/)
[![License](https://img.shields.io/github/license/twardoch/uubed.svg)](https://github.com/twardoch/uubed/blob/main/LICENSE)

**uubed** (pronounced "you-you-bed") is a high-performance library for encoding embedding vectors into position-safe strings that solve the "substring pollution" problem in search systems.

## 🏗️ Project Structure

This is the main repository for the uubed project. The implementation is split across multiple repositories:

- **[uubed](https://github.com/twardoch/uubed)** (this repo) - Project coordination and documentation
- **[uubed-rs](https://github.com/twardoch/uubed-rs)** - High-performance Rust implementation
- **[uubed-py](https://github.com/twardoch/uubed-py)** - Python bindings and API
- **[uubed-docs](https://github.com/twardoch/uubed-docs)** - Comprehensive documentation and book

## 🚀 Key Features

- **Position-Safe Encoding**: QuadB64 family prevents false substring matches
- **Blazing Fast**: 40-105x faster than pure Python with Rust acceleration
- **Multiple Encoding Methods**: Full precision, SimHash, Top-k, Z-order
- **Search Engine Friendly**: No more substring pollution in Elasticsearch/Solr
- **Easy Integration**: Simple API, works with any vector database

## 📊 Performance

With native Rust acceleration:
- **Eq64 encoding**: 40-105x speedup (>230 MB/s throughput)
- **Shq64 (SimHash)**: 1.7-9.7x faster with parallel processing  
- **Zoq64 (Z-order)**: 60-1600x faster with efficient bit manipulation
- **T8q64 (Top-k)**: Optimized sparse vector handling

### Benchmark Results

<details>
<summary>Performance comparison (click to expand)</summary>

```
Embedding Size: 1024 bytes (256 dimensions × 4 bytes)
Hardware: Apple M1 Pro / Intel i7-9750H
=====================================
Method    Implementation    Time (μs)    Throughput (MB/s)    Speedup
---------------------------------------------------------------------
Eq64      Pure Python       464.82       2.20                 1.0x
Eq64      Native Rust       4.37         234.42               105.4x

Shq64     Pure Python       1431.33      0.72                 1.0x  
Shq64     Native Rust       139.79       7.33                 10.2x

Zoq64     Pure Python       73.59        13.91                1.0x
Zoq64     Native Rust       0.63         1631.92              116.8x

T8q64     Pure Python       892.45       1.15                 1.0x
T8q64     Native Rust       42.18        24.31                21.2x
```

</details>

## Installation

Install the latest release from PyPI:

```bash
pip install uubed
```

Or, to install the latest development version from this repository:

```bash
pip install git+https://github.com/twardoch/uubed.git
```

## Development

To set up a development environment, you will need Python 3.10+ and Rust.

1.  Clone the repository:

    ```bash
    git clone https://github.com/twardoch/uubed.git
    cd uubed
    ```

2.  Create a virtual environment:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Install the package in editable mode:

    ```bash
    maturin develop
    ```

4.  Run the tests:

    ```bash
    pytest
    ```


## 🎯 Quick Start

```python
import numpy as np
from uubed import encode, decode

# Create an embedding
embedding = np.random.randint(0, 256, 256, dtype=np.uint8)

# Full precision encoding
full_code = encode(embedding, method="eq64")
print(f"Full: {full_code[:50]}...")  # AQgxASgz...

# Compact similarity hash
compact_code = encode(embedding, method="shq64")
print(f"Compact: {compact_code}")  # 16 chars preserving similarity

# Decode back to original
decoded = decode(full_code)
assert np.array_equal(embedding, np.frombuffer(decoded, dtype=np.uint8))
```

## 🧩 Encoding Methods

### Eq64 - Full Embeddings
- **Use case**: Need exact values
- **Size**: 2 chars per byte
- **Features**: Lossless, supports decode

### Shq64 - SimHash  
- **Use case**: Fast similarity search
- **Size**: 16 characters (64-bit hash)
- **Features**: Preserves cosine similarity

### T8q64 - Top-k Indices
- **Use case**: Sparse representations
- **Size**: 16 characters (8 indices)
- **Features**: Captures most important dimensions

### Zoq64 - Z-order
- **Use case**: Spatial/prefix search
- **Size**: 8 characters
- **Features**: Nearby points share prefixes

## 💡 Why QuadB64?

### The Problem
Regular Base64 encoding in search engines causes **substring pollution**:

<img src="https://github.com/twardoch/uubed/assets/123456/substring-pollution-diagram.png" alt="Substring Pollution Problem" width="600">

```python
# Regular Base64
encode("Hello") → "SGVsbG8="
search("Vsb") → Matches! (false positive)
```

### The Solution  
QuadB64 uses position-dependent alphabets:

<img src="https://github.com/twardoch/uubed/assets/123456/quadb64-solution-diagram.png" alt="QuadB64 Solution" width="600">

```python
# QuadB64
encode("Hello") → "EYm1.Gcm8"  # Note the dot separator
search("Ym1") → No match (different positions use different alphabets)
```

Position-safe alphabets:
- Position 0,4,8...: `ABCDEFGHIJKLMNOP`
- Position 1,5,9...: `QRSTUVWXYZabcdef`
- Position 2,6,10..: `ghijklmnopqrstuv`
- Position 3,7,11..: `wxyz0123456789-_`

The dot separator every 4 characters ensures position alignment and prevents arbitrary substring matches.

## 🔌 Integration Examples

### With Elasticsearch
```python
# Index embeddings without substring pollution
doc = {
    "id": "123",
    "embedding_code": encode(embedding, method="eq64")
}

# Search works correctly - no false matches
es.search(body={
    "query": {"term": {"embedding_code": target_code}}
})
```

### With Vector Databases
```python
# Store with Pinecone/Weaviate/Qdrant
encoded = encode(embedding, method="shq64")
index.upsert(
    id="doc123",
    values=embedding.tolist(),
    metadata={"q64_code": encoded}
)
```

## 🛠️ Development

```bash
# Setup development environment
pip install hatch
hatch shell

# Run tests
hatch test

# Run benchmarks
python benchmarks/bench_encoders.py

# Build native module
maturin develop --release
```

## 📈 Latest Benchmarks

Performance tests run nightly via GitHub Actions. View the [latest benchmark results](https://github.com/twardoch/uubed/actions/workflows/nightly-benchmarks.yml).

### Memory Efficiency

<details>
<summary>Memory usage comparison (click to expand)</summary>

```
Method      Input Size    Encoded Size    Compression    Memory Overhead
------------------------------------------------------------------------
Eq64        1024 bytes    2048 chars      2.0x           < 1%
Shq64       1024 bytes    16 chars        0.016x         < 1%
T8q64       1024 bytes    16 chars        0.016x         < 1%
Zoq64       1024 bytes    8 chars         0.008x         < 1%
```

</details>

## 🤝 Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [PyO3](https://pyo3.rs/) - Rust bindings for Python
- [Maturin](https://maturin.rs/) - Build and publish Rust Python extensions
- [Rayon](https://github.com/rayon-rs/rayon) - Data parallelism for Rust

## 📚 Learn More

- [Quick Start Guide](docs/quickstart.md)
- [API Reference](docs/api.md)
- [Performance Guide](docs/performance.md)
- [Architecture](docs/architecture.md)