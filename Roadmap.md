# DocCraft Roadmap

> **Development Note:**
> Always use the conda environment named `doccraft` for all development and testing. Activate with:
> `conda activate doccraft`
> 
> **Status Update (2024-06-13):**
> - The `doccraft` conda environment is fully set up and tested.
> - All dependencies install and run correctly in the environment.
> - Tesseract OCR parser is implemented, demoed, and fully tested.

## Package Summary
**Purpose**: A Python package for intelligent document parsing and preprocessing, offering a unified interface for OCR, PDF extraction, AI model integration, and comprehensive benchmarking. DocCraft transforms complex document workflows into streamlined, measurable processes.

**Key Features**:
- **Unified API**: Simplify usage of OCR engines (Tesseract, PaddleOCR) and PDF libraries (PyMuPDF, pdfplumber).
- **Preprocessing**: Image enhancement (deskew, binarization), PDF splitting, and format conversion.
- **AI Integration**: Wrappers for models like LayoutLM or Donut for structured text extraction.
- **Postprocessing**: Text cleanup, table formatting, and output standardization (JSON/CSV).
- **Benchmarking**: Performance metrics and comparison tools for different parsing methods and configurations.

**Use Case**: Streamline document parsing workflows for developers/researchers working with scanned documents or PDFs, with a focus on performance optimization and measurable results.

## Phase 1: Core Setup & Basic Parsers (1-2 Weeks)
- [x] Initialize repo with `setup.py`, dependencies, and package structure.  
- [x] Implement core document parsers:  
  - [x] **Tesseract OCR**: Text extraction from images/PDFs.  
  - [x] **PyMuPDF**: Fast PDF text and metadata extraction.  
- [ ] Add basic preprocessing:  
  - [ ] Image deskewing/binarization (OpenCV).  
  - [ ] PDF-to-image conversion (`pdf2image`).  
- [ ] Minimal postprocessing:  
  - [ ] Regex-based text cleanup (dates, invoices).  
- [x] Write unit tests (pytest).  
- [x] Set up basic benchmarking framework:
  - [x] Define key performance metrics (speed, accuracy, memory usage).
  - [x] Create benchmark dataset with various document types.

## Phase 2: Advanced Parsers & Preprocessing (2-3 Weeks)  
- [ ] Add deep learning model integrations:  
  - [ ] **LayoutLM** (Hugging Face Transformers for structured text).  
  - [ ] **OCRmyPDF** wrapper for OCR-backed PDFs.  
- [ ] Advanced preprocessing:  
  - [ ] Table detection (using `Camelot` or `tabula-py`).  
  - [ ] Document splitting by sections/pages.  
- [ ] Postprocessing expansion:  
  - [ ] Table-to-CSV conversion.  
  - [ ] JSON schema standardization (e.g., for invoices).  
- [ ] Expand benchmarking suite:
  - [ ] Compare performance across different OCR engines.
  - [ ] Benchmark preprocessing pipeline efficiency.
  - [ ] Create performance comparison reports.

## Phase 3: Usability & Deployment (1 Week)  
- [ ] Write documentation (README, examples, API docs).  
- [ ] Publish to PyPI via `twine`.  
- [ ] Add CI/CD (GitHub Actions for automated testing).  
- [ ] Create demo scripts for common workflows.  
- [ ] Document benchmarking results and best practices:
  - [ ] Create benchmark visualization tools.
  - [ ] Add performance optimization guidelines.

## Future Enhancements  
- [ ] Support AWS Textract/Google Vision API integrations.  
- [ ] Add a CLI for non-Python users.  
- [ ] Dockerize for easy deployment.  
- [ ] Continuous benchmarking integration:
  - [ ] Automated performance regression testing.
  - [ ] Real-time performance monitoring tools.

## Design Principles: Modularity & Object-Oriented Architecture

- Each major functionality (parsing, preprocessing, postprocessing, benchmarking) is a separate subpackage.
- All algorithms/utilities are implemented as classes or functions in their own modules.
- Base classes/interfaces are defined for each component type (e.g., BaseParser, BasePreprocessor, BasePostprocessor).
- Each implementation is a subclass (e.g., TesseractOCRParser, BinarizationPreprocessor).
- Users can import and compose only the modules they need.
- Pipelines can be constructed by chaining objects (e.g., PreprocessingPipeline, Parser, PostprocessingPipeline).
- The API exposes a simple way to build and run pipelines, allowing users to select and configure modules via code or config.
- All modules and options are documented for discoverability and ease of use.

## Project File Structure (as of 2024-06-13)

```
DocCraft/
├── doccraft/
│   ├── __init__.py
│   ├── setup.py
│   ├── requirements.txt
│   ├── README.md
│   ├── doccraft/
│   │   ├── __init__.py
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── base_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── ocr_parser.py
│   │   ├── preprocessing/
│   │   │   └── __init__.py
│   │   ├── postprocessing/
│   │   │   └── __init__.py
│   │   ├── benchmarking/
│   │   │   └── __init__.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_pdf_parser.py
│   │   ├── test_ocr_parser.py
│   │   ├── test_package_structure.py
│   │   └── test_files/
│   │       ├── dummy.pdf
│   │       ├── lenna.png
│   │       ├── benchmark.tif
│   │       └── download_test_assets.py
│   ├── demo_ocr_parser.py
│   └── ...
├── Roadmap.md
└── ...
```

- `test_files/` contains reproducible test assets for integration tests.
- All core modules and tests are organized under `doccraft/`.