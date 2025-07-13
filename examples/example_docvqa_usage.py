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

# Import DocCraft parsers
from doccraft.parsers import (
    PDFParser, PDFPlumberParser, OCRParser, PaddleOCRParser
)


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
        'Tesseract': OCRParser(),
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
    
    # Load ground truth
    with open(ground_truth_path, 'r') as f:
        gt_data = json.load(f)
    
    # Get parser
    parsers = {
        'pymupdf': PDFParser(),
        'pdfplumber': PDFPlumberParser(),
        'tesseract': OCRParser(),
        'paddleocr': PaddleOCRParser()
    }
    
    if parser_name not in parsers:
        print(f"Unknown parser: {parser_name}")
        return
    
    parser = parsers[parser_name]
    
    # Create predictions
    predictions = []
    
    for i, qa_item in enumerate(gt_data['data'][:5]):  # Process first 5 questions
        question_id = qa_item['question_id']
        question = qa_item['question']
        
        print(f"Processing question {question_id}: {question}")
        
        # Find document (simplified approach)
        documents_dir = Path(documents_dir)
        document_path = None
        
        for ext in ['.jpg', '.jpeg', '.png', '.tiff', '.tif']:
            possible_path = documents_dir / f"{question_id}{ext}"
            if possible_path.exists():
                document_path = str(possible_path)
                break
        
        if not document_path:
            # Try to find any image file
            for ext in ['.jpg', '.jpeg', '.png', '.tiff', '.tif']:
                for path in documents_dir.glob(f"*{ext}"):
                    document_path = str(path)
                    break
                if document_path:
                    break
        
        if document_path:
            print(f"  Using document: {Path(document_path).name}")
            
            # Extract text
            result = parser.extract_text(document_path)
            
            if result['error']:
                print(f"  Error: {result['error']}")
                answers = ['extraction failed']
                evidence = [0.1] * 10
            else:
                text = result['text']
                print(f"  Extracted {len(text)} characters")
                
                # Simple answer generation (keyword matching)
                text_lower = text.lower()
                question_lower = question.lower()
                
                answers = []
                question_words = set(question_lower.split())
                text_words = text_lower.split()
                
                for word in text_words:
                    if word in question_words and len(word) > 3:
                        answers.append(word)
                
                if not answers:
                    # Look for numbers
                    import re
                    numbers = re.findall(r'\d+', text)
                    answers = numbers[:3]
                
                if not answers:
                    answers = ['no specific answer found']
                
                # Simple evidence scoring
                overlap_count = sum(1 for word in text_words if word in question_words)
                relevance = min(1.0, overlap_count / max(1, len(text_words) / 10))
                evidence = [relevance] * 10
        else:
            print("  No document found")
            answers = ['no document found']
            evidence = [0.1] * 10
        
        # Create prediction
        prediction = {
            'question_id': question_id,
            'evidence': evidence,
            'answer': answers
        }
        
        predictions.append(prediction)
    
    # Save predictions
    with open(output_path, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"\nPredictions saved to {output_path}")
    print(f"Processed {len(predictions)} questions")


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
    
    # Create DocVQA predictions with different parsers
    for parser_name in ['tesseract', 'paddleocr']:
        output_path = f"predictions_{parser_name}.json"
        create_docvqa_predictions(ground_truth_path, documents_dir, parser_name, output_path)
    
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}")
    print("1. Run the full benchmark:")
    print("   python docvqa_benchmark.py -g path/to/gt.json -d path/to/documents")
    print("\n2. Compare specific parsers:")
    print("   python docvqa_benchmark.py -g path/to/gt.json -d path/to/documents -p tesseract")
    print("\n3. Use the original evaluate.py script:")
    print("   python evaluate.py -g path/to/gt.json -s predictions_tesseract.json")


if __name__ == "__main__":
    main() 