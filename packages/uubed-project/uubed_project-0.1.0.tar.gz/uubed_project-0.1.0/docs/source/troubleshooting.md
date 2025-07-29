# Troubleshooting Guide

This guide covers common issues and their solutions when using uubed.

## Installation Issues

### Problem: "No module named 'uubed._native'"

**Symptom**: ImportError when trying to use uubed after installation.

**Solution**:
```bash
# Ensure you have the latest pip
pip install --upgrade pip

# Reinstall uubed with proper wheel support
pip install --force-reinstall uubed
```

### Problem: Build fails on M1/M2 Macs

**Symptom**: Compilation errors during installation on Apple Silicon.

**Solution**:
```bash
# Install Rust if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Set the correct target
rustup target add aarch64-apple-darwin

# Install with maturin
pip install maturin
maturin develop --release
```

## Performance Issues

### Problem: Encoding is slower than expected

**Symptom**: Performance doesn't match benchmarks.

**Possible causes and solutions**:

1. **Native module not loaded**:
   ```python
   import uubed
   print(uubed._has_native)  # Should be True
   ```

2. **Debug build instead of release**:
   ```bash
   # Reinstall with release optimizations
   pip install --force-reinstall uubed
   ```

3. **Input data type issues**:
   ```python
   # Ensure proper data types
   import numpy as np
   embedding = np.array(data, dtype=np.float32)  # Use float32
   ```

## Encoding Issues

### Problem: "Invalid embedding values" error

**Symptom**: ValueError when encoding embeddings.

**Solution**:
```python
# Ensure values are in valid range [0, 255] for uint8
embedding = np.clip(embedding * 255, 0, 255).astype(np.uint8)
```

### Problem: Decoded embedding doesn't match original

**Symptom**: Round-trip encoding/decoding produces different values.

**Note**: Only Eq64 supports exact round-trip decoding. Other methods are lossy by design.

```python
# Use Eq64 for exact round-trip
encoded = encode(embedding, method="eq64")
decoded = decode(encoded)  # Only works with eq64
```

## Integration Issues

### Problem: Search engine still shows substring matches

**Symptom**: Despite using uubed, substring pollution persists.

**Solutions**:

1. **Ensure proper field configuration**:
   ```json
   // Elasticsearch mapping
   {
     "mappings": {
       "properties": {
         "embedding": {
           "type": "keyword",  // Not "text"
           "index": true
         }
       }
     }
   }
   ```

2. **Use exact match queries**:
   ```python
   # Use term query, not match query
   query = {"term": {"embedding": encoded_string}}
   ```

## Memory Issues

### Problem: High memory usage with large batches

**Symptom**: Memory errors when encoding many embeddings.

**Solution**:
```python
# Process in smaller batches
batch_size = 1000
for i in range(0, len(embeddings), batch_size):
    batch = embeddings[i:i+batch_size]
    encoded_batch = [encode(emb) for emb in batch]
    # Process batch...
```

## Common Error Messages

### "Embedding must be 1-dimensional"
Ensure your embedding is flattened:
```python
embedding = embedding.flatten()
```

### "Cannot encode NaN values"
Check for and handle NaN values:
```python
if np.isnan(embedding).any():
    embedding = np.nan_to_num(embedding, 0)
```

### "Incompatible alphabet at position X"
This indicates corrupted encoded data. Ensure encoded strings aren't modified.

## Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/twardoch/uubed/issues)
2. Review the [API documentation](api-reference.html)
3. Ask in [GitHub Discussions](https://github.com/twardoch/uubed/discussions)
4. File a bug report with:
   - Python version
   - uubed version
   - Minimal reproducible example
   - Full error traceback