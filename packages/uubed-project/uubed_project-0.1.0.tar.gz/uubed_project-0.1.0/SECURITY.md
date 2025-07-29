# Security Policy

## Supported Versions

We actively support security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| 0.x.x   | :x:                |

## Reporting a Vulnerability

The uubed team takes security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do NOT create a public issue

Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report privately

Send an email to: **security@uubed.dev** (if available) or create a [private vulnerability report](https://github.com/twardoch/uubed/security/advisories/new) on GitHub.

Include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Affected versions
- Potential impact
- Any suggested fixes (if available)

### 3. Response timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Depends on severity, typically 30-90 days

## Security Considerations

### Input Validation

uubed processes binary data and embedding vectors. While the library is designed to be safe, consider these best practices:

- **Validate input sizes**: Ensure embedding dimensions are within expected ranges
- **Sanitize encoded strings**: When using encoded output in search queries, apply appropriate escaping
- **Rate limiting**: In production systems, implement rate limiting for encoding operations

### Memory Safety

- **Rust core**: The core implementation in Rust provides memory safety guarantees
- **Python bindings**: PyO3 bindings include bounds checking and safe memory management
- **Large inputs**: Be aware of memory usage with very large embeddings or batch operations

### Cryptographic Considerations

**Important**: uubed is NOT a cryptographic library. The encoding schemes are designed for efficiency and substring pollution prevention, not security:

- **Not for secrets**: Never use uubed to encode sensitive information like passwords or API keys
- **Not tamper-proof**: Encoded strings can be modified; use proper authentication for integrity
- **Not for encryption**: The encoding is reversible and provides no confidentiality

### Supply Chain Security

We follow these practices to ensure supply chain security:

- **Dependency auditing**: Regular security audits of all dependencies
- **Reproducible builds**: Deterministic build processes
- **Signed releases**: All releases are signed and verified
- **Minimal dependencies**: We minimize external dependencies

## Security Best Practices for Users

### Deployment

1. **Version management**: Keep uubed updated to the latest stable version
2. **Dependency scanning**: Regularly scan your dependencies for vulnerabilities
3. **Input validation**: Validate all inputs before processing
4. **Error handling**: Implement proper error handling to avoid information leakage

### Integration Security

1. **Search query safety**: When using encoded strings in search queries:
   ```python
   # Good - parameterized query
   cursor.execute("SELECT * FROM docs WHERE embedding_code = %s", (encoded,))
   
   # Bad - string concatenation (SQL injection risk)
   cursor.execute(f"SELECT * FROM docs WHERE embedding_code = '{encoded}'")
   ```

2. **API security**: When exposing uubed functionality via APIs:
   - Implement proper authentication and authorization
   - Apply rate limiting to prevent abuse
   - Validate and sanitize all inputs
   - Use HTTPS for all communications

3. **Data handling**: 
   - Don't log sensitive embeddings or encoded data
   - Implement proper access controls for encoded data
   - Consider encryption at rest for sensitive applications

## Known Security Considerations

### Resource Exhaustion

- **Large batch operations**: Very large batch encoding operations may consume significant memory
- **Mitigation**: Implement appropriate limits on batch sizes and concurrent operations

### Information Disclosure

- **Timing attacks**: Encoding time may vary based on input characteristics
- **Mitigation**: For security-sensitive applications, consider constant-time requirements

### Dependencies

We regularly monitor our dependencies for security vulnerabilities:

- **Rust dependencies**: Tracked via `cargo audit`
- **Python dependencies**: Tracked via security scanners
- **Build tools**: Keep toolchain updated

## Acknowledgments

We appreciate responsible disclosure of security vulnerabilities. Contributors who report valid security issues will be:

- Credited in our security advisories (with their permission)
- Listed in our CHANGELOG for the fix release
- Invited to join our security advisory team for future reviews

## Questions?

If you have questions about this security policy or need clarification on security practices, please contact us through our [GitHub Discussions](https://github.com/twardoch/uubed/discussions) for general security questions, or privately via email for sensitive matters.