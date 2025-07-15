"""
Document parsers module.

Contains implementations for various document parsing methods:
- OCR engines (Tesseract, PaddleOCR)
- PDF libraries (PyMuPDF, pdfplumber)
- AI model integrations (LayoutLM, DeepSeek-VL)
"""

# Import the base parser class
from .base_parser import BaseParser

# Import specific parser implementations
from .pdf_parser import PDFParser
from .pdfplumber_parser import PDFPlumberParser
from .ocr_parser import OCRParser
from .paddle_ocr_parser import PaddleOCRParser
from .qwen_vl_parser import QwenVLParser

# Import AI parsers (optional dependencies)
try:
    from .base_ai_parser import BaseAIParser
    from .layoutlmv3_parser import LayoutLMv3Parser
    from .deepseek_vl_parser import DeepSeekVLParser
    AI_PARSERS_AVAILABLE = True
except ImportError:
    AI_PARSERS_AVAILABLE = False
    BaseAIParser = None
    LayoutLMv3Parser = None
    DeepSeekVLParser = None

# Define what gets imported when someone does "from doccraft.parsers import *"
__all__ = [
    'BaseParser',
    'PDFParser',
    'PDFPlumberParser',
    'OCRParser',
    'PaddleOCRParser',
]

# Add AI parsers to __all__ if available
if AI_PARSERS_AVAILABLE:
    __all__.extend([
        'BaseAIParser',
        'LayoutLMv3Parser',
        'DeepSeekVLParser',
    ])

# Parser registry for dynamic lookup
PARSER_REGISTRY = {
    'pdf': PDFParser,
    'pdfplumber': PDFPlumberParser,
    'ocr': OCRParser,
    'paddleocr': PaddleOCRParser,
}

if AI_PARSERS_AVAILABLE:
    PARSER_REGISTRY.update({
        'layoutlmv3': LayoutLMv3Parser,
        'deepseekvl': DeepSeekVLParser,
        'qwenvl': QwenVLParser,
    }) 