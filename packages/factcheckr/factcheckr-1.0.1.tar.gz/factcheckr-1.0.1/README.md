# FactCheckr 🔍

A powerful AI-powered fact-checking tool that helps you verify claims and statements with confidence scores and detailed evidence.

[![PyPI version](https://badge.fury.io/py/factcheckr.svg)](https://badge.fury.io/py/factcheckr)
[![Python Support](https://img.shields.io/pypi/pyversions/factcheckr.svg)](https://pypi.org/project/factcheckr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/factcheckr/workflows/Tests/badge.svg)](https://github.com/yourusername/factcheckr/actions)

## Features

- 🤖 **AI-Powered Analysis**: Uses advanced AI models to fact-check claims
- 📊 **Confidence Scoring**: Provides confidence levels for each fact-check
- 📝 **Detailed Evidence**: Returns comprehensive evidence and reasoning
- 🔄 **Fallback System**: Robust fallback for common claims when AI is unavailable
- 💻 **Cross-Platform**: Works on Windows, macOS, and Linux
- 🎯 **Multiple Input Methods**: Command-line, interactive mode, and stdin support
- 📋 **JSON Output**: Machine-readable output format available
- 🚀 **Easy Installation**: Available on PyPI with simple pip install

## Quick Start

### Installation

#### From PyPI (Recommended)
```bash
pip install factcheckr
```

#### From GitHub
```bash
pip install git+https://github.com/yourusername/factcheckr.git
```

#### Development Installation
```bash
git clone https://github.com/yourusername/factcheckr.git
cd factcheckr
pip install -e .
```

### Basic Usage

#### Command Line
```bash
# Check a single claim
factcheckr "The Earth is round"

# Alternative syntax
python -m factcheckr "Cats have 9 lives"

# Get JSON output
factcheckr "Water boils at 100°C" --json

# Interactive mode
factcheckr --interactive

# Read from stdin
echo "The moon is made of cheese" | factcheckr --stdin

# Verbose output
factcheckr "Birds can fly" --verbose
```

#### Python API
```python
from factcheckr import CompleteFactCheckr

# Initialize the fact checker
checker = CompleteFactCheckr()

# Check a claim
result = checker.fact_check_with_ai("The Earth is flat")
print(f"Verdict: {result['verdict']}")
print(f"Evidence: {result['evidence']}")
print(f"Confidence: {result['confidence']}")
```

## Installation Verification

After installation, verify that FactCheckr is working correctly:

```bash
# Check version
factcheckr --version

# Test with a simple claim
factcheckr "Water is wet"

# Test JSON output
factcheckr "The sky is blue" --json
```

## Command Line Options

```
usage: factcheckr [-h] [--version] [--interactive] [--stdin] [--json] [--verbose] [claim]

AI-powered fact-checking tool

positional arguments:
  claim          The claim to fact-check

options:
  -h, --help     show this help message and exit
  --version      show program's version number and exit
  --interactive  Enter interactive mode
  --stdin        Read claims from stdin
  --json         Output results in JSON format
  --verbose      Enable verbose output
```

## Output Format

### Standard Output
```
Claim: "The Earth is round"
Verdict: True
Evidence: The Earth is an oblate spheroid, confirmed by satellite imagery, physics, and centuries of scientific observation.
Confidence: 0.95
```

### JSON Output
```json
{
  "claim": "The Earth is round",
  "verdict": "True",
  "evidence": "The Earth is an oblate spheroid, confirmed by satellite imagery, physics, and centuries of scientific observation.",
  "confidence": 0.95
}
```

## Platform-Specific Instructions

### Windows
```cmd
# Using Command Prompt
pip install factcheckr
factcheckr "Your claim here"

# Using PowerShell
pip install factcheckr
factcheckr "Your claim here"
```

### macOS
```bash
# Using Homebrew Python (recommended)
brew install python
pip3 install factcheckr
factcheckr "Your claim here"

# Using system Python
python3 -m pip install factcheckr
python3 -m factcheckr "Your claim here"
```

### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip
pip3 install factcheckr
factcheckr "Your claim here"

# CentOS/RHEL/Fedora
sudo yum install python3-pip  # or dnf on newer versions
pip3 install factcheckr
factcheckr "Your claim here"
```

## Troubleshooting

### Common Issues

#### "Command not found" Error
If you get a "command not found" error, try:

1. **Use the module syntax**:
   ```bash
   python -m factcheckr "Your claim"
   ```

2. **Check your PATH** (add Python Scripts directory):
   - **Windows**: Add `%APPDATA%\Python\Python3x\Scripts` to PATH
   - **macOS/Linux**: Add `~/.local/bin` to PATH

3. **Reinstall with user flag**:
   ```bash
   pip install --user factcheckr
   ```

#### Installation Issues

1. **Upgrade pip first**:
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Use virtual environment**:
   ```bash
   python -m venv factcheckr_env
   # Windows
   factcheckr_env\Scripts\activate
   # macOS/Linux
   source factcheckr_env/bin/activate
   pip install factcheckr
   ```

3. **Install from source**:
   ```bash
   git clone https://github.com/yourusername/factcheckr.git
   cd factcheckr
   pip install -e .
   ```

#### AI Service Issues

FactCheckr includes a robust fallback system for common claims when the AI service is unavailable. If you encounter AI-related errors:

1. The tool will automatically fall back to heuristic-based checking for common claims
2. Check your internet connection
3. The fallback system handles claims like:
   - "Cats have 9 lives" → Likely False
   - "The Earth is flat" → False
   - "Water boils at 100 degrees Celsius" → Likely True

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/factcheckr.git
cd factcheckr

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest build twine
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_core.py

# Run with coverage
pytest --cov=factcheckr
```

### Building and Publishing

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### Using the Deployment Script

A comprehensive deployment script is included:

```bash
# Full deployment to PyPI
python deploy.py

# Deploy to Test PyPI
python deploy.py --test

# Skip tests during deployment
python deploy.py --skip-tests

# Build only (skip upload)
python deploy.py --skip-upload
```

## API Reference

### CompleteFactCheckr Class

```python
class CompleteFactCheckr:
    def __init__(self, api_url: str = None)
    def fact_check_with_ai(self, claim: str) -> dict
    def extract_claim(self, text: str) -> str
```

#### Methods

- **`fact_check_with_ai(claim: str) -> dict`**: Main fact-checking method
  - **Parameters**: `claim` - The claim to fact-check
  - **Returns**: Dictionary with `verdict`, `evidence`, and `confidence`

- **`extract_claim(text: str) -> str`**: Extract the main claim from text
  - **Parameters**: `text` - Input text
  - **Returns**: Extracted claim string

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.1
- Enhanced error handling and fallback system
- Improved cross-platform compatibility
- Added comprehensive test suite
- Better CLI argument parsing
- JSON output support
- Interactive mode improvements

### v1.0.0
- Initial release
- Basic fact-checking functionality
- Command-line interface
- AI integration

## Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search [existing issues](https://github.com/yourusername/factcheckr/issues)
3. Create a [new issue](https://github.com/yourusername/factcheckr/issues/new)

## Acknowledgments

- Thanks to the Hack Club AI for providing the AI fact-checking capabilities
- Inspired by the need for reliable fact-checking tools in the digital age
- Built with Python and modern packaging best practices

---

**Made with ❤️ for truth and accuracy**