"""
Tests for the PDF parser implementation.

This module contains comprehensive tests for the PDFParser class,
including text extraction, metadata extraction, and error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
from doccraft.parsers import PDFParser, BaseParser


class TestPDFParser:
    """Test suite for the PDFParser class."""
    
    def setup_method(self):
        """
        Set up test fixtures before each test method.
        
        This method runs before each test and creates a fresh
        PDFParser instance for testing.
        """
        self.parser = PDFParser()
    
    def test_parser_inheritance(self):
        """Test that PDFParser inherits from BaseParser."""
        # Check that PDFParser is a subclass of BaseParser
        assert issubclass(PDFParser, BaseParser)
        
        # Check that we can instantiate it
        assert isinstance(self.parser, BaseParser)
        assert isinstance(self.parser, PDFParser)
    
    def test_parser_attributes(self):
        """Test that the parser has the correct attributes."""
        # Check basic attributes
        assert self.parser.name == "PyMuPDF"
        assert ".pdf" in self.parser.supported_formats
        assert len(self.parser.supported_formats) == 1
        
        # Check that version is a string
        assert isinstance(self.parser.version, str)
        assert len(self.parser.version) > 0
    
    def test_can_parse_pdf(self):
        """Test that the parser can identify PDF files."""
        # Test with .pdf extension
        assert self.parser.can_parse("document.pdf")
        assert self.parser.can_parse("test.PDF")  # Case insensitive
        assert self.parser.can_parse(Path("document.pdf"))
        
        # Test with non-PDF extensions
        assert not self.parser.can_parse("document.txt")
        assert not self.parser.can_parse("image.jpg")
        assert not self.parser.can_parse("document.docx")
    
    def test_parser_info(self):
        """Test that parser info is returned correctly."""
        info = self.parser.get_parser_info()
        
        # Check that all required keys are present
        assert 'name' in info
        assert 'version' in info
        assert 'supported_formats' in info
        
        # Check values
        assert info['name'] == "PyMuPDF"
        assert info['supported_formats'] == ['.pdf']
        assert isinstance(info['version'], str)
    
    def test_extract_text_invalid_file(self):
        """Test that the parser handles invalid files gracefully."""
        # Test with non-existent file
        result = self.parser.extract_text("nonexistent.pdf")
        
        # Check that error is captured
        assert result['error'] is not None
        assert result['text'] == ''
        assert result['extraction_time'] > 0
    
    def test_extract_text_unsupported_format(self):
        """Test that the parser rejects unsupported file formats."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"This is a text file, not a PDF")
            temp_file = f.name
        
        try:
            result = self.parser.extract_text(temp_file)
            
            # Check that error is captured
            assert result['error'] is not None
            assert "not supported" in result['error']
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_extract_metadata_only(self):
        """Test metadata-only extraction (requires a real PDF)."""
        # This test would require a real PDF file
        # For now, we'll test the method exists and has correct signature
        assert hasattr(self.parser, 'extract_metadata_only')
        
        # Test with non-existent file
        with pytest.raises(Exception):
            self.parser.extract_metadata_only("nonexistent.pdf")
    
    def test_get_last_extraction_time(self):
        """Test that extraction time is tracked correctly."""
        # Initially, no extraction has been performed
        assert self.parser.get_last_extraction_time() == 0.0
        
        # After attempting extraction (even if it fails), time should be recorded
        result = self.parser.extract_text("nonexistent.pdf")
        assert self.parser.get_last_extraction_time() > 0.0
        assert self.parser.get_last_extraction_time() == result['extraction_time']


class TestPDFParserIntegration:
    """Integration tests for PDF parser (requires real PDF files)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDFParser()
    
    def test_extract_text_with_real_pdf(self):
        """
        Test text extraction with a real PDF file.
        """
        # Use the downloaded dummy PDF
        test_pdf_path = Path(__file__).parent / "test_files" / "dummy.pdf"
        if not test_pdf_path.exists():
            pytest.skip("No test PDF file found. Run download_test_assets.py to fetch 'dummy.pdf'.")
        result = self.parser.extract_text(test_pdf_path)
        assert result['error'] is None
        assert result['text'] != ''
        assert result['extraction_time'] > 0
        assert result['parser_info']['name'] == "PyMuPDF"
        assert result['metadata']['file_path'] == str(test_pdf_path)
        assert result['metadata']['total_pages'] > 0
        assert result['metadata']['extraction_method'] == 'PyMuPDF'
    
    def test_extract_metadata_with_real_pdf(self):
        """Test metadata extraction with a real PDF file."""
        test_pdf_path = Path(__file__).parent / "test_files" / "dummy.pdf"
        if not test_pdf_path.exists():
            pytest.skip("No test PDF file found. Run download_test_assets.py to fetch 'dummy.pdf'.")
        metadata = self.parser.extract_metadata_only(test_pdf_path)
        assert metadata['file_path'] == str(test_pdf_path)
        assert metadata['total_pages'] > 0
        assert metadata['file_size'] > 0
        assert metadata['extraction_method'] == 'PyMuPDF (metadata only)'
        import time
        start_time = time.time()
        self.parser.extract_metadata_only(test_pdf_path)
        metadata_time = time.time() - start_time
        start_time = time.time()
        self.parser.extract_text(test_pdf_path)
        text_time = time.time() - start_time
        assert metadata_time < text_time 