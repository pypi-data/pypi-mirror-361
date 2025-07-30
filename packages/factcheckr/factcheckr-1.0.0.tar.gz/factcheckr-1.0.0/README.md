# FactCheckr 🔍

An AI-powered fact-checking tool that analyzes claims and provides evidence-based verdicts using free Hack Club AI.

## 🚀 Quick Start

### Install from PyPI
```bash
pip install factcheckr
```

### Install from Source
```bash
git clone https://github.com/geno543/fact_MCP_tool.git
cd fact_MCP_tool
pip install -e .
```

## ✨ Features

- **AI-Powered Analysis**: Uses advanced language models for accurate fact-checking
- **Free Service**: Powered by Hack Club AI - completely free, no API keys required
- **Multiple Input Methods**: Supports single claims, batch processing, and text analysis
- **Detailed Results**: Provides verdict, confidence score, and supporting evidence
- **Easy Integration**: Simple Python API and command-line interface
- **Instant Setup**: No configuration needed - works out of the box
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📖 Usage

### Command Line Interface

```bash
# Check a single claim
factcheckr "The Earth is round"

# Interactive mode
factcheckr --interactive

# Check from stdin
echo "Water boils at 100°C" | factcheckr --stdin

# JSON output
factcheckr "Cats have 9 lives" --json

# Show version
factcheckr --version
```

### Python API

```python
from factcheckr import FactCheckr

# Initialize the fact checker
fc = FactCheckr()

# Check a single claim
result = fc.fact_check("The Earth is flat")
print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']}")
print(f"Evidence: {result['evidence']}")

# Extract and check claims from text
text = "The sky is blue. Cats have 6 legs. Water boils at 100°C."
claims = fc.extract_claims(text)
for claim in claims:
    result = fc.fact_check(claim)
    print(f"{claim}: {result['verdict']} ({result['confidence']:.2f})")
```

### Batch Processing

```python
from factcheckr import FactCheckr

fc = FactCheckr()
claims = [
    "The Earth is round",
    "Cats have 9 lives", 
    "Python is a programming language"
]

for claim in claims:
    result = fc.fact_check(claim)
    print(f"{claim}: {result['verdict']} ({result['confidence']:.2f})")
```

## 📊 Example Output

```
$ factcheckr "Humans can fly"

Claim: "Humans can fly"
Verdict: False
Confidence: 0.95
Evidence: Humans cannot fly naturally without mechanical assistance. While humans have developed various flying machines and technologies, the human body lacks the necessary biological adaptations for flight, such as wings, hollow bones, and the required muscle structure.

$ factcheckr "Water boils at 100°C at sea level" --json
{
  "claim": "Water boils at 100°C at sea level",
  "verdict": "True",
  "confidence": 0.98,
  "evidence": "Water boils at 100°C (212°F) at standard atmospheric pressure (sea level). This is a well-established scientific fact."
}
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/geno543/fact_MCP_tool.git
cd fact_MCP_tool

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=factcheckr

# Run specific test
pytest tests/test_core.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 🌟 Why Hack Club AI?

- **Completely Free**: No API keys, no rate limits, no costs
- **High Quality**: Powered by advanced language models
- **Reliable**: Consistent uptime and performance
- **No Setup**: Works immediately without configuration
- **Community Driven**: Supported by the Hack Club community

## 📋 Requirements

- Python 3.7+
- requests library
- Internet connection

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/factcheckr/
- **GitHub Repository**: https://github.com/geno543/fact_MCP_tool
- **Issues**: https://github.com/geno543/fact_MCP_tool/issues
- **Hack Club AI**: https://ai.hackclub.com/