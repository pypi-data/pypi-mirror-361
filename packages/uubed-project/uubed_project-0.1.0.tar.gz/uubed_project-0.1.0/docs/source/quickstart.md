# Quick Start Guide

Get up and running with uubed in minutes!

## Installation

Install uubed from PyPI:

```bash
pip install uubed
```

## Basic Usage

### 1. Simple Encoding

```python
import numpy as np
from uubed import encode

# Create a sample embedding (e.g., from OpenAI, Cohere, etc.)
embedding = np.random.rand(384).astype(np.float32)

# Convert to uint8 range [0, 255]
embedding_uint8 = (embedding * 255).astype(np.uint8)

# Encode with automatic method selection
encoded = encode(embedding_uint8)
print(f"Encoded: {encoded[:50]}...")
```

### 2. Choosing Encoding Methods

```python
# Full precision (best for exact search)
encoded_full = encode(embedding_uint8, method="eq64")

# SimHash (best for similarity search)
encoded_sim = encode(embedding_uint8, method="shq64")

# Top-k features (best for sparse embeddings)
encoded_topk = encode(embedding_uint8, method="t8q64")

# Z-order (best for range queries)
encoded_spatial = encode(embedding_uint8, method="zoq64")
```

### 3. Round-trip Encoding/Decoding

Only Eq64 supports exact round-trip:

```python
from uubed import encode, decode

# Encode
encoded = encode(embedding_uint8, method="eq64")

# Decode back to bytes
decoded_bytes = decode(encoded)

# Convert back to array
decoded_array = np.frombuffer(decoded_bytes, dtype=np.uint8)

# Verify
assert np.array_equal(embedding_uint8, decoded_array)
```

## Integration Examples

### With Elasticsearch

```python
from elasticsearch import Elasticsearch
from uubed import encode

es = Elasticsearch()

# Index an embedding
doc = {
    "text": "Example document",
    "embedding": encode(embedding_uint8, method="shq64")
}

es.index(index="embeddings", body=doc)

# Search by embedding
query_embedding = encode(query_vector, method="shq64")
results = es.search(
    index="embeddings",
    body={
        "query": {
            "term": {
                "embedding": query_embedding
            }
        }
    }
)
```

### With Redis

```python
import redis
from uubed import encode

r = redis.Redis()

# Store embedding
embedding_key = encode(embedding_uint8, method="zoq64")
r.set(f"embedding:{doc_id}", embedding_key)

# Retrieve by exact match
stored_key = r.get(f"embedding:{doc_id}")
```

### With PostgreSQL

```python
import psycopg2
from uubed import encode

conn = psycopg2.connect("dbname=vectors")
cur = conn.cursor()

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id SERIAL PRIMARY KEY,
        doc_text TEXT,
        embedding VARCHAR(100)
    )
""")

# Insert embedding
encoded = encode(embedding_uint8, method="eq64")
cur.execute(
    "INSERT INTO embeddings (doc_text, embedding) VALUES (%s, %s)",
    (document_text, encoded)
)

# Query by exact match
cur.execute(
    "SELECT * FROM embeddings WHERE embedding = %s",
    (query_encoded,)
)
```

## Batch Processing

For processing many embeddings efficiently:

```python
from uubed import encode
import numpy as np

# Batch of embeddings
embeddings = np.random.rand(1000, 384).astype(np.float32)
embeddings_uint8 = (embeddings * 255).astype(np.uint8)

# Encode all embeddings
encoded_batch = [
    encode(emb, method="shq64") 
    for emb in embeddings_uint8
]

# Process with multiprocessing for large batches
from multiprocessing import Pool

def encode_wrapper(emb):
    return encode(emb, method="shq64")

with Pool() as pool:
    encoded_batch = pool.map(encode_wrapper, embeddings_uint8)
```

## Performance Tips

1. **Use Native Acceleration**: Ensure the Rust module is loaded:
   ```python
   import uubed
   print(f"Native acceleration: {uubed._has_native}")
   ```

2. **Choose the Right Method**:
   - `eq64`: When you need exact matches and full precision
   - `shq64`: For similarity search with good compression
   - `t8q64`: For sparse embeddings or feature analysis
   - `zoq64`: For spatial queries or maximum compression

3. **Batch Operations**: Process multiple embeddings together

4. **Pre-process Data**: Convert to uint8 once and reuse

## Common Patterns

### Caching Embeddings

```python
from functools import lru_cache
from uubed import encode

@lru_cache(maxsize=10000)
def get_cached_encoding(embedding_bytes):
    return encode(embedding_bytes, method="shq64")
```

### Similarity Search

```python
def find_similar(query_embedding, database_embeddings, threshold=0.9):
    query_encoded = encode(query_embedding, method="shq64")
    
    similar = []
    for idx, db_encoded in enumerate(database_embeddings):
        if query_encoded == db_encoded:  # Exact match for shq64
            similar.append(idx)
    
    return similar
```

## Next Steps

- Read the [API Reference](api-reference.html) for detailed documentation
- Check [Troubleshooting](troubleshooting.html) if you encounter issues
- See [Examples](https://github.com/twardoch/uubed/tree/main/examples) for more use cases