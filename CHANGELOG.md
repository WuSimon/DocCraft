# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-08-20

### Changed
- Rename distribution on PyPI to `doccraft-toolkit` (Python import remains `doccraft`).
- Update README install commands and PyPI links to use `doccraft-toolkit`.
- Guard AI parser imports so core installs work without `[ai]` extras (no `torch` required for `import doccraft`).

### Packaging
- Exclude `examples/` from source distribution; keep `docs/` only in sdist.
- Prune vendored `src/doccraft/DeepSeek-VL/` from sdist and repository; users install from upstream repo per README.
- Verify artifacts with build + twine check; confirm exclusions in sdist and wheel.

### Documentation
- Add Project Structure to README; clarify what is packaged vs excluded.
- Add TestPyPI/PyPI usage guidance; clarify DeepSeek-VL installation from source.

### Repository housekeeping
- Remove presentation assets and preparation documents from the repository.
- Update `Roadmap.md`: published to PyPI as `doccraft-toolkit`; next focus on CI/CD and docs.

---

## [0.1.0] - 2025-06-08

### Added
- Initial release of DocCraft: A comprehensive document processing and question-answering toolkit
- **Core Parsers**: Tesseract, PaddleOCR, PDFPlumber, PyMuPDF
- **AI Parsers**: LayoutLMv3, Qwen-VL, DeepSeek-VL (optional dependencies)
- **Document Processing Pipeline**: Preprocessing, parsing, and postprocessing modules
- **DocVQA Benchmarking**: Built-in support for DocVQA evaluation with comprehensive metrics
- **CLI Interface**: Command-line tools for document processing and benchmarking
- **Modular Architecture**: Extensible design for easy addition of new parsers and processors
- **Comprehensive Testing**: Unit and integration tests with proper test fixtures
- **Modern Packaging**: src layout, proper dependency management, and optional extras

### Features
- **Multiple Parser Support**: Unified interface for various OCR and PDF parsing engines
- **AI-Powered Document Understanding**: Integration with state-of-the-art vision-language models
- **Benchmarking Framework**: Performance and accuracy evaluation tools
- **Robust Error Handling**: Graceful handling of missing dependencies and parsing errors
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux
- **Python 3.8+ Support**: Compatible with modern Python versions

### Installation Options
- (Historical for 0.1.0)
- **Core Installation**: `pip install doccraft`
- **AI Features**: `pip install "doccraft[ai]"`
- **Development Tools**: `pip install "doccraft[dev]"`
- **Complete Installation**: `pip install "doccraft[all]"`

### CLI Commands
- `doccraft --help`: Show main help
- `doccraft benchmark --help`: Show benchmarking help
- `doccraft benchmark -g <gt.json> -d <documents> -p <parser>`: Run DocVQA benchmarks

### Documentation
- Comprehensive README with installation and usage instructions
- API documentation and examples
- DocVQA integration guide
- Package preparation and release checklist

### Technical Details
- **License**: MIT License
- **Python Version**: 3.8+
- **Dependencies**: Core dependencies for basic functionality, optional AI dependencies
- **Architecture**: Modular design with clear separation of concerns
- **Testing**: pytest-based test suite with 59 passing tests

---

## [0.1.1] - 2025-01-27

### Fixed
- Fixed author and email information in package metadata
- Updated version numbering for PyPI release
- Improved package structure and manifest

### Changed
- Version bump from 0.1.0 to 0.1.1 for PyPI release

---

## [Unreleased]

### Planned
- Additional AI model integrations
- Enhanced preprocessing options
- More comprehensive benchmarking metrics
- Web interface for document processing
- Cloud deployment support 