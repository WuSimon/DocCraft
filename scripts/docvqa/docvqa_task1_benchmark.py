#!/usr/bin/env python3
"""
DocVQA Task 1 Benchmarking with DocCraft Parsers

This script benchmarks different DocCraft parsers on the DocVQA Task 1 dataset.
Task 1 is Single Page Document Visual Question Answering with a simple Q&A format.

Usage:
    python docvqa_task1_benchmark.py --ground_truth path/to/gt.json --documents path/to/documents
"""

import json
import argparse
import os
import warnings
from typing import Dict, List, Any, Optional
from pathlib import Path

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*image_processor_class.*")
warnings.filterwarnings("ignore", message=".*use_fast.*")
warnings.filterwarnings("ignore", message=".*legacy.*")
warnings.filterwarnings("ignore", message=".*device.*")

# Set environment variables to suppress tokenizer warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Import DocCraft parsers
try:
    from doccraft.parsers import (
        PaddleOCRParser, PDFPlumberParser, 
        LayoutLMv3Parser, DeepSeekVLParser
    )
except ImportError:
    print("Warning: DocCraft not installed. Using fallback imports.")
    # Fallback for testing
    class MockParser:
        def __init__(self, name):
            self.name = name
        def extract_text(self, image_path):
            return f"Mock text from {self.name} for {image_path}"
    
    PaddleOCRParser = lambda: MockParser("paddleocr")
    PDFPlumberParser = lambda: MockParser("pdfplumber")
    LayoutLMv3Parser = lambda: MockParser("layoutlmv3")
    DeepSeekVLParser = lambda: MockParser("deepseekvl")


