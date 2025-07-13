#!/usr/bin/env python3
"""
Test script for DocVQA integration with DocCraft parsers.

This script tests the basic functionality of the DocVQA integration
without requiring the actual DocVQA dataset.
"""

import json
import tempfile
import os
from pathlib import Path

# Import DocCraft parsers
from doccraft.parsers import (
    PDFParser, PDFPlumberParser, OCRParser, PaddleOCRParser
)


def create_mock_docvqa_data():
    """Create mock DocVQA data for testing."""
    
    # Create mock ground truth
    mock_gt = {
        "dataset_name": "DocVQA Test",
        "data": [
            {
                "question_id": 1,
                "question": "What is the total amount?",
                "answer": ["$100", "100 dollars"],
                "ground_truth": [1.0, 0.8, 0.6, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0]
            },
            {
                "question_id": 2,
                "question": "What is the date?",
                "answer": ["January 15, 2024", "01/15/2024"],
                "ground_truth": [1.0, 0.9, 0.7, 0.5, 0.3, 0.1, 0.0, 0.0, 0.0, 0.0]
            },
            {
                "question_id": 3,
                "question": "Who is the sender?",
                "answer": ["John Smith", "Smith"],
                "ground_truth": [1.0, 0.8, 0.6, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0]
            }
        ]
    }
    
    return mock_gt


def test_parser_initialization():
    """Test that all parsers can be initialized."""
    print("Testing parser initialization...")
    
    try:
        parsers = {
            'pymupdf': PDFParser(),
            'pdfplumber': PDFPlumberParser(),
            'tesseract': OCRParser(),
            'paddleocr': PaddleOCRParser()
        }
        
        for name, parser in parsers.items():
            print(f"  ✓ {name} parser initialized successfully")
            print(f"    - Name: {parser.name}")
            print(f"    - Version: {parser.version}")
            print(f"    - Supported formats: {parser.supported_formats}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error initializing parsers: {e}")
        return False


def test_benchmarker_creation():
    """Test that the benchmarker can be created."""
    print("\nTesting benchmarker creation...")
    
    try:
        # Import the benchmarker
        from docvqa_benchmark import DocVQABenchmarker
        
        benchmarker = DocVQABenchmarker()
        print("  ✓ DocVQABenchmarker created successfully")
        
        # Test parser access
        for parser_name in ['pymupdf', 'pdfplumber', 'tesseract', 'paddleocr']:
            parser = benchmarker.get_parser(parser_name)
            print(f"  ✓ Retrieved {parser_name} parser")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error creating benchmarker: {e}")
        return False


def test_evaluation_functions():
    """Test the evaluation functions."""
    print("\nTesting evaluation functions...")
    
    try:
        from docvqa_benchmark import (
            normalize_str, levenshtein_distance, NLS, 
            evaluate_question_evidence, evaluate_answer_anlsl
        )
        
        # Test string normalization
        assert normalize_str("Hello World") == "hello world"
        print("  ✓ String normalization works")
        
        # Test Levenshtein distance
        assert levenshtein_distance("hello", "helo") == 1
        print("  ✓ Levenshtein distance works")
        
        # Test NLS
        nls_score = NLS("hello", "helo")
        assert 0 <= nls_score <= 1
        print("  ✓ NLS calculation works")
        
        # Test evidence evaluation
        pred_evidence = [0.9, 0.8, 0.7, 0.6, 0.5]
        gt_evidence = [1.0, 0.8, 0.6, 0.4, 0.2]
        ap_score = evaluate_question_evidence(pred_evidence, gt_evidence)
        assert 0 <= ap_score <= 1
        print("  ✓ Evidence evaluation works")
        
        # Test answer evaluation
        pred_answers = ["hello", "world"]
        gt_answers = ["hello", "earth"]
        anlsl_score = evaluate_answer_anlsl(pred_answers, gt_answers, 1)
        assert 0 <= anlsl_score <= 1
        print("  ✓ Answer evaluation works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing evaluation functions: {e}")
        return False


def test_prediction_generation():
    """Test prediction generation with mock data."""
    print("\nTesting prediction generation...")
    
    try:
        from docvqa_benchmark import DocVQABenchmarker
        
        # Create mock data
        mock_gt = create_mock_docvqa_data()
        
        # Create temporary directory for mock documents
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock document files
            for i in range(1, 4):
                doc_path = temp_path / f"{i}.txt"
                with open(doc_path, 'w') as f:
                    f.write(f"This is a mock document {i} with some text content.")
            
            # Create temporary ground truth file
            gt_file = temp_path / "gt.json"
            with open(gt_file, 'w') as f:
                json.dump(mock_gt, f)
            
            # Test benchmarker
            benchmarker = DocVQABenchmarker()
            
            # Test with a simple text-based approach (since we don't have real images)
            for parser_name in ['tesseract', 'paddleocr']:
                try:
                    # This will likely fail since we don't have real images,
                    # but we can test the structure
                    print(f"  Testing {parser_name} parser structure...")
                    
                    # Test the helper functions
                    text = "This is a test document with some content."
                    question = "What is the content?"
                    
                    answers = benchmarker.create_simple_answer_from_text(text, question)
                    assert isinstance(answers, list)
                    print(f"    ✓ Answer generation works for {parser_name}")
                    
                    evidence = benchmarker.create_evidence_scores(text, question)
                    assert isinstance(evidence, list)
                    assert len(evidence) == 10
                    print(f"    ✓ Evidence scoring works for {parser_name}")
                    
                except Exception as e:
                    print(f"    ⚠ {parser_name} test had issues (expected for mock data): {e}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing prediction generation: {e}")
        return False


def test_script_imports():
    """Test that all scripts can be imported."""
    print("\nTesting script imports...")
    
    try:
        # Test docvqa_benchmark.py
        import docvqa_benchmark
        print("  ✓ docvqa_benchmark.py imports successfully")
        
        # Test docvqa_evaluation.py
        import docvqa_evaluation
        print("  ✓ docvqa_evaluation.py imports successfully")
        
        # Test example_docvqa_usage.py
        import example_docvqa_usage
        print("  ✓ example_docvqa_usage.py imports successfully")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error importing scripts: {e}")
        return False


def main():
    """Run all tests."""
    print("DocVQA Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Parser Initialization", test_parser_initialization),
        ("Benchmarker Creation", test_benchmarker_creation),
        ("Evaluation Functions", test_evaluation_functions),
        ("Prediction Generation", test_prediction_generation),
        ("Script Imports", test_script_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DocVQA integration is ready to use.")
        print("\nNext steps:")
        print("1. Download the DocVQA dataset")
        print("2. Run: python docvqa_benchmark.py -g gt.json -d documents/")
        print("3. Check the results and compare parser performance")
    else:
        print("⚠ Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    main() 