#!/usr/bin/env python3
"""
DocVQA Evaluation with DocCraft Parsers

This script integrates DocCraft parsers with the DocVQA evaluation framework.
It allows you to benchmark different parsers (OCR, PDF) against the DocVQA dataset
and compare their performance using MAP and ANLSL metrics.

Usage:
    python docvqa_evaluation.py --ground_truth path/to/gt.json --documents path/to/documents --parser tesseract
"""

import os
import json
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np

# Import DocCraft parsers
from doccraft.parsers import (
    PDFParser, PDFPlumberParser, OCRParser, PaddleOCRParser
)

# Import evaluation functions from the provided evaluate.py
# (We'll include the key functions here for convenience)
from collections import Counter, OrderedDict


class DocVQAEvaluator:
    """
    Evaluates DocCraft parsers on the DocVQA dataset.
    """
    
    def __init__(self):
        self.parsers = {
            'pymupdf': PDFParser(),
            'pdfplumber': PDFPlumberParser(),
            'tesseract': OCRParser(),
            'paddleocr': PaddleOCRParser()
        }
    
    def get_parser(self, parser_name: str):
        """Get a parser by name."""
        if parser_name not in self.parsers:
            raise ValueError(f"Unknown parser: {parser_name}. Available: {list(self.parsers.keys())}")
        return self.parsers[parser_name]
    
    def extract_text_from_document(self, parser, document_path: str) -> str:
        """
        Extract text from a document using the specified parser.
        
        Args:
            parser: DocCraft parser instance
            document_path: Path to the document
            
        Returns:
            str: Extracted text
        """
        try:
            result = parser.extract_text(document_path)
            if result['error']:
                print(f"Warning: Error extracting text from {document_path}: {result['error']}")
                return ""
            return result['text']
        except Exception as e:
            print(f"Error extracting text from {document_path}: {e}")
            return ""
    
    def create_simple_answer_from_text(self, text: str, question: str) -> List[str]:
        """
        Create a simple answer based on extracted text and question.
        This is a basic implementation - in practice, you'd want a more sophisticated
        answer generation model.
        
        Args:
            text: Extracted text from document
            question: The question being asked
            
        Returns:
            List[str]: List of potential answers
        """
        # This is a very basic implementation
        # In practice, you'd want to use a proper QA model here
        text_lower = text.lower()
        question_lower = question.lower()
        
        # Simple keyword matching
        answers = []
        
        # Look for numbers in the text
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            answers.extend(numbers[:3])  # Take first 3 numbers
        
        # Look for words that appear in both question and text
        question_words = set(question_lower.split())
        text_words = text_lower.split()
        
        for word in text_words:
            if word in question_words and len(word) > 3:
                answers.append(word)
        
        # If no specific answers found, return some text snippets
        if not answers:
            sentences = text.split('.')
            answers = [s.strip()[:50] for s in sentences[:2] if s.strip()]
        
        return answers[:5]  # Limit to 5 answers
    
    def create_evidence_scores(self, text: str, question: str) -> List[float]:
        """
        Create evidence scores based on text relevance to question.
        This is a basic implementation - in practice, you'd want a more sophisticated
        relevance scoring model.
        
        Args:
            text: Extracted text from document
            question: The question being asked
            
        Returns:
            List[float]: Evidence scores (higher = more relevant)
        """
        # This is a very basic implementation
        # In practice, you'd want to use a proper relevance scoring model
        
        # For now, we'll create dummy evidence scores
        # The DocVQA format expects a list of floats with the same length as ground truth
        # We'll create a simple scoring based on word overlap
        
        text_lower = text.lower()
        question_lower = question.lower()
        
        # Simple word overlap scoring
        question_words = set(question_lower.split())
        text_words = text_lower.split()
        
        overlap_count = sum(1 for word in text_words if word in question_words)
        total_words = len(text_words)
        
        if total_words == 0:
            return [0.1] * 10  # Default low score
        
        relevance_score = min(1.0, overlap_count / max(1, total_words / 10))
        
        # Create a list of scores (DocVQA expects this format)
        # We'll create a simple distribution around the relevance score
        scores = []
        for i in range(10):  # Assuming 10 evidence items (adjust as needed)
            # Add some variation to the scores
            variation = np.random.normal(0, 0.1)
            score = max(0.0, min(1.0, relevance_score + variation))
            scores.append(score)
        
        return scores
    
    def generate_predictions(self, ground_truth_path: str, documents_dir: str, 
                           parser_name: str) -> List[Dict[str, Any]]:
        """
        Generate predictions for DocVQA using the specified parser.
        
        Args:
            ground_truth_path: Path to DocVQA ground truth JSON file
            documents_dir: Directory containing document images
            parser_name: Name of the parser to use
            
        Returns:
            List[Dict[str, Any]]: Predictions in DocVQA format
        """
        # Load ground truth
        with open(ground_truth_path, 'r') as f:
            gt_data = json.load(f)
        
        # Get parser
        parser = self.get_parser(parser_name)
        
        predictions = []
        
        print(f"Generating predictions using {parser_name} parser...")
        
        for i, qa_item in enumerate(gt_data['data']):
            question_id = qa_item['question_id']
            question = qa_item['question']
            
            # Find the corresponding document
            # DocVQA typically uses image files, so we need to find the right image
            # This is a simplified approach - you might need to adjust based on your dataset structure
            document_path = self.find_document_path(documents_dir, qa_item)
            
            if not document_path:
                print(f"Warning: Could not find document for question {question_id}")
                # Create dummy prediction
                prediction = {
                    'question_id': question_id,
                    'evidence': [0.1] * 10,  # Dummy evidence scores
                    'answer': ['no document found']
                }
                predictions.append(prediction)
                continue
            
            # Extract text from document
            print(f"Processing question {question_id} ({i+1}/{len(gt_data['data'])})")
            text = self.extract_text_from_document(parser, document_path)
            
            # Generate answer
            answers = self.create_simple_answer_from_text(text, question)
            
            # Generate evidence scores
            evidence_scores = self.create_evidence_scores(text, question)
            
            # Create prediction
            prediction = {
                'question_id': question_id,
                'evidence': evidence_scores,
                'answer': answers
            }
            
            predictions.append(prediction)
        
        return predictions
    
    def find_document_path(self, documents_dir: str, qa_item: Dict[str, Any]) -> Optional[str]:
        """
        Find the document path for a given QA item.
        This is a simplified implementation - you may need to adjust based on your dataset structure.
        
        Args:
            documents_dir: Directory containing documents
            qa_item: QA item from ground truth
            
        Returns:
            Optional[str]: Path to the document, or None if not found
        """
        # This is a simplified approach
        # In practice, you'd need to map question_id to the correct document
        # based on your specific dataset structure
        
        documents_dir = Path(documents_dir)
        
        # Look for common image formats
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']
        
        # Try to find a document based on question_id
        # This is a heuristic - adjust based on your actual dataset structure
        for ext in image_extensions:
            # Try different naming patterns
            possible_names = [
                f"{qa_item['question_id']}{ext}",
                f"doc_{qa_item['question_id']}{ext}",
                f"image_{qa_item['question_id']}{ext}",
                f"{qa_item['question_id']:04d}{ext}",  # Zero-padded
            ]
            
            for name in possible_names:
                path = documents_dir / name
                if path.exists():
                    return str(path)
        
        # If not found, try to find any image file
        for ext in image_extensions:
            for path in documents_dir.glob(f"*{ext}"):
                return str(path)
        
        return None
    
    def save_predictions(self, predictions: List[Dict[str, Any]], output_path: str):
        """Save predictions to a JSON file."""
        with open(output_path, 'w') as f:
            json.dump(predictions, f, indent=2)
        print(f"Predictions saved to {output_path}")
    
    def run_evaluation(self, ground_truth_path: str, predictions_path: str) -> Dict[str, Any]:
        """
        Run the DocVQA evaluation on the predictions.
        
        Args:
            ground_truth_path: Path to ground truth JSON file
            predictions_path: Path to predictions JSON file
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Import the evaluation functions
        # Note: You'll need to have the evaluate.py script in the same directory
        # or import it properly
        
        try:
            # Try to import the evaluation module
            import sys
            sys.path.append('.')
            from evaluate import evaluate_method
            
            # Run evaluation
            results = evaluate_method(ground_truth_path, predictions_path, {})
            return results
            
        except ImportError:
            print("Warning: Could not import evaluate.py. Please ensure it's in the current directory.")
            print("You can run the evaluation manually with:")
            print(f"python evaluate.py -g {ground_truth_path} -s {predictions_path}")
            return {}


def main():
    parser = argparse.ArgumentParser(description="Evaluate DocCraft parsers on DocVQA dataset")
    
    parser.add_argument('-g', '--ground_truth', type=str, required=True,
                       help="Path to DocVQA ground truth JSON file")
    parser.add_argument('-d', '--documents', type=str, required=True,
                       help="Directory containing document images")
    parser.add_argument('-p', '--parser', type=str, required=True,
                       choices=['pymupdf', 'pdfplumber', 'tesseract', 'paddleocr'],
                       help="Parser to use for evaluation")
    parser.add_argument('-o', '--output', type=str, default='predictions.json',
                       help="Output file for predictions (default: predictions.json)")
    parser.add_argument('--run_eval', action='store_true',
                       help="Run evaluation after generating predictions")
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = DocVQAEvaluator()
    
    # Generate predictions
    print(f"Starting evaluation with {args.parser} parser...")
    predictions = evaluator.generate_predictions(
        args.ground_truth, args.documents, args.parser
    )
    
    # Save predictions
    evaluator.save_predictions(predictions, args.output)
    
    # Run evaluation if requested
    if args.run_eval:
        print("Running evaluation...")
        results = evaluator.run_evaluation(args.ground_truth, args.output)
        
        if results:
            print("\nEvaluation Results:")
            print(f"Mean Average Precision: {np.mean(list(results['method']['map_dict'].values())):.4f}")
            print(f"Mean ANLSL: {np.mean(list(results['method']['anlsl_dict'].values())):.4f}")
    
    print("Done!")


if __name__ == "__main__":
    main() 