class DocVQATask1Benchmarker:
    """
    Benchmarker for DocVQA Task 1 (Single Page Document VQA).
    
    Task 1 format is simpler than Task 2:
    - Questions have image paths
    - No complex evidence scoring required
    - Simple question-answer pairs
    """
    
    def __init__(self):
        self.parsers = {
            'paddleocr': PaddleOCRParser(),
            'pdfplumber': PDFPlumberParser(),
            'layoutlmv3': LayoutLMv3Parser(),
            'deepseekvl': DeepSeekVLParser()
        }
    
    def load_ground_truth(self, gt_path: str) -> Dict[str, Any]:
        """Load Task 1 ground truth file."""
        with open(gt_path, 'r') as f:
            return json.load(f)
    
    def get_parser(self, parser_name: str):
        """Get parser by name."""
        if parser_name not in self.parsers:
            raise ValueError(f"Unknown parser: {parser_name}. Available: {list(self.parsers.keys())}")
        return self.parsers[parser_name]
    
    def extract_text_from_document(self, parser, image_path: str, documents_dir: str) -> str:
        """Extract text from document using the specified parser."""
        # Handle different image path formats
        # Ground truth might have "documents/filename.png" but actual files are just "filename.png"
        if image_path.startswith('documents/'):
            image_path = image_path.replace('documents/', '')
        
        full_path = os.path.join(documents_dir, image_path)
        
        if not os.path.exists(full_path):
            print(f"Warning: Image not found: {full_path}")
            return ""
        
        try:
            if hasattr(parser, 'extract_text'):
                return parser.extract_text(full_path)
            else:
                # Fallback for mock parsers
                return parser.extract_text(full_path)
        except Exception as e:
            print(f"Error extracting text from {full_path}: {e}")
            return ""
    
    def generate_answer(self, question: str, extracted_text: str) -> str:
        """
        Generate an answer based on the question and extracted text.
        This is a simple implementation - you can enhance this with better QA logic.
        """
        if not extracted_text:
            return "No answer"
        
        # Simple keyword-based answer generation
        question_lower = question.lower()
        text_lower = extracted_text.lower()
        
        # Look for numbers in the text if question asks for numbers
        if any(word in question_lower for word in ['how much', 'what is the', 'amount', 'number', 'percentage', '%']):
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', extracted_text)
            if numbers:
                return numbers[0]
        
        # Look for dates
        if any(word in question_lower for word in ['when', 'date', 'year']):
            import re
            dates = re.findall(r'\d{4}', extracted_text)
            if dates:
                return dates[0]
        
        # Look for names (simple heuristic)
        if any(word in question_lower for word in ['who', 'name', 'person']):
            # Simple name extraction - look for capitalized words
            import re
            names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', extracted_text)
            if names:
                return names[0]
        
        # Default: return first sentence
        sentences = extracted_text.split('.')
        if sentences:
            return sentences[0].strip()
        
        return "No answer"
    
    def benchmark_parser(self, ground_truth_path: str, documents_dir: str, 
                        parser_name: str, max_questions: Optional[int] = None) -> Dict[str, Any]:
        """
        Benchmark a single parser on the DocVQA Task 1 dataset.
        
        Args:
            ground_truth_path: Path to Task 1 ground truth JSON file
            documents_dir: Directory containing document images
            parser_name: Name of the parser to use
            max_questions: Maximum number of questions to process (for testing)
        
        Returns:
            Dictionary with benchmark results
        """
        print(f"\n=== Benchmarking {parser_name.upper()} on DocVQA Task 1 ===")
        
        # Load ground truth
        gt_data = self.load_ground_truth(ground_truth_path)
        questions = gt_data['data']
        
        if max_questions:
            questions = questions[:max_questions]
        
        print(f"Processing {len(questions)} questions...")
        
        # Get parser
        parser = self.get_parser(parser_name)
        
        results = {
            'parser': parser_name,
            'total_questions': len(questions),
            'processed_questions': 0,
            'answers': []
        }
        
        for i, qa_item in enumerate(questions):
            if i % 10 == 0:
                print(f"Processing question {i+1}/{len(questions)}")
            
            question_id = qa_item['questionId']
            question = qa_item['question']
            image_path = qa_item['image']
            
            # Handle different image path formats
            if image_path.startswith('documents/'):
                image_path = image_path.replace('documents/', '')
            
            full_image_path = os.path.join(documents_dir, image_path)
            
            if not os.path.exists(full_image_path):
                print(f"Warning: Image not found: {full_image_path}")
                predicted_answer = "No answer"
                confidence = 0.0
                extracted_text = ""
            else:
                try:
                    # Use ask_question method for AI parsers (like LayoutLMv3)
                    if hasattr(parser, 'ask_question'):
                        result = parser.ask_question(full_image_path, question)
                        predicted_answer = result.get('answer', 'No answer')
                        confidence = result.get('confidence', 0.0)
                        extracted_text = result.get('raw_answer', '')
                    else:
                        # Fallback for non-AI parsers
                        extracted_text = self.extract_text_from_document(parser, image_path, documents_dir)
                        predicted_answer = self.generate_answer(question, extracted_text)
                        confidence = 1.0  # Default confidence for non-AI parsers
                        
                except Exception as e:
                    print(f"Error processing question {question_id}: {e}")
                    predicted_answer = f"Error: {e}"
                    confidence = 0.0
                    extracted_text = ""
            
            results['answers'].append({
                'question_id': question_id,
                'question': question,
                'image': image_path,
                'extracted_text': extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
                'predicted_answer': predicted_answer,
                'confidence': confidence
            })
            
            results['processed_questions'] += 1
        
        print(f"✓ Completed {parser_name} benchmark")
        return results
    
    def benchmark_all_parsers(self, ground_truth_path: str, documents_dir: str,
                             max_questions: Optional[int] = None) -> Dict[str, Any]:
        """
        Benchmark all available parsers on the DocVQA Task 1 dataset.
        
        Args:
            ground_truth_path: Path to Task 1 ground truth JSON file
            documents_dir: Directory containing document images
            max_questions: Maximum number of questions to process (for testing)
        
        Returns:
            Dictionary with results for all parsers
        """
        print("DOCVQA TASK 1 BENCHMARK RESULTS")
        print("=" * 50)
        
        all_results = {
            'dataset': 'DocVQA Task 1',
            'ground_truth_path': ground_truth_path,
            'documents_dir': documents_dir,
            'parsers': {}
        }
        
        for parser_name in self.parsers.keys():
            try:
                results = self.benchmark_parser(
                    ground_truth_path, documents_dir, parser_name, max_questions
                )
                all_results['parsers'][parser_name] = results
            except Exception as e:
                print(f"Error benchmarking {parser_name}: {e}")
                all_results['parsers'][parser_name] = {
                    'parser': parser_name,
                    'error': str(e)
                }
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save benchmark results to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")
    
    def generate_predictions_file(self, ground_truth_path: str, documents_dir: str,
                                parser_name: str, output_path: str, max_questions: Optional[int] = None) -> None:
        """
        Generate predictions file in Task 1 format.
        
        Args:
            ground_truth_path: Path to Task 1 ground truth JSON file
            documents_dir: Directory containing document images
            parser_name: Name of the parser to use
            output_path: Path to save predictions file
            max_questions: Maximum number of questions to process (for testing)
        """
        print(f"\nGenerating predictions with {parser_name}...")
        
        # Load ground truth
        gt_data = self.load_ground_truth(ground_truth_path)
        questions = gt_data['data']
        
        if max_questions:
            questions = questions[:max_questions]
        
        # Get parser
        parser = self.get_parser(parser_name)
        
        predictions = []
        
        for i, qa_item in enumerate(questions):
            if i % 10 == 0:
                print(f"Processing question {i+1}/{len(questions)}")
            
            question_id = qa_item['questionId']
            question = qa_item['question']
            image_path = qa_item['image']
            
            # Handle different image path formats
            if image_path.startswith('documents/'):
                image_path = image_path.replace('documents/', '')
            
            full_image_path = os.path.join(documents_dir, image_path)
            
            if not os.path.exists(full_image_path):
                print(f"Warning: Image not found: {full_image_path}")
                predicted_answer = "No answer"
                confidence = 0.0
                extracted_text = ""
            else:
                try:
                    # Use ask_question method for AI parsers (like LayoutLMv3)
                    if hasattr(parser, 'ask_question'):
                        result = parser.ask_question(full_image_path, question)
                        predicted_answer = result.get('answer', 'No answer')
                        confidence = result.get('confidence', 0.0)
                        extracted_text = result.get('raw_answer', '')
                    else:
                        # Fallback for non-AI parsers
                        extracted_text = self.extract_text_from_document(parser, image_path, documents_dir)
                        predicted_answer = self.generate_answer(question, extracted_text)
                        confidence = 1.0  # Default confidence for non-AI parsers
                        
                except Exception as e:
                    print(f"Error processing question {question_id}: {e}")
                    predicted_answer = f"Error: {e}"
                    confidence = 0.0
                    extracted_text = ""
            
            predictions.append({
                'questionId': question_id,
                'question': question,
                'image': image_path,
                'predicted_answer': predicted_answer,
                'confidence': confidence,
                'extracted_text': extracted_text
            })
        
        # Save predictions
        with open(output_path, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        print(f"✓ Predictions saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark DocCraft parsers on DocVQA Task 1 dataset")
    parser.add_argument('--ground_truth', '-g', required=True,
                       help="Path to DocVQA Task 1 ground truth JSON file")
    parser.add_argument('--documents', '-d', required=True,
                       help="Directory containing document images")
    parser.add_argument('--parser', '-p', default='layoutlmv3',
                       help="Parser to use (default: layoutlmv3)")
    parser.add_argument('--all_parsers', '-a', action='store_true',
                       help="Benchmark all available parsers")
    parser.add_argument('--output', '-o', default='task1_benchmark_results.json',
                       help="Output file for results (default: task1_benchmark_results.json)")
    parser.add_argument('--generate_predictions', action='store_true',
                       help="Generate predictions file instead of full benchmark")
    parser.add_argument('--max_questions', type=int,
                       help="Maximum number of questions to process (for testing)")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.ground_truth):
        print(f"Error: Ground truth file not found: {args.ground_truth}")
        return
    
    if not os.path.exists(args.documents):
        print(f"Error: Documents directory not found: {args.documents}")
        return
    
    # Create benchmarker
    benchmarker = DocVQATask1Benchmarker()
    
    if args.generate_predictions:
        # Generate predictions file
        predictions_file = f"{args.parser}_task1_predictions.json"
        benchmarker.generate_predictions_file(
            args.ground_truth, args.documents, args.parser, predictions_file, args.max_questions
        )
    elif args.all_parsers:
        # Benchmark all parsers
        results = benchmarker.benchmark_all_parsers(
            args.ground_truth, args.documents, args.max_questions
        )
        benchmarker.save_results(results, args.output)
    else:
        # Benchmark single parser
        results = benchmarker.benchmark_parser(
            args.ground_truth, args.documents, args.parser, args.max_questions
        )
        benchmarker.save_results(results, args.output)


if __name__ == "__main__":
    main() 