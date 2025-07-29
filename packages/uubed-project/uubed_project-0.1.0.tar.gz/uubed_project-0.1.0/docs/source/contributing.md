# Contributing to uubed

Thank you for your interest in contributing to uubed! This guide will help you get started.

## Project Structure

The uubed project is organized across multiple repositories:

- **uubed** (main): Project coordination and documentation
- **uubed-rs**: Rust implementation
- **uubed-py**: Python bindings  
- **uubed-docs**: Documentation

## Getting Started

### 1. Fork and Clone

Fork the appropriate repository and clone it locally:

```bash
git clone https://github.com/YOUR_USERNAME/uubed.git
cd uubed
```

### 2. Set Up Development Environment

#### For Python Development (uubed-py):
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

#### For Rust Development (uubed-rs):
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build the project
cargo build --release

# Run tests
cargo test
```

### 3. Make Your Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards

3. Write or update tests

4. Update documentation if needed

### 4. Run Tests

#### Python:
```bash
uvx hatch test
# or
pytest tests/
```

#### Rust:
```bash
cargo test
cargo clippy
```

## Coding Standards

### Python Code Style
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Docstrings for all public functions

Example:
```python
def encode_embedding(
    data: np.ndarray,
    method: str = "eq64"
) -> str:
    """
    Encode an embedding vector to a position-safe string.
    
    Args:
        data: The embedding vector to encode
        method: Encoding method to use
        
    Returns:
        Position-safe encoded string
    """
    ...
```

### Rust Code Style
- Follow Rust formatting guidelines
- Use `cargo fmt` before committing
- Add documentation comments

Example:
```rust
/// Encode bytes using Q64 position-safe encoding
/// 
/// # Arguments
/// * `data` - The bytes to encode
/// 
/// # Returns
/// The encoded string
pub fn q64_encode(data: &[u8]) -> String {
    // Implementation
}
```

## Testing

### Writing Tests

Add tests for new features:

```python
# Python test example
def test_new_feature():
    result = new_feature(input_data)
    assert result == expected_output
```

```rust
// Rust test example
#[test]
fn test_new_feature() {
    let result = new_feature(&input_data);
    assert_eq!(result, expected_output);
}
```

### Performance Benchmarks

When adding performance-critical code:

1. Add benchmarks to track performance
2. Compare with existing implementations
3. Document performance characteristics

## Documentation

### Code Documentation
- All public APIs must have docstrings/doc comments
- Include examples in documentation
- Explain complex algorithms

### User Documentation
- Update relevant .md files in docs/
- Add examples for new features
- Update the API reference

## Pull Request Process

1. **Before submitting:**
   - Ensure all tests pass
   - Run linters and formatters
   - Update documentation
   - Add entry to CHANGELOG.md

2. **PR Description:**
   - Clearly describe the changes
   - Reference any related issues
   - Include benchmark results if relevant

3. **Review Process:**
   - Address reviewer feedback promptly
   - Keep PRs focused and manageable
   - Be patient and respectful

## Reporting Issues

When reporting issues:

1. Search existing issues first
2. Use issue templates
3. Provide:
   - Clear description
   - Minimal reproducible example
   - System information
   - Error messages/tracebacks

## Development Workflow

### For Cross-Repository Changes

If your change affects multiple repositories:

1. Create branches in all affected repos
2. Submit PRs in dependency order (rs → py → docs)
3. Link related PRs in descriptions

### Release Process

Releases follow semantic versioning:
- MAJOR: Breaking API changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes

## Community

- Be respectful and inclusive
- Follow the Code of Conduct
- Help others in discussions
- Share your use cases

## Getting Help

- GitHub Discussions for questions
- Issues for bugs/features
- Development chat (if available)

Thank you for contributing to uubed!