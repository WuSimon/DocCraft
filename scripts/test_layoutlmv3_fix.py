#!/usr/bin/env python3
"""
Test script for the fixed LayoutLMv3Parser.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from doccraft.parsers import LayoutLMv3Parser
from PIL import Image
import numpy as np

def create_test_image():
    """Create a simple test image with text."""
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    
    # Add some text using PIL's ImageDraw
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Draw some text
    draw.text((50, 50), "Invoice", fill='black', font=font)
    draw.text((50, 80), "Date: January 15, 2024", fill='black', font=font)
    draw.text((50, 110), "Amount: $150.00", fill='black', font=font)
    draw.text((50, 140), "Customer: John Doe", fill='black', font=font)
    
    return img

def test_layoutlmv3_parser():
    """Test the LayoutLMv3Parser with a simple question."""
    print("Testing LayoutLMv3Parser...")
    
    try:
        # Initialize parser
        parser = LayoutLMv3Parser(task="question_answering")
        print("✓ Parser initialized successfully")
        
        # Create test image
        test_image = create_test_image()
        test_image_path = "test_image.png"
        test_image.save(test_image_path)
        print("✓ Test image created")
        
        # Test question answering
        question = "What is the amount on the invoice?"
        result = parser.ask_question(test_image_path, question)
        
        print(f"Question: {question}")
        print(f"Answer: {result.get('answer', 'No answer')}")
        print(f"Confidence: {result.get('confidence', 0.0)}")
        print("✓ Question answering test completed")
        
        # Clean up
        os.remove(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing LayoutLMv3Parser: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_layoutlmv3_parser()
    if success:
        print("\n🎉 LayoutLMv3Parser test passed!")
    else:
        print("\n❌ LayoutLMv3Parser test failed!")
        sys.exit(1) 