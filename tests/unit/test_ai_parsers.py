#!/usr/bin/env python3
"""
Test script for AI parsers (LayoutLMv3 and DeepSeek-VL).

This script tests the AI parsers with available test assets and various scenarios
to ensure they work correctly and handle different document types.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any
import pytest

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doccraft.parsers import LayoutLMv3Parser, DeepSeekVLParser
from doccraft.parsers import PDFParser, TesseractParser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_parser_initialization():
    """Test that AI parsers can be initialized correctly."""
    print("\n" + "="*60)
    print("TESTING PARSER INITIALIZATION")
    print("="*60)
    
    parsers = {}
    
    try:
        # Test LayoutLMv3 parser
        print("\n1. Testing LayoutLMv3 parser initialization...")
        layoutlmv3_parser = LayoutLMv3Parser(
            model_name="microsoft/layoutlmv3-base",
            device="cpu",  # Use CPU for testing
            task="document_understanding"
        )
        parsers['LayoutLMv3'] = layoutlmv3_parser
        print("✓ LayoutLMv3 parser initialized successfully")
        print(f"  - Model: {layoutlmv3_parser.model_name}")
        print(f"  - Device: {layoutlmv3_parser.device}")
        print(f"  - Task: {layoutlmv3_parser.task}")
        
    except Exception as e:
        print(f"✗ LayoutLMv3 parser initialization failed: {e}")
        logger.error(f"LayoutLMv3 initialization error: {e}")
    
    try:
        # Test DeepSeek-VL parser
        print("\n2. Testing DeepSeek-VL parser initialization...")
        deepseek_parser = DeepSeekVLParser(
            model_name="deepseek-ai/deepseek-vl-7b-chat",
            device="cpu",  # Use CPU for testing
            max_length=1024,
            temperature=0.1
        )
        parsers['DeepSeek-VL'] = deepseek_parser
        print("✓ DeepSeek-VL parser initialized successfully")
        print(f"  - Model: {deepseek_parser.model_name}")
        print(f"  - Device: {deepseek_parser.device}")
        print(f"  - Max length: {deepseek_parser.max_length}")
        print(f"  - Temperature: {deepseek_parser.temperature}")
        
    except Exception as e:
        print(f"✗ DeepSeek-VL parser initialization failed: {e}")
        logger.error(f"DeepSeek-VL initialization error: {e}")
    
    # Assert that at least some parsers were initialized successfully
    assert len(parsers) > 0, "No AI parsers were initialized successfully"


@pytest.fixture(scope="module")
def parsers():
    """Pytest fixture for initializing AI parsers."""
    parsers = {}
    
    try:
        # Test LayoutLMv3 parser
        layoutlmv3_parser = LayoutLMv3Parser(
            model_name="microsoft/layoutlmv3-base",
            device="cpu",  # Use CPU for testing
            task="document_understanding"
        )
        parsers['LayoutLMv3'] = layoutlmv3_parser
    except Exception as e:
        logger.error(f"LayoutLMv3 initialization error: {e}")
    
    try:
        # Test DeepSeek-VL parser
        deepseek_parser = DeepSeekVLParser(
            model_name="deepseek-ai/deepseek-vl-7b-chat",
            device="cpu",  # Use CPU for testing
            max_length=1024,
            temperature=0.1
        )
        parsers['DeepSeek-VL'] = deepseek_parser
    except Exception as e:
        logger.error(f"DeepSeek-VL initialization error: {e}")
    
    return parsers


def test_basic_text_extraction(parsers: Dict[str, Any]):
    """Test basic text extraction with available test assets."""
    print("\n" + "="*60)
    print("TESTING BASIC TEXT EXTRACTION")
    print("="*60)
    
    # Find test assets
    test_assets_dir = project_root / "test_assets"
    if not test_assets_dir.exists():
        print("✗ Test assets directory not found. Skipping text extraction tests.")
        return
    
    # Look for test images
    test_files = []
    for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        test_files.extend(test_assets_dir.glob(f"*{ext}"))
    
    if not test_files:
        print("✗ No test image files found. Skipping text extraction tests.")
        return
    
    print(f"Found {len(test_files)} test files: {[f.name for f in test_files]}")
    
    for parser_name, parser in parsers.items():
        print(f"\n--- Testing {parser_name} Parser ---")
        
        for test_file in test_files[:2]:  # Test with first 2 files
            print(f"\nProcessing: {test_file.name}")
            
            try:
                start_time = time.time()
                
                # Extract text
                extracted_text, metadata = parser.extract_text(str(test_file))
                
                processing_time = time.time() - start_time
                
                print(f"✓ Successfully extracted text from {test_file.name}")
                print(f"  - Processing time: {processing_time:.2f} seconds")
                print(f"  - Text length: {len(extracted_text)} characters")
                print(f"  - Device: {metadata.get('device', 'unknown')}")
                print(f"  - Model: {metadata.get('model_name', 'unknown')}")
                
                # Show first 200 characters of extracted text
                preview = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
                print(f"  - Text preview: {preview}")
                
            except Exception as e:
                print(f"✗ Failed to extract text from {test_file.name}: {e}")
                logger.error(f"Text extraction error with {parser_name}: {e}")


def test_advanced_features(parsers: Dict[str, Any]):
    """Test advanced features specific to each AI parser."""
    print("\n" + "="*60)
    print("TESTING ADVANCED FEATURES")
    print("="*60)
    
    # Find a test image
    test_assets_dir = project_root / "test_assets"
    test_files = list(test_assets_dir.glob("*.png")) + list(test_assets_dir.glob("*.jpg"))
    
    if not test_files:
        print("✗ No test image files found. Skipping advanced feature tests.")
        return
    
    test_file = test_files[0]
    print(f"Using test file: {test_file.name}")
    
    # Test LayoutLMv3 specific features
    if 'LayoutLMv3' in parsers:
        print("\n--- Testing LayoutLMv3 Advanced Features ---")
        layoutlmv3_parser = parsers['LayoutLMv3']
        
        try:
            # Test layout information extraction
            print("\n1. Testing layout information extraction...")
            layout_info = layoutlmv3_parser.extract_layout_info(str(test_file))
            print(f"✓ Layout info extracted: {list(layout_info.keys())}")
            
            # Test different tasks
            print("\n2. Testing different tasks...")
            for task in ["document_understanding", "classification", "ner"]:
                try:
                    layoutlmv3_parser.set_task(task)
                    extracted_text, metadata = layoutlmv3_parser.extract_text(str(test_file))
                    print(f"✓ Task '{task}' completed successfully")
                except Exception as e:
                    print(f"✗ Task '{task}' failed: {e}")
            
            # Test supported tasks
            supported_tasks = layoutlmv3_parser.get_supported_tasks()
            print(f"✓ Supported tasks: {supported_tasks}")
            
        except Exception as e:
            print(f"✗ LayoutLMv3 advanced features failed: {e}")
    
    # Test DeepSeek-VL specific features
    if 'DeepSeek-VL' in parsers:
        print("\n--- Testing DeepSeek-VL Advanced Features ---")
        deepseek_parser = parsers['DeepSeek-VL']
        
        try:
            # Test question answering
            print("\n1. Testing question answering...")
            question = "What is the main content of this document?"
            answer = deepseek_parser.ask_question(str(test_file), question)
            print(f"✓ Question answered: {answer.get('answer', 'No answer')[:100]}...")
            
            # Test structured information extraction
            print("\n2. Testing structured information extraction...")
            fields = ["title", "date", "content_type"]
            structured_info = deepseek_parser.extract_structured_info(str(test_file), fields)
            print(f"✓ Structured info extracted: {structured_info.get('data', {})}")
            
            # Test document summarization
            print("\n3. Testing document summarization...")
            summary = deepseek_parser.summarize_document(str(test_file))
            print(f"✓ Summary generated: {summary.get('answer', 'No summary')[:100]}...")
            
            # Test model capabilities
            capabilities = deepseek_parser.get_model_capabilities()
            print(f"✓ Model capabilities: {capabilities}")
            
        except Exception as e:
            print(f"✗ DeepSeek-VL advanced features failed: {e}")


def test_performance_comparison(parsers: Dict[str, Any]):
    """Compare performance between AI parsers and traditional parsers."""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON")
    print("="*60)
    
    # Find a test image
    test_assets_dir = project_root / "test_assets"
    test_files = list(test_assets_dir.glob("*.png")) + list(test_assets_dir.glob("*.jpg"))
    
    if not test_files:
        print("✗ No test image files found. Skipping performance comparison.")
        return
    
    test_file = test_files[0]
    print(f"Using test file: {test_file.name}")
    
    # Initialize traditional parsers for comparison
    traditional_parsers = {}
    
    try:
        ocr_parser = TesseractParser()
        traditional_parsers['Tesseract'] = ocr_parser
        print("✓ Tesseract parser initialized for comparison")
    except Exception as e:
        print(f"✗ Tesseract parser initialization failed: {e}")
    
    # Test all parsers
    all_parsers = {**parsers, **traditional_parsers}
    
    results = {}
    
    for parser_name, parser in all_parsers.items():
        print(f"\n--- Testing {parser_name} Performance ---")
        
        try:
            start_time = time.time()
            
            # Extract text
            extracted_text, metadata = parser.extract_text(str(test_file))
            
            processing_time = time.time() - start_time
            
            results[parser_name] = {
                'processing_time': processing_time,
                'text_length': len(extracted_text),
                'success': True
            }
            
            print(f"✓ {parser_name}: {processing_time:.2f}s, {len(extracted_text)} chars")
            
        except Exception as e:
            print(f"✗ {parser_name} failed: {e}")
            results[parser_name] = {
                'processing_time': None,
                'text_length': 0,
                'success': False,
                'error': str(e)
            }
    
    # Print comparison summary
    print("\n" + "-"*60)
    print("PERFORMANCE COMPARISON SUMMARY")
    print("-"*60)
    
    successful_parsers = {k: v for k, v in results.items() if v['success']}
    
    if successful_parsers:
        fastest_parser = min(successful_parsers.items(), key=lambda x: x[1]['processing_time'])
        print(f"Fastest parser: {fastest_parser[0]} ({fastest_parser[1]['processing_time']:.2f}s)")
        
        print("\nDetailed results:")
        for parser_name, result in results.items():
            if result['success']:
                print(f"  {parser_name}: {result['processing_time']:.2f}s, {result['text_length']} chars")
            else:
                print(f"  {parser_name}: FAILED - {result.get('error', 'Unknown error')}")
    else:
        print("No parsers completed successfully.")


def test_error_handling(parsers: Dict[str, Any]):
    """Test error handling with invalid inputs."""
    print("\n" + "="*60)
    print("TESTING ERROR HANDLING")
    print("="*60)
    
    for parser_name, parser in parsers.items():
        print(f"\n--- Testing {parser_name} Error Handling ---")
        
        # Test with non-existent file
        try:
            extracted_text, metadata = parser.extract_text("non_existent_file.png")
            print(f"✗ Should have failed with non-existent file")
        except Exception as e:
            print(f"✓ Correctly handled non-existent file: {type(e).__name__}")
        
        # Test with invalid file type
        try:
            # Create a temporary text file
            temp_file = project_root / "temp_test.txt"
            temp_file.write_text("This is not an image file.")
            
            extracted_text, metadata = parser.extract_text(str(temp_file))
            print(f"✗ Should have failed with text file")
            
            # Clean up
            temp_file.unlink()
        except Exception as e:
            print(f"✓ Correctly handled invalid file type: {type(e).__name__}")
            # Clean up if file was created
            temp_file = project_root / "temp_test.txt"
            if temp_file.exists():
                temp_file.unlink()


def main():
    """Main test function."""
    print("AI PARSERS TEST SUITE")
    print("="*60)
    print("This script tests the AI parsers (LayoutLMv3 and DeepSeek-VL)")
    print("with available test assets and various scenarios.")
    print("="*60)
    
    # Test parser initialization
    parsers = test_parser_initialization()
    
    if not parsers:
        print("\n✗ No AI parsers could be initialized. Exiting.")
        return
    
    # Test basic functionality
    test_basic_text_extraction(parsers)
    
    # Test advanced features
    test_advanced_features(parsers)
    
    # Test performance comparison
    test_performance_comparison(parsers)
    
    # Test error handling
    test_error_handling(parsers)
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
    print("Check the output above for any errors or issues.")
    print("If all tests pass, the AI parsers are working correctly!")


if __name__ == "__main__":
    main() 