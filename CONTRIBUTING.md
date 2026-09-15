# Contributing

Contributions are welcome! Please follow these guidelines.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Types of Contributions

### Bug Reports
- Use GitHub issues
- Describe the bug clearly
- Include reproduction steps
- Add error messages and logs

### Feature Requests
- Use GitHub issues with [FEATURE] prefix
- Explain the use case
- Describe expected behavior

### Code Improvements
- Better scoring algorithm
- Improved keyword extraction
- Performance optimizations
- Better error handling
- Additional tests

## Development Setup

See [SETUP.md](docs/SETUP.md) for full setup instructions.

## Code Style

- Python: Follow PEP 8
- Bash: Use shellcheck
- Markdown: Use 2 spaces for indentation

## Testing

Test locally before submitting PR:
```bash
./scripts/deploy_function.sh
./scripts/create_agent.sh
# Test with sample resumes
```

## Documentation

Update docs if you change:
- Architecture or design
- API endpoints
- Configuration options
- Deployment process

---

Thank you for contributing!
