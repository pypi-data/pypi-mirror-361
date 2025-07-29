# uubed v{VERSION} Release Template

Use this template for creating blog-style release posts when publishing new versions.

## Release Post Title
```
🚀 uubed v{VERSION}: {MAJOR_HIGHLIGHT}
```

## Release Post Structure

### Opening
```markdown
We're excited to announce the release of uubed v{VERSION}! This release brings {BRIEF_SUMMARY}.

## 🎉 What's New

### {FEATURE_CATEGORY_1}
- **{Feature Name}**: {Brief description and benefit}
- **{Feature Name}**: {Brief description and benefit}

### {FEATURE_CATEGORY_2}  
- **{Feature Name}**: {Brief description and benefit}

## 📈 Performance Improvements

{Include any performance benchmarks or improvements}

## 🔧 Breaking Changes

{List any breaking changes and migration guidance}

## 🐛 Bug Fixes

{List important bug fixes}

## 📦 Installation

Install the latest version:

```bash
# Python
pip install uubed=={VERSION}

# Rust
cargo add uubed@{VERSION}
```

## 🙏 Contributors

Thanks to all contributors who made this release possible:
{List contributors}

## 🔗 Links

- [Full Changelog](https://github.com/twardoch/uubed/blob/main/CHANGELOG.md)
- [Documentation](https://uubed.readthedocs.io/)
- [PyPI Package](https://pypi.org/project/uubed/{VERSION}/)
- [Crates.io Package](https://crates.io/crates/uubed/{VERSION})

---

Have questions or feedback? Join the discussion in our [GitHub Discussions](https://github.com/twardoch/uubed/discussions)!
```

## Example Release Post

### 🚀 uubed v1.1.0: SIMD Acceleration & Matryoshka Support

We're excited to announce the release of uubed v1.1.0! This release brings significant performance improvements through SIMD acceleration and introduces experimental support for Matryoshka embeddings.

## 🎉 What's New

### Performance Enhancements
- **SIMD Acceleration**: AVX2 and NEON implementations provide 2-4x speedup on compatible hardware
- **Memory Optimization**: Reduced memory footprint by 30% for large batch operations
- **Parallel Processing**: Enhanced multi-threading for batch encoding operations

### New Features
- **Matryoshka Embeddings**: Experimental support for nested embedding representations
- **Streaming API**: Process large datasets without loading everything into memory
- **Custom Alphabets**: Configure position-safe alphabets for domain-specific needs

## 📈 Performance Improvements

```
Benchmark: 1000 embeddings (1024 bytes each)
Hardware: Apple M1 Pro

Method    v1.0.x     v1.1.0     Improvement
------------------------------------------
Eq64      45ms       12ms       3.75x faster
Shq64     156ms      89ms       1.75x faster
T8q64     78ms       34ms       2.29x faster
```

## 🔧 Breaking Changes

- `encode()` function now requires explicit `method` parameter
- Removed deprecated `q64_encode()` function (use `encode(method="eq64")`)

## 🐛 Bug Fixes

- Fixed edge case in Z-order encoding for sparse vectors
- Resolved memory leak in Python bindings during batch operations
- Corrected position alphabet validation for custom schemes

## 📦 Installation

Install the latest version:

```bash
# Python
pip install uubed==1.1.0

# Rust  
cargo add uubed@1.1.0
```

## 🙏 Contributors

Thanks to all contributors who made this release possible:
- @contributor1 - SIMD implementations
- @contributor2 - Matryoshka embedding support  
- @contributor3 - Documentation improvements

## 🔗 Links

- [Full Changelog](https://github.com/twardoch/uubed/blob/main/CHANGELOG.md)
- [Documentation](https://uubed.readthedocs.io/)
- [PyPI Package](https://pypi.org/project/uubed/1.1.0/)
- [Crates.io Package](https://crates.io/crates/uubed/1.1.0)

---

Have questions or feedback? Join the discussion in our [GitHub Discussions](https://github.com/twardoch/uubed/discussions)!