#!/usr/bin/env python3
"""
Demo script for the OCR parser.

This script demonstrates the capabilities of the OCRParser class
by creating test images and extracting text from them.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PIL import Image, ImageDraw, ImageFont
from doccraft.parsers import TesseractParser


def create_test_image(text: str, filename: str, size: tuple = (600, 200)) -> str:
    """
    Create a test image with text for OCR demonstration.
    
    Args:
        text (str): Text to write on the image
        filename (str): Output filename
        size (tuple): Image size (width, height)
        
    Returns:
        str: Path to the created image file
    """
    width, height = size
    
    # Create a new image with white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a nice font
    try:
        # Try system fonts
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        except (OSError, IOError):
            # Fallback to default font
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
    image.save(filename)
    print(f"Created test image: {filename}")
    
    return filename


def demo_basic_ocr():
    """Demonstrate basic OCR functionality."""
    print("\n" + "="*60)
    print("DEMO: Basic OCR Text Extraction")
    print("="*60)
    
    try:
        # Initialize the OCR parser
        parser = TesseractParser()
        print(f"✓ OCR Parser initialized: {parser.name} v{parser.version}")
        
        # Create a test image
        test_text = "Hello World! This is a test of OCR capabilities."
        image_path = create_test_image(test_text, "demo_basic.png")
        
        try:
            # Extract text from the image
            print(f"\nExtracting text from: {image_path}")
            result = parser.extract_text(image_path)
            
            # Display results
            print(f"\nExtraction Results:")
            print(f"  Success: {'Yes' if result['error'] is None else 'No'}")
            print(f"  Time: {result['extraction_time']:.3f} seconds")
            print(f"  Language: {result['metadata']['ocr_language']}")
            print(f"  Confidence: {result['metadata']['ocr_confidence']:.1f}%")
            
            if result['error'] is None:
                print(f"\nExtracted Text:")
                print(f"  '{result['text']}'")
                
                # Show image info
                img_info = result['metadata']['image_info']
                print(f"\nImage Information:")
                print(f"  Format: {img_info['format']}")
                print(f"  Size: {img_info['width']}x{img_info['height']}")
                print(f"  Mode: {img_info['mode']}")
            else:
                print(f"  Error: {result['error']}")
                
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
                
    except ImportError as e:
        print(f"✗ Error: {e}")
        print("Please install Tesseract and pytesseract to run this demo.")


def demo_confidence_extraction():
    """Demonstrate detailed confidence extraction."""
    print("\n" + "="*60)
    print("DEMO: Detailed Confidence Extraction")
    print("="*60)
    
    try:
        parser = TesseractParser()
        
        # Create a test image with multiple words
        test_text = "OCR Confidence Test Multiple Words"
        image_path = create_test_image(test_text, "demo_confidence.png")
        
        try:
            # Extract text with confidence information
            print(f"\nExtracting text with confidence from: {image_path}")
            result = parser.extract_text_with_confidence(image_path)
            
            # Display results
            print(f"\nConfidence Analysis:")
            print(f"  Total text blocks: {result['total_blocks']}")
            print(f"  Average confidence: {result['average_confidence']:.1f}%")
            
            if result['text_blocks']:
                print(f"\nText Blocks with Confidence:")
                for i, block in enumerate(result['text_blocks'][:5]):  # Show first 5
                    print(f"  {i+1}. '{block['text']}' - {block['confidence']:.1f}%")
                
                if len(result['text_blocks']) > 5:
                    print(f"  ... and {len(result['text_blocks']) - 5} more blocks")
                    
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
                
    except ImportError as e:
        print(f"✗ Error: {e}")


def demo_language_support():
    """Demonstrate language support."""
    print("\n" + "="*60)
    print("DEMO: Language Support")
    print("="*60)
    
    try:
        parser = TesseractParser()
        
        # Get supported languages
        languages = parser.get_supported_languages()
        print(f"\nSupported Languages ({len(languages)}):")
        
        # Display first 10 languages
        for i, lang in enumerate(languages[:10]):
            print(f"  {i+1}. {lang}")
        
        if len(languages) > 10:
            print(f"  ... and {len(languages) - 10} more languages")
            
        # Test with different language setting
        print(f"\nTesting with language: eng")
        test_text = "English Text Test"
        image_path = create_test_image(test_text, "demo_language.png")
        
        try:
            result = parser.extract_text(image_path, language='eng')
            print(f"  Success: {'Yes' if result['error'] is None else 'No'}")
            if result['error'] is None:
                print(f"  Extracted: '{result['text']}'")
                
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
                
    except ImportError as e:
        print(f"✗ Error: {e}")


def demo_preprocessing_options():
    """Demonstrate preprocessing options."""
    print("\n" + "="*60)
    print("DEMO: Preprocessing Options")
    print("="*60)
    
    try:
        parser = TesseractParser()
        
        # Create a test image
        test_text = "Preprocessing Test"
        image_path = create_test_image(test_text, "demo_preprocess.png")
        
        try:
            # Test with preprocessing enabled (default)
            print(f"\nTesting with preprocessing enabled:")
            result_with_preprocess = parser.extract_text(image_path, preprocess=True)
            print(f"  Success: {'Yes' if result_with_preprocess['error'] is None else 'No'}")
            print(f"  Time: {result_with_preprocess['extraction_time']:.3f}s")
            
            # Test with preprocessing disabled
            print(f"\nTesting with preprocessing disabled:")
            result_without_preprocess = parser.extract_text(image_path, preprocess=False)
            print(f"  Success: {'Yes' if result_without_preprocess['error'] is None else 'No'}")
            print(f"  Time: {result_without_preprocess['extraction_time']:.3f}s")
            
            # Compare results
            if (result_with_preprocess['error'] is None and 
                result_without_preprocess['error'] is None):
                print(f"\nComparison:")
                print(f"  With preprocessing: '{result_with_preprocess['text']}'")
                print(f"  Without preprocessing: '{result_without_preprocess['text']}'")
                
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
                
    except ImportError as e:
        print(f"✗ Error: {e}")


def demo_confidence_threshold():
    """Demonstrate confidence threshold filtering."""
    print("\n" + "="*60)
    print("DEMO: Confidence Threshold Filtering")
    print("="*60)
    
    try:
        parser = TesseractParser()
        
        # Create a test image
        test_text = "Threshold Test"
        image_path = create_test_image(test_text, "demo_threshold.png")
        
        try:
            # Test with different confidence thresholds
            thresholds = [0, 50, 80, 95]
            
            for threshold in thresholds:
                print(f"\nTesting with confidence threshold: {threshold}%")
                result = parser.extract_text(image_path, confidence_threshold=threshold)
                
                if result['error'] is None:
                    print(f"  Extracted text: '{result['text']}'")
                    print(f"  Average confidence: {result['metadata']['ocr_confidence']:.1f}%")
                else:
                    print(f"  Error: {result['error']}")
                    
        finally:
            # Clean up
            if os.path.exists(image_path):
                os.unlink(image_path)
                
    except ImportError as e:
        print(f"✗ Error: {e}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n" + "="*60)
    print("DEMO: Error Handling")
    print("="*60)
    
    try:
        parser = TesseractParser()
        
        # Test with non-existent file
        print(f"\nTesting with non-existent file:")
        result = parser.extract_text("nonexistent_image.png")
        print(f"  Error handled: {'Yes' if result['error'] is not None else 'No'}")
        print(f"  Error message: {result['error']}")
        
        # Test with unsupported file format
        print(f"\nTesting with unsupported file format:")
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"This is a text file")
            temp_file = f.name
        
        try:
            result = parser.extract_text(temp_file)
            print(f"  Error handled: {'Yes' if result['error'] is not None else 'No'}")
            print(f"  Error message: {result['error']}")
        finally:
            os.unlink(temp_file)
            
    except ImportError as e:
        print(f"✗ Error: {e}")


def main():
    """Run all OCR parser demos."""
    print("DocCraft OCR Parser Demo")
    print("="*60)
    print("This demo showcases the capabilities of the OCRParser class")
    print("which uses Tesseract OCR engine to extract text from images.")
    
    # Run all demos
    demo_basic_ocr()
    demo_confidence_extraction()
    demo_language_support()
    demo_preprocessing_options()
    demo_confidence_threshold()
    demo_error_handling()
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("  ✓ Basic text extraction from images")
    print("  ✓ Confidence score analysis")
    print("  ✓ Multiple language support")
    print("  ✓ Image preprocessing options")
    print("  ✓ Confidence threshold filtering")
    print("  ✓ Robust error handling")
    print("\nThe OCR parser is now ready for integration into the DocCraft pipeline!")


if __name__ == "__main__":
    main() 