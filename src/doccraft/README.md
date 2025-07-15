# DocCraft

Intelligent Document Processing & Benchmarking

A Python package for unified document parsing, preprocessing, and benchmarking.

## Features

- **Unified API**: Simplify usage of OCR engines (Tesseract, PaddleOCR) and PDF libraries (PyMuPDF, pdfplumber)
- **Preprocessing**: Image enhancement (deskew, binarization), PDF splitting, and format conversion
- **AI Integration**: Wrappers for models like LayoutLM or Donut for structured text extraction
- **Postprocessing**: Text cleanup, table formatting, and output standardization (JSON/CSV)
- **Benchmarking**: Performance metrics and comparison tools for different parsing methods and configurations

## Installation

```bash
pip install doccraft
```

For development installation:
```bash
git clone https://github.com/WuSimon/DocCraft.git
cd DocCraft
pip install -e .
```

## Quick Start

```python
from doccraft.parsers import PDFParser
from doccraft.preprocessing import ImageEnhancer
from doccraft.benchmarking import BenchmarkSuite

# Parse a PDF document
parser = PDFParser()
text = parser.extract_text("document.pdf")

# Enhance image quality
enhancer = ImageEnhancer()
enhanced_image = enhancer.deskew("image.jpg")

# Benchmark different parsers
benchmark = BenchmarkSuite()
results = benchmark.compare_parsers(["document1.pdf", "document2.pdf"])
```

## Development Status

This project is currently in **Phase 1** of development. See [Roadmap.md](../Roadmap.md) for detailed development plans.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 