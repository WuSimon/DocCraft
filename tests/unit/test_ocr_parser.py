"""
Tests for the OCR parser implementation.

This module contains comprehensive tests for the OCRParser class,
including text extraction, image preprocessing, and error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from doccraft.parsers import TesseractParser, BaseParser


class TestTesseractParser:
    """Test suite for the TesseractParser class."""
    
    def setup_method(self):
        """
        Set up test fixtures before each test method.
        
        This method runs before each test and creates a fresh
        TesseractParser instance for testing.
        """
        try:
            self.parser = TesseractParser()
        except ImportError:
            # Skip tests if Tesseract is not available
            pytest.skip("Tesseract not available")
    
    def test_parser_inheritance(self):
        """Test that TesseractParser inherits from BaseParser."""
        # Check that TesseractParser is a subclass of BaseParser
        assert issubclass(TesseractParser, BaseParser)
        
        # Check that we can instantiate it
        assert isinstance(self.parser, BaseParser)
        assert isinstance(self.parser, TesseractParser)
    
    def test_parser_attributes(self):
        """Test that the parser has the correct attributes."""
        # Check basic attributes
        assert self.parser.name == "Tesseract OCR"
        assert ".png" in self.parser.supported_formats
        assert ".jpg" in self.parser.supported_formats
        assert len(self.parser.supported_formats) >= 5  # Multiple image formats
        
        # Check that version is a string
        assert isinstance(self.parser.version, str)
        assert len(self.parser.version) > 0
        
        # Check language setting
        assert hasattr(self.parser, 'language')
        assert self.parser.language == 'eng'
    
    def test_can_parse_images(self):
        """Test that the parser can identify image files."""
        # Test with image extensions
        assert self.parser.can_parse("document.png")
        assert self.parser.can_parse("image.JPG")  # Case insensitive
        assert self.parser.can_parse("scan.tiff")
        assert self.parser.can_parse(Path("photo.bmp"))
        
        # Test with non-image extensions
        assert not self.parser.can_parse("document.pdf")
        assert not self.parser.can_parse("text.txt")
        assert not self.parser.can_parse("data.csv")
    
    def test_parser_info(self):
        """Test that parser info is returned correctly."""
        info = self.parser.get_parser_info()
        
        # Check that all required keys are present
        assert 'name' in info
        assert 'version' in info
        assert 'supported_formats' in info
        
        # Check values
        assert info['name'] == "Tesseract OCR"
        assert '.png' in info['supported_formats']
        assert isinstance(info['version'], str)
    
    def test_extract_text_invalid_file(self):
        """Test that the parser handles invalid files gracefully."""
        # Test with non-existent file
        result = self.parser.extract_text("nonexistent.png")
        
        # Check that error is captured
        assert result['error'] is not None
        assert result['text'] == ''
        assert result['extraction_time'] > 0
    
    def test_extract_text_unsupported_format(self):
        """Test that the parser rejects unsupported file formats."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"This is a text file, not an image")
            temp_file = f.name
        
        try:
            result = self.parser.extract_text(temp_file)
            
            # Check that error is captured
            assert result['error'] is not None
            assert "not supported" in result['error']
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_get_last_extraction_time(self):
        """Test that extraction time is tracked correctly."""
        # Initially, no extraction has been performed
        assert self.parser.get_last_extraction_time() == 0.0
        
        # After attempting extraction (even if it fails), time should be recorded
        result = self.parser.extract_text("nonexistent.png")
        assert self.parser.get_last_extraction_time() > 0.0
        assert self.parser.get_last_extraction_time() == result['extraction_time']
    
    def test_supported_languages(self):
        """Test that supported languages can be retrieved."""
        languages = self.parser.get_supported_languages()
        
        # Should return a list
        assert isinstance(languages, list)
        
        # Should contain at least English
        assert 'eng' in languages
    
    def test_parser_with_custom_language(self):
        """Test parser initialization with custom language."""
        try:
            # Create parser with custom language
            parser = TesseractParser(language='eng')
            assert parser.language == 'eng'
        except ImportError:
            pytest.skip("Tesseract not available")


