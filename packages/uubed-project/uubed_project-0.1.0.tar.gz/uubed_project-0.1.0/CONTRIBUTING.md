# Contributing to uubed

Thank you for your interest in contributing to the uubed project! This guide will help you understand how to contribute effectively across our multi-repository structure.

## Project Structure

The uubed project is organized into four main repositories:

- **[uubed](https://github.com/twardoch/uubed)** - Project home, coordination, and high-level documentation
- **[uubed-rs](https://github.com/twardoch/uubed-rs)** - Rust implementation (core performance-critical code)
- **[uubed-py](https://github.com/twardoch/uubed-py)** - Python bindings and high-level API
- **[uubed-docs](https://github.com/twardoch/uubed-docs)** - Documentation and technical book

## Where to Contribute

### Bug Reports and Feature Requests

- **Rust implementation issues** → [uubed-rs/issues](https://github.com/twardoch/uubed-rs/issues)
- **Python API issues** → [uubed-py/issues](https://github.com/twardoch/uubed-py/issues)
- **Documentation issues** → [uubed-docs/issues](https://github.com/twardoch/uubed-docs/issues)
- **Cross-cutting concerns** → [uubed/issues](https://github.com/twardoch/uubed/issues)

### Code Contributions

1. **Rust Core Development**
   - Performance optimizations
   - New encoding schemes
   - SIMD implementations
   - Repository: [uubed-rs](https://github.com/twardoch/uubed-rs)

2. **Python Development**
   - API improvements
   - Integration with ML frameworks
   - CLI enhancements
   - Repository: [uubed-py](https://github.com/twardoch/uubed-py)

3. **Documentation**
   - API documentation
   - Tutorials and examples
   - Technical explanations
   - Repository: [uubed-docs](https://github.com/twardoch/uubed-docs)

## Getting Started

### Prerequisites

- **For Rust development**: Rust 1.70+ with cargo
- **For Python development**: Python 3.8+ with pip
- **For documentation**: Node.js for MkDocs toolchain

### Development Setup

1. Fork the appropriate repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/uubed-COMPONENT.git
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Making Changes

1. Follow the coding style of the existing codebase
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation as needed
5. Keep commits focused and write clear commit messages

### Testing

- **Rust**: Run `cargo test` in uubed-rs
- **Python**: Run `pytest` in uubed-py
- **Docs**: Build locally with `mkdocs serve`

### Submitting Pull Requests

1. Push your changes to your fork
2. Create a pull request against the `main` branch
3. Fill out the PR template completely
4. Wait for CI checks to pass
5. Address review feedback promptly

## Code Style

### Rust
- Follow standard Rust formatting (`cargo fmt`)
- Use `cargo clippy` for linting
- Write idiomatic Rust code

### Python
- Follow PEP 8
- Use type hints where appropriate
- Format with `black` and lint with `ruff`

### Documentation
- Use clear, concise language
- Include code examples
- Follow the existing documentation structure

## Performance Considerations

Since uubed is a performance-critical library:

- Benchmark your changes using the existing benchmark suite
- Consider memory usage and allocation patterns
- Profile code for bottlenecks
- Document any performance implications

## Community

- Be respectful and follow our [Code of Conduct](CODE_OF_CONDUCT.md)
- Help others in issues and discussions
- Share your use cases and feedback

## Questions?

If you're unsure where to start or have questions:

1. Check existing issues and discussions
2. Open a discussion in the main [uubed repository](https://github.com/twardoch/uubed/discussions)
3. Reach out to maintainers via GitHub

Thank you for contributing to make uubed better!