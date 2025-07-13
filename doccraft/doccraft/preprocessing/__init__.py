"""
Document preprocessing module.

Contains tools for document preparation:
- Image enhancement (deskew, binarization)
- PDF splitting and conversion
- Format standardization
"""

# Import the base preprocessor class
from .base_preprocessor import BasePreprocessor

# Import specific preprocessor implementations
from .image_preprocessor import ImagePreprocessor
from .pdf_preprocessor import PDFPreprocessor

# Define what gets imported when someone does "from doccraft.preprocessing import *"
__all__ = [
    'BasePreprocessor',
    'ImagePreprocessor',
    'PDFPreprocessor',
] 