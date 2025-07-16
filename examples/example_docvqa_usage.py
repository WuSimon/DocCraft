#!/usr/bin/env python3
"""
Example: Using DocCraft Parsers with DocVQA Evaluation

This script demonstrates how to use your DocCraft parsers to benchmark
against the DocVQA dataset. It shows both the full benchmarking approach
and a simple comparison of parsers.
"""

import json
import time
from pathlib import Path
import sys

# Import DocCraft parsers
from doccraft.parsers import (
    PDFParser, PDFPlumberParser, TesseractParser, PaddleOCRParser
)

# Note: AI parsers (LayoutLMv3, Qwen-VL, DeepSeek-VL) require [ai] extra
# from doccraft.parsers import LayoutLMv3Parser, QwenVLParser, DeepSeekVLParser

# Import the unified DocVQABenchmarker
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
from doccraft.benchmarking.docvqa_benchmarker import DocVQABenchmarker


def simple_parser_comparison(documents_dir: str):
    """
    Simple comparison of parsers on a few documents.
    
    Args:
        documents_dir: Directory containing test documents
    """
    print("=" * 60)
    print("SIMPLE PARSER COMPARISON")
    print("=" * 60)
    
    # Initialize parsers
    parsers = {
        'PyMuPDF': PDFParser(),
        'PDFPlumber': PDFPlumberParser(),
        'Tesseract': TesseractParser(),
        'PaddleOCR': PaddleOCRParser()
    }
    
    # Find test documents
    documents_dir = Path(documents_dir)
    test_files = []
    
    # Look for common document formats
    for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif']:
        test_files.extend(documents_dir.glob(f"*{ext}"))
    
    if not test_files:
        print("No test documents found!")
        return
    
    print(f"Found {len(test_files)} test documents")
    
    # Test each parser on each document
    results = {}
    
    for parser_name, parser in parsers.items():
        print(f"\nTesting {parser_name} parser...")
        parser_results = []
        
        for doc_path in test_files[:3]:  # Test first 3 documents
            print(f"  Processing {doc_path.name}...")
            
            try:
                start_time = time.time()
                result = parser.extract_text(str(doc_path))
                extraction_time = time.time() - start_time
                
                if result['error']:
                    print(f"    Error: {result['error']}")
                    parser_results.append({
                        'file': doc_path.name,
                        'success': False,
                        'error': result['error'],
                        'time': extraction_time
                    })
                else:
                    text_length = len(result['text'])
                    print(f"    Success: {text_length} characters in {extraction_time:.2f}s")
                    parser_results.append({
                        'file': doc_path.name,
                        'success': True,
                        'text_length': text_length,
                        'time': extraction_time,
                        'text_preview': result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                    })
                    
            except Exception as e:
                print(f"    Exception: {e}")
                parser_results.append({
                    'file': doc_path.name,
                    'success': False,
                    'error': str(e),
                    'time': 0
                })
        
        results[parser_name] = parser_results
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for parser_name, parser_results in results.items():
        successful = sum(1 for r in parser_results if r['success'])
        total_time = sum(r['time'] for r in parser_results)
        avg_time = total_time / len(parser_results) if parser_results else 0
        
        print(f"\n{parser_name}:")
        print(f"  Success rate: {successful}/{len(parser_results)} ({successful/len(parser_results)*100:.1f}%)")
        print(f"  Average time: {avg_time:.2f}s")
        
        if successful > 0:
            avg_text_length = sum(r['text_length'] for r in parser_results if r['success']) / successful
            print(f"  Average text length: {avg_text_length:.0f} characters")


def create_docvqa_predictions(ground_truth_path: str, documents_dir: str, 
                            parser_name: str, output_path: str):
    """
    Create DocVQA format predictions using a specific parser.
    
    Args:
        ground_truth_path: Path to DocVQA ground truth JSON
        documents_dir: Directory containing documents
        parser_name: Name of parser to use
        output_path: Path to save predictions
    """
    print(f"\n{'='*60}")
    print(f"CREATING DOCVQA PREDICTIONS WITH {parser_name.upper()}")
    print(f"{'='*60}")
    benchmarker = DocVQABenchmarker()
    benchmarker.generate_predictions_file(ground_truth_path, documents_dir, parser_name, output_path)
    print(f"\nPredictions saved to {output_path}")


def main():
    """Main function demonstrating DocVQA integration."""
    
    print("DocCraft + DocVQA Integration Example")
    print("=" * 50)
    
    # Example paths (adjust these to your actual paths)
    documents_dir = "path/to/your/documents"  # Directory with DocVQA images
    ground_truth_path = "path/to/gt.json"     # DocVQA ground truth file
    
    # Check if paths exist
    if not Path(documents_dir).exists():
        print(f"Documents directory not found: {documents_dir}")
        print("Please update the path in the script and try again.")
        return
    
    if not Path(ground_truth_path).exists():
        print(f"Ground truth file not found: {ground_truth_path}")
        print("Please update the path in the script and try again.")
        return
    
    # Run simple comparison
    simple_parser_comparison(documents_dir)
    
    # Example: create predictions with unified benchmarker
    create_docvqa_predictions(ground_truth_path, documents_dir, 'paddleocr', 'docvqa_predictions_paddleocr.json')
    
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}")
    print("1. Run the full benchmark:")
    print("   doccraft benchmark -g path/to/gt.json -d path/to/documents -a")
    print("\n2. Compare specific parsers:")
    print("   doccraft benchmark -g path/to/gt.json -d path/to/documents -p tesseract")
    print("\n3. Test with limited questions:")
    print("   doccraft benchmark -g path/to/gt.json -d path/to/documents -p qwenvl --max_questions 10")


if __name__ == "__main__":
    main() 