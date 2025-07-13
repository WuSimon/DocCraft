"""
Document postprocessing module.

Contains tools for output processing:
- Text cleanup and formatting
- Table extraction and conversion
- Output standardization (JSON/CSV)
"""

# Import the base postprocessor class
from .base_postprocessor import BasePostprocessor

# Import specific postprocessor implementations
from .text_postprocessor import TextPostprocessor
from .table_postprocessor import TablePostprocessor

# Define what gets imported when someone does "from doccraft.postprocessing import *"
__all__ = [
    'BasePostprocessor',
    'TextPostprocessor',
    'TablePostprocessor',
] 