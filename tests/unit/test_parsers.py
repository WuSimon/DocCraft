import pytest
from pathlib import Path
from doccraft.parsers import PDFParser, PDFPlumberParser, TesseractParser, PaddleOCRParser
import os
import shutil

data_dir = Path(os.path.dirname(__file__)).parent / "data"

def tesseract_available():
    return shutil.which("tesseract") is not None

def test_pdf_parser_instantiation():
    parser = PDFParser()
    assert hasattr(parser, "extract_text")

def test_pdfplumber_parser_instantiation():
    parser = PDFPlumberParser()
    assert hasattr(parser, "extract_text")

def test_tesseract_parser_instantiation():
    try:
        parser = TesseractParser()
    except ImportError as e:
        pytest.skip(f"Tesseract not available: {e}")
    assert hasattr(parser, "extract_text")

def test_paddleocr_parser_instantiation():
    parser = PaddleOCRParser()
    assert hasattr(parser, "extract_text")

@pytest.mark.skipif(not (data_dir / "dummy.pdf").exists(), reason="dummy.pdf not found")
def test_pdf_parser_extract_text():
    parser = PDFParser()
    result = parser.extract_text(data_dir / "dummy.pdf")
    assert isinstance(result, dict)
    assert "text" in result

@pytest.mark.skipif(not (data_dir / "dummy.pdf").exists(), reason="dummy.pdf not found")
def test_pdfplumber_parser_extract_text():
    parser = PDFPlumberParser()
    result = parser.extract_text(data_dir / "dummy.pdf")
    assert isinstance(result, dict)
    assert "text" in result

def test_ocr_parser_extract_text():
    if not (data_dir / "lenna.png").exists():
        pytest.skip("lenna.png not found")
    try:
        parser = TesseractParser()
    except ImportError as e:
        pytest.skip(f"Tesseract not available: {e}")
    result = parser.extract_text(data_dir / "lenna.png")
    assert isinstance(result, dict)
    assert "text" in result

@pytest.mark.skipif(not (data_dir / "lenna.png").exists(), reason="lenna.png not found")
def test_paddleocr_parser_extract_text():
    parser = PaddleOCRParser()
    result = parser.extract_text(data_dir / "lenna.png")
    assert isinstance(result, dict)
    assert "text" in result 