#!/usr/bin/env python3
"""
Test script for LayoutLMv3Parser with postprocessing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'doccraft'))

from doccraft.parsers import LayoutLMv3Parser
from pathlib import Path

def test_single_sample():
    """Test a single sample with postprocessing."""
    
    # Initialize parser
    parser = LayoutLMv3Parser(
        model_name="rubentito/layoutlmv3-base-mpdocvqa",
        device="auto"
    )
    
    # Test file path
    test_file = "doccraft/tests/test_files/docvqa/images/14350.jpg"
    
    if not Path(test_file).exists():
        print(f"Test file not found: {test_file}")
        return
    
    # Test questions
    questions = [
        "What is the candidate's name?",
        "What is the candidate's address?",
        "What is the candidate's phone number?",
        "What is the candidate's email?",
        "What is the candidate's date of birth?"
    ]
    
    print("Testing LayoutLMv3Parser with postprocessing...")
    print("=" * 60)
    
    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 40)
        
        try:
            result = parser.ask_question(test_file, question)
            
            print(f"Raw answer: {result.get('raw_answer', 'N/A')}")
            print(f"Cleaned answer: {result.get('answer', 'N/A')}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_single_sample() 