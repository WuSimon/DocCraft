"""
Document parsers module.

Contains implementations for various document parsing methods:
- OCR engines (Tesseract, PaddleOCR)
- PDF libraries (PyMuPDF, pdfplumber)
- AI model integrations (LayoutLM, Donut)
"""

# Import the base parser class
from .base_parser import BaseParser

# Import specific parser implementations
from .pdf_parser import PDFParser
from .ocr_parser import OCRParser

# Define what gets imported when someone does "from doccraft.parsers import *"
__all__ = [
    'BaseParser',
    'PDFParser',
    'OCRParser',
] 