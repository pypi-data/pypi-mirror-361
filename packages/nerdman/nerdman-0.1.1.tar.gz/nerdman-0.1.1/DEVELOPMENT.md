# Development Guide for NerdMan

## Quick Start for Development

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/nerdman.git
cd nerdman
```

### 2. Install in Development Mode

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or using make
make install-dev
```

### 3. Run Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test
python -m pytest tests/test_nerdman.py::TestNerdManBasics::test_import_success -v
```

### 4. Format and Lint

```bash
# Format code
make format

# Run linting
make lint
```

## Building and Distribution

### 1. Build the Package

```bash
# Clean previous builds and create new distribution
make dist

# Or step by step:
make clean
make build
make check-dist
```

### 2. Test Installation Locally

```bash
# Install from local wheel
pip install dist/nerdman-*.whl

# Test the CLI
nerdman version
nerdman demo
```

### 3. Upload to Test PyPI

```bash
# First, register at https://test.pypi.org/
# Configure your credentials with twine

make upload-test
```

### 4. Upload to PyPI

```bash
# Register at https://pypi.org/
make upload
```

## Project Structure

```plaintext
nerdman/
├── nerdman.py          # Main module
├── setup.py            # Setup script (legacy)
├── pyproject.toml      # Modern Python packaging
├── README.md           # Documentation
├── LICENSE             # MIT License
├── CHANGELOG.md        # Version history
├── requirements.txt    # Dependencies (empty - stdlib only)
├── MANIFEST.in         # Include/exclude files for distribution
├── Makefile            # Development commands
├── .gitignore          # Git ignore patterns
├── tests/              # Test suite
│   ├── __init__.py
│   └── test_nerdman.py
└── docs/               # Documentation (future)
```

## Available Make Commands

- `make help` - Show available commands
- `make install` - Install package in development mode
- `make install-dev` - Install with development dependencies
- `make test` - Run test suite
- `make test-coverage` - Run tests with coverage report
- `make lint` - Run code linting
- `make format` - Format code with black
- `make clean` - Clean build artifacts
- `make build` - Build distribution packages
- `make check-dist` - Validate distribution packages
- `make upload-test` - Upload to Test PyPI
- `make upload` - Upload to PyPI
- `make dist` - Clean, build, and check (full release prep)
- `make demo` - Run the interactive demo
- `make cheat` - Generate HTML cheatsheet
- `make version` - Show version information
- `make update` - Update Nerd Fonts data

## Testing

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_nerdman.py -v

# Test with coverage
python -m pytest tests/ --cov=nerdman --cov-report=html
```

### Writing Tests

- Tests are in the `tests/` directory
- Use unittest or pytest frameworks
- Test files should start with `test_`
- Set `NERDMAN_TEST_MODE=1` to avoid interactive prompts

## Code Style

### Formatting

- Use `black` for code formatting: `make format`
- Line length: 88 characters
- Target Python 3.7+ compatibility

### Linting

- Use `flake8` for style checking: `make lint`
- Use `mypy` for type checking
- Follow PEP 8 guidelines

## Release Process

1. **Update Version**: Update version in comments/strings in `nerdman.py`
2. **Update Changelog**: Add entries to `CHANGELOG.md`
3. **Test Thoroughly**: Run `make test` and manual testing
4. **Build Package**: Run `make dist`
5. **Test on Test PyPI**: Run `make upload-test` and test installation
6. **Release**: Run `make upload`
7. **Tag Release**: Create git tag for the version

## Continuous Integration

Consider setting up GitHub Actions or similar CI/CD with:

- Automated testing on multiple Python versions
- Code quality checks
- Automated publishing to PyPI on tags
- Documentation building

## Dependencies

NerdMan intentionally has **zero external dependencies** and uses only Python's standard library. This design choice ensures:

- Fast installation
- Minimal compatibility issues
- Easy distribution
- Reduced security surface area

## Platform Support

The package is designed to work on:

- Windows (PowerShell, CMD)
- macOS (Terminal, iTerm2)  
- Linux (Bash, Zsh, Fish)
- Python 3.7+

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the right directory and have installed the package
2. **Config Prompts**: Set `NERDMAN_TEST_MODE=1` for automated testing
3. **Unicode Issues**: Ensure your terminal supports Unicode characters
4. **Network Issues**: Some features require internet access for updates

### Debug Mode

```bash
# Run with verbose output
python -v nerdman.py demo

# Test individual functions
python -c "import nerdman; print(nerdman.get_icon_count())"
```