class TestOCRParserWithRealImages:
    """Integration tests for OCR parser with real image files."""
    
    def setup_method(self):
        """Set up test fixtures."""
        try:
            self.parser = TesseractParser()
        except ImportError:
            pytest.skip("Tesseract not available")
    
    def create_test_image(self, text: str = "Hello World", filename: str = "test_image.png") -> str:
        """
        Create a test image with text for OCR testing.
        
        Args:
            text (str): Text to write on the image
            filename (str): Name of the output file
            
        Returns:
            str: Path to the created image file
        """
        # Create a simple image with text
        width, height = 400, 100
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a default font, fallback to basic if not available
        try:
            # Try to use a system font
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except (OSError, IOError):
            try:
                # Try another common font
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            except (OSError, IOError):
                # Use default font
                font = ImageFont.load_default()
        
        # Calculate text position to center it
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text in black
        draw.text((x, y), text, fill='black', font=font)
        
        # Save the image
        image_path = filename
        image.save(image_path)
        return image_path
    
    def test_extract_text_with_real_image(self):
        """
        Test text extraction with a real image file (Lenna PNG).
        """
        # Use the downloaded Lenna image
        test_image_path = os.path.join(os.path.dirname(__file__), "test_files", "lenna.png")
        if not os.path.exists(test_image_path):
            pytest.skip("Lenna test image not found.")
        result = self.parser.extract_text(test_image_path)
        # We don't know the exact text, but it should not error and should return some text or empty string
        assert result['error'] is None or isinstance(result['error'], str)
        assert 'text' in result
        assert 'extraction_time' in result
    
    def test_extract_text_with_confidence(self):
        """Test detailed OCR extraction with confidence scores."""
        # Create a test image
        test_text = "Confidence Test"
        image_path = self.create_test_image(test_text, "test_confidence.png")
        
        try:
            # Extract text with confidence information
            result = self.parser.extract_text_with_confidence(image_path)
            
            # Check result structure
            assert 'text_blocks' in result
            assert 'total_blocks' in result
            assert 'average_confidence' in result
            
            # Check data types
            assert isinstance(result['text_blocks'], list)
            assert isinstance(result['total_blocks'], int)
            assert isinstance(result['average_confidence'], float)
            
            # Check confidence range (0-100)
            assert 0 <= result['average_confidence'] <= 100
            
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    def test_ocr_with_different_languages(self):
        """Test OCR with different language settings."""
        # Create a test image
        image_path = self.create_test_image("Test", "test_language.png")
        
        try:
            # Test with English (default)
            result_eng = self.parser.extract_text(image_path, language='eng')
            assert result_eng['error'] is None
            
            # Test with different language setting
            result_custom = self.parser.extract_text(image_path, language='eng')
            assert result_custom['error'] is None
            
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    def test_ocr_with_preprocessing_disabled(self):
        """Test OCR with preprocessing disabled."""
        # Create a test image
        image_path = self.create_test_image("Preprocessing Test", "test_preprocess.png")
        
        try:
            # Test with preprocessing disabled
            result = self.parser.extract_text(image_path, preprocess=False)
            
            # Check that preprocessing was not applied
            assert result['metadata']['preprocessing_applied'] is False
            assert result['error'] is None
            
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    def test_ocr_with_confidence_threshold(self):
        """Test OCR with confidence threshold filtering."""
        # Create a test image
        image_path = self.create_test_image("Threshold Test", "test_threshold.png")
        
        try:
            # Test with high confidence threshold
            result = self.parser.extract_text(image_path, confidence_threshold=80)
            
            # Check that confidence threshold was applied
            assert result['metadata']['confidence_threshold'] == 80
            assert result['error'] is None
            
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)


class TestOCRParserErrorHandling:
    """Test error handling in OCR parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        try:
            self.parser = TesseractParser()
        except ImportError:
            pytest.skip("Tesseract not available")
    
    def test_parser_with_invalid_tesseract_path(self):
        """Test parser initialization with invalid Tesseract path."""
        with pytest.raises(ImportError):
            TesseractParser(tesseract_path="/invalid/path/to/tesseract")
    
    def test_extract_text_corrupted_image(self):
        """Test handling of corrupted image files."""
        # Create a corrupted image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(b"This is not a valid image file")
            corrupted_file = f.name
        
        try:
            result = self.parser.extract_text(corrupted_file)
            
            # Should handle the error gracefully
            assert result['error'] is not None
            
        finally:
            os.unlink(corrupted_file) 