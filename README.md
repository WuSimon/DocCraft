# DocCraft

A comprehensive document processing and question-answering toolkit.

## Installation

### Basic Installation (Core Features Only)
```bash
pip install doccraft
```

### With AI Features (LayoutLMv3, Qwen-VL, DeepSeek-VL)
```bash
pip install "doccraft[ai]"
```

### With Development Tools
```bash
pip install "doccraft[dev]"
```

### Complete Installation (AI + Development)
```bash
pip install "doccraft[all]"
```

## Optional Dependencies

### AI Features
The AI functionality requires additional dependencies that are not installed by default:

- **LayoutLMv3, Qwen-VL, DeepSeek-VL**: Install with `pip install "doccraft[ai]"`

**Includes:**
- **AI Models**: transformers, torch, torchvision (for AI parsers)
- **Visualization**: matplotlib (for plotting and analysis)
- **Streaming**: transformers_stream_generator (for Qwen-VL)

**DeepSeek-VL**: Requires manual installation from source:
```bash
pip install git+https://github.com/deepseek-ai/DeepSeek-VL.git
# Then install DocCraft with AI extras:
pip install "doccraft[ai]"
```

### Development Tools
For development and testing:
```bash
pip install "doccraft[dev]"
```

**Includes:**
- **Testing**: pytest, pytest-cov (test framework and coverage)
- **Code Quality**: black (formatting), flake8 (linting), mypy (type checking)
- **Evaluation**: python-Levenshtein, munkres (metrics and algorithms)

### Core vs AI Parsers
- **Core Parsers** (always available): Tesseract, PaddleOCR, PDFPlumber
- **AI Parsers** (require `[ai]` extra): LayoutLMv3, Qwen-VL, DeepSeek-VL

## Quick Start

1. **Install the package:**
   ```bash
   # Core features only
   pip install doccraft
   
   # With AI features
   pip install "doccraft[ai]"
   ```

2. **Basic usage:**
   ```python
   from doccraft.parsers import TesseractParser, PaddleOCRParser
   from doccraft.parsers import DeepSeekVLParser, QwenVLParser  # Requires [ai] extra
   
   # Core parsers
   tesseract = TesseractParser()
   paddle = PaddleOCRParser()
   
   # AI parsers (if installed with [ai] extra)
   deepseek = DeepSeekVLParser()
   qwen = QwenVLParser()
   ```

3. **Run DocVQA benchmarks:**
   ```bash
   # Using the CLI
   doccraft benchmark -g path/to/gt.json -d path/to/documents -p tesseract
   doccraft benchmark -g path/to/gt.json -d path/to/documents -p qwenvl
   ```

## CLI Usage

DocCraft provides a command-line interface for common tasks:

```bash
# Show help
doccraft --help

# Process documents
doccraft --input path/to/document.pdf --parser paddle

# Run DocVQA benchmarks
doccraft benchmark -g path/to/gt.json -d path/to/documents -p tesseract
```

## Key Features

- **Multiple Parser Support**: Tesseract, PaddleOCR, PDFPlumber, and AI-powered parsers
- **Document Processing Pipeline**: Preprocessing, parsing, and postprocessing
- **DocVQA Benchmarking**: Built-in support for DocVQA evaluation
- **Extensible Architecture**: Easy to add new parsers and processors
- **CLI Interface**: Command-line tools for common tasks

## Documentation

- [DocVQA Integration Guide](docs/DOCVQA_INTEGRATION.md)
- [API Documentation](https://doccraft.readthedocs.io/) *(if available)*

## Links
- [GitHub Repository](https://github.com/WuSimon/DocCraft)
- [PyPI Project Page](https://pypi.org/project/doccraft/)
- [DeepSeek-VL GitHub](https://github.com/deepseek-ai/DeepSeek-VL)

## Getting Help
- For issues, please open an issue on [GitHub](https://github.com/WuSimon/DocCraft/issues).
- For questions, see the documentation or contact the maintainer.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 