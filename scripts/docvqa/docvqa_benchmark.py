#!/usr/bin/env python3
"""
DocVQA Benchmarking with DocCraft Parsers

This script benchmarks different DocCraft parsers on the DocVQA dataset.
It extracts text from documents using various parsers and evaluates them
using the DocVQA metrics (MAP and ANLSL).

Usage:
    python docvqa_benchmark.py --ground_truth path/to/gt.json --documents path/to/documents
"""

import os
import json
import argparse
import time
import re
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, OrderedDict

# Import DocCraft parsers
from doccraft.parsers import (
    PDFParser, PDFPlumberParser, OCRParser, PaddleOCRParser
)
from doccraft.benchmarking import DocVQABenchmarker as NewDocVQABenchmarker
try:
    from doccraft.parsers import DeepSeekVLParser, LayoutLMv3Parser
    AI_PARSERS_AVAILABLE = True
except ImportError:
    AI_PARSERS_AVAILABLE = False
    DeepSeekVLParser = None
    LayoutLMv3Parser = None


# Evaluation functions (simplified from the original evaluate.py)
def normalize_str(string):
    """Normalize string for comparison."""
    return str(string).lower().strip()


def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings."""
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def NLS(str1, str2, threshold=0.5):
    """Normalized Levenshtein Similarity."""
    str1, str2 = normalize_str(str1), normalize_str(str2)
    lev_dist = levenshtein_distance(str1, str2)
    max_len = max(len(str1), len(str2))
    
    if max_len == 0:
        return 1.0
    
    norm_lev_dist = lev_dist / max_len
    norm_lev_sim = 1 - norm_lev_dist
    
    return norm_lev_sim if norm_lev_sim > threshold else 0


def precision_at_k(r, k):
    """Calculate precision at k."""
    assert k >= 1
    r = np.asarray(r)[:k] != 0
    if r.size != k:
        raise ValueError('Relevance score length < k')
    return np.mean(r)


def average_precision(r):
    """Calculate average precision."""
    r = np.asarray(r) != 0
    out = [precision_at_k(r, k + 1) for k in range(r.size) if r[k]]
    if not out:
        return 0.
    return np.mean(out)


def evaluate_question_evidence(pred_evidence, gt_evidence):
    """Evaluate evidence ranking using Average Precision."""
    inversed_gt = [-x for x in gt_evidence]
    ranked_gt = [gt for _, _, gt in sorted(zip(pred_evidence, inversed_gt, gt_evidence), reverse=True)]
    return average_precision(ranked_gt)


def evaluate_answer_anlsl(pred_answers, gt_answers, question_id):
    """Evaluate answer similarity using ANLSL."""
    # Simple implementation - in practice you'd want the full Hungarian algorithm
    if not pred_answers or not gt_answers:
        return 0.0
    
    # Calculate similarity between each predicted and ground truth answer
    similarities = []
    for pred in pred_answers:
        for gt in gt_answers:
            sim = NLS(pred, gt)
            similarities.append(sim)
    
    # Return the best similarity
    return max(similarities) if similarities else 0.0


class LegacyDocVQABenchmarker:
    """
    Benchmarks DocCraft parsers on the DocVQA dataset.
    """
    
    def __init__(self):
        self.parsers = {
            'pymupdf': PDFParser(),
            'pdfplumber': PDFPlumberParser(),
            'tesseract': OCRParser(),
            'paddleocr': PaddleOCRParser()
        }
        
        # Add AI parsers if available
        if AI_PARSERS_AVAILABLE:
            self.parsers['deepseekvl'] = DeepSeekVLParser()
            self.parsers['layoutlmv3'] = LayoutLMv3Parser()
    
    def get_parser(self, parser_name: str):
        """Get a parser by name."""
        if parser_name not in self.parsers:
            raise ValueError(f"Unknown parser: {parser_name}. Available: {list(self.parsers.keys())}")
        return self.parsers[parser_name]
    
    def extract_text_from_document(self, parser, document_path: str) -> str:
        """Extract text from a document using the specified parser."""
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
        """Create a simple answer based on extracted text and question."""
        text_lower = text.lower()
        question_lower = question.lower()
        
        answers = []
        
        # Look for numbers in the text
        numbers = re.findall(r'\d+', text)
        if numbers:
            answers.extend(numbers[:3])
        
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
        
        return answers[:5]
    
    def create_evidence_scores(self, text: str, question: str) -> List[float]:
        """Create evidence scores based on text relevance to question."""
        text_lower = text.lower()
        question_lower = question.lower()
        
        # Simple word overlap scoring
        question_words = set(question_lower.split())
        text_words = text_lower.split()
        
        overlap_count = sum(1 for word in text_words if word in question_words)
        total_words = len(text_words)
        
        if total_words == 0:
            return [0.1] * 10
        
        relevance_score = min(1.0, overlap_count / max(1, total_words / 10))
        
        # Create a list of scores
        scores = []
        for i in range(10):
            variation = np.random.normal(0, 0.1)
            score = max(0.0, min(1.0, relevance_score + variation))
            scores.append(score)
        
        return scores
    
    def find_document_path(self, documents_dir: str, qa_item: Dict[str, Any]) -> Optional[str]:
        """Find the document path for a given QA item."""
        documents_dir = Path(documents_dir)
        
        # Look for common image formats
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']
        
        # Try to find a document based on question_id
        for ext in image_extensions:
            possible_names = [
                f"{qa_item['question_id']}{ext}",
                f"doc_{qa_item['question_id']}{ext}",
                f"image_{qa_item['question_id']}{ext}",
                f"{qa_item['question_id']:04d}{ext}",
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
    
    def benchmark_parser(self, ground_truth_path: str, documents_dir: str, 
                        parser_name: str) -> Dict[str, Any]:
        """
        Benchmark a single parser on the DocVQA dataset.
        
        Args:
            ground_truth_path: Path to DocVQA ground truth JSON file
            documents_dir: Directory containing document images
            parser_name: Name of the parser to benchmark
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        # Load ground truth
        with open(ground_truth_path, 'r') as f:
            gt_data = json.load(f)
        
        # Get parser
        parser = self.get_parser(parser_name)
        
        # Initialize metrics
        map_scores = []
        anlsl_scores = []
        extraction_times = []
        
        print(f"Benchmarking {parser_name} parser...")
        
        for i, qa_item in enumerate(gt_data['data']):
            question_id = qa_item['question_id']
            question = qa_item['question']
            
            # Find the corresponding document
            document_path = self.find_document_path(documents_dir, qa_item)
            
            if not document_path:
                print(f"Warning: Could not find document for question {question_id}")
                map_scores.append(0.0)
                anlsl_scores.append(0.0)
                extraction_times.append(0.0)
                continue
            
            # Extract text from document
            print(f"Processing question {question_id} ({i+1}/{len(gt_data['data'])})")
            start_time = time.time()
            
            # Check if parser supports question answering
            if hasattr(parser, 'ask_question'):
                # Use AI parser's question answering capability
                print(f"  Using AI parser for question: {question}")
                result = parser.ask_question(document_path, question)
                extraction_time = time.time() - start_time
                extraction_times.append(extraction_time)
                
                # Extract answer from AI parser result
                answer = result.get('answer', '')
                if isinstance(answer, str):
                    answers = [answer] if answer.strip() else []
                else:
                    answers = answer if isinstance(answer, list) else []
                
                # For AI parsers, we need to extract text for evidence scoring
                text = self.extract_text_from_document(parser, document_path)
                evidence_scores = self.create_evidence_scores(text, question)
                
                print(f"  AI parser answer: {answers}")
            else:
                # Use traditional text extraction approach
                text = self.extract_text_from_document(parser, document_path)
                extraction_time = time.time() - start_time
                extraction_times.append(extraction_time)
                
                # Generate answer
                answers = self.create_simple_answer_from_text(text, question)
                
                # Generate evidence scores
                evidence_scores = self.create_evidence_scores(text, question)
            
            # Evaluate evidence (MAP)
            gt_evidence = qa_item.get('ground_truth', [0.0] * len(evidence_scores))
            if len(gt_evidence) != len(evidence_scores):
                # Pad or truncate to match
                if len(gt_evidence) < len(evidence_scores):
                    gt_evidence.extend([0.0] * (len(evidence_scores) - len(gt_evidence)))
                else:
                    gt_evidence = gt_evidence[:len(evidence_scores)]
            
            map_score = evaluate_question_evidence(evidence_scores, gt_evidence)
            map_scores.append(map_score)
            
            # Evaluate answer (ANLSL)
            gt_answers = qa_item.get('answer', [])
            if isinstance(gt_answers, str):
                gt_answers = [gt_answers]
            
            anlsl_score = evaluate_answer_anlsl(answers, gt_answers, question_id)
            anlsl_scores.append(anlsl_score)
        
        # Calculate final metrics
        results = {
            'parser': parser_name,
            'mean_map': np.mean(map_scores),
            'mean_anlsl': np.mean(anlsl_scores),
            'mean_extraction_time': np.mean(extraction_times),
            'total_questions': len(gt_data['data']),
            'successful_extractions': len([t for t in extraction_times if t > 0]),
            'map_scores': map_scores,
            'anlsl_scores': anlsl_scores,
            'extraction_times': extraction_times
        }
        
        return results
    
    def benchmark_all_parsers(self, ground_truth_path: str, documents_dir: str) -> Dict[str, Any]:
        """
        Benchmark all available parsers on the DocVQA dataset.
        
        Args:
            ground_truth_path: Path to DocVQA ground truth JSON file
            documents_dir: Directory containing document images
            
        Returns:
            Dict[str, Any]: Results for all parsers
        """
        all_results = {}
        
        for parser_name in self.parsers.keys():
            print(f"\n{'='*50}")
            print(f"Benchmarking {parser_name.upper()} parser")
            print(f"{'='*50}")
            
            try:
                results = self.benchmark_parser(ground_truth_path, documents_dir, parser_name)
                all_results[parser_name] = results
            except Exception as e:
                print(f"Error benchmarking {parser_name}: {e}")
                all_results[parser_name] = {
                    'parser': parser_name,
                    'error': str(e)
                }
        
        return all_results
    
    def print_results(self, results: Dict[str, Any]):
        """Print benchmark results in a formatted way."""
        print(f"\n{'='*60}")
        print("DOCVQA BENCHMARK RESULTS")
        print(f"{'='*60}")
        
        # Print summary table
        print(f"{'Parser':<15} {'MAP':<10} {'ANLSL':<10} {'Time (s)':<12} {'Success':<10}")
        print("-" * 60)
        
        for parser_name, result in results.items():
            if 'error' in result:
                print(f"{parser_name:<15} {'ERROR':<10} {'ERROR':<10} {'ERROR':<12} {'ERROR':<10}")
                continue
            
            success_rate = (result['successful_extractions'] / result['total_questions']) * 100
            print(f"{parser_name:<15} {result['mean_map']:<10.4f} {result['mean_anlsl']:<10.4f} "
                  f"{result['mean_extraction_time']:<12.4f} {success_rate:<10.1f}%")
        
        print(f"\n{'='*60}")
        
        # Find best parser for each metric
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if valid_results:
            best_map = max(valid_results.items(), key=lambda x: x[1]['mean_map'])
            best_anlsl = max(valid_results.items(), key=lambda x: x[1]['mean_anlsl'])
            fastest = min(valid_results.items(), key=lambda x: x[1]['mean_extraction_time'])
            
            print(f"Best MAP: {best_map[0]} ({best_map[1]['mean_map']:.4f})")
            print(f"Best ANLSL: {best_anlsl[0]} ({best_anlsl[1]['mean_anlsl']:.4f})")
            print(f"Fastest: {fastest[0]} ({fastest[1]['mean_extraction_time']:.4f}s)")
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save benchmark results to a JSON file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_path}")

    def generate_predictions_file(self, ground_truth_path: str, documents_dir: str, 
                                parser_name: str, output_path: str) -> None:
        """
        Generate predictions file in the format expected by the official DocVQA evaluation script.
        Args:
            ground_truth_path: Path to DocVQA ground truth JSON file
            documents_dir: Directory containing document images
            parser_name: Name of the parser to use
            output_path: Path to save predictions file
        """
        # Load ground truth
        with open(ground_truth_path, 'r') as f:
            gt_data = json.load(f)
        
        # Get parser
        parser = self.get_parser(parser_name)
        
        predictions = []
        
        print(f"Generating predictions for {parser_name} parser...")
        
        for i, qa_item in enumerate(gt_data['data']):
            question_id = qa_item['question_id']
            question = qa_item['question']
            ground_truth_evidence = qa_item.get('ground_truth', [])
            evidence_length = len(ground_truth_evidence)
            
            # Find the corresponding document
            document_path = self.find_document_path(documents_dir, qa_item)
            
            if not document_path:
                print(f"Warning: Could not find document for question {question_id}")
                # Create dummy prediction
                prediction = {
                    'question_id': question_id,
                    'evidence': [0.1] * evidence_length,  # Dummy evidence scores, but correct length
                    'answer': ['no document found']
                }
                predictions.append(prediction)
                continue
            
            print(f"Processing question {question_id} ({i+1}/{len(gt_data['data'])})")
            
            # Check if parser supports question answering
            if hasattr(parser, 'ask_question'):
                # Use AI parser's question answering capability
                print(f"  Using AI parser for question: {question}")
                result = parser.ask_question(document_path, question)
                
                # Extract answer from AI parser result
                answer = result.get('answer', '')
                if isinstance(answer, str):
                    answers = [answer] if answer.strip() else []
                else:
                    answers = answer if isinstance(answer, list) else []
                
                # For AI parsers, we need to extract text for evidence scoring
                text = self.extract_text_from_document(parser, document_path)
            else:
                # Use traditional text extraction approach
                text = self.extract_text_from_document(parser, document_path)
                # Generate answer
                answers = self.create_simple_answer_from_text(text, question)
            
            # Generate evidence scores with correct length and scoring logic
            # Example scoring: assign higher scores to evidence indices that match question words
            # For now, use a simple logic: if the index is divisible by 10, score higher
            scores = []
            question_words = set(question.lower().split())
            for idx in range(evidence_length):
                # Example: score based on index and question length
                score = 0.1
                if (idx % 10) == 0:
                    score += 0.2
                if (idx % (len(question_words) + 1)) == 0:
                    score += 0.1
                # Add some random noise for variety
                import random
                score += random.uniform(-0.05, 0.05)
                score = max(0.0, min(1.0, score))
                scores.append(score)
            
            prediction = {
                'question_id': question_id,
                'evidence': scores,
                'answer': answers
            }
            predictions.append(prediction)
        
        # Save predictions
        with open(output_path, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        print(f"Predictions saved to {output_path}")
        print(f"Total predictions: {len(predictions)}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark DocCraft parsers on DocVQA dataset")
    
    parser.add_argument('-g', '--ground_truth', type=str, required=True,
                       help="Path to DocVQA ground truth JSON file")
    parser.add_argument('-d', '--documents', type=str, required=True,
                       help="Directory containing document images")
    parser.add_argument('-p', '--parser', type=str,
                       choices=['pymupdf', 'pdfplumber', 'tesseract', 'paddleocr', 'deepseekvl', 'layoutlmv3'],
                       help="Benchmark specific parser (default: all parsers)")
    parser.add_argument('-o', '--output', type=str, default='benchmark_results.json',
                       help="Output file for results (default: benchmark_results.json)")
    parser.add_argument('--use_docvqa_benchmarker', action='store_true',
                       help="Use the new DocVQABenchmarker class for benchmarking")
    parser.add_argument('--eval_script', type=str, default=None,
                       help="Path to official DocVQA evaluation script (optional)")
    parser.add_argument('--generate_predictions', action='store_true',
                       help="Generate predictions file in format for official evaluation script")
    args = parser.parse_args()
    
    if args.use_docvqa_benchmarker:
        # Use new DocVQABenchmarker
        gt_json = args.ground_truth
        images_dir = args.documents
        eval_script = args.eval_script
        benchmarker = NewDocVQABenchmarker(
            dataset_json=gt_json,
            images_dir=images_dir,
            eval_script_path=eval_script,
            gt_json=gt_json
        )
        # Parser selection
        parser_map = {
            'pymupdf': PDFParser(),
            'pdfplumber': PDFPlumberParser(),
            'tesseract': OCRParser(),
            'paddleocr': PaddleOCRParser(),
        }
        if AI_PARSERS_AVAILABLE:
            parser_map['deepseekvl'] = DeepSeekVLParser()
            parser_map['layoutlmv3'] = LayoutLMv3Parser()
        if args.parser:
            if args.parser not in parser_map:
                raise ValueError(f"Unknown parser: {args.parser}")
            selected_parser = parser_map[args.parser]
            results = benchmarker.benchmark(selected_parser, output_predictions_path=args.output)
            print(results.get('eval_results', ''))
        else:
            for name, selected_parser in parser_map.items():
                print(f"\n{'='*50}\nBenchmarking {name.upper()} parser\n{'='*50}")
                results = benchmarker.benchmark(selected_parser, output_predictions_path=f"{name}_predictions.json")
                print(results.get('eval_results', ''))
        print("\nDocVQABenchmarker benchmarking complete!")
        return
    
    # Initialize benchmarker
    benchmarker = LegacyDocVQABenchmarker()
    
    if args.generate_predictions:
        # Generate predictions file for official evaluation
        if not args.parser:
            print("Error: --generate_predictions requires specifying a parser with --parser")
            return
        
        print(f"Generating predictions for {args.parser} parser...")
        predictions_output = f"{args.parser}_predictions.json"
        benchmarker.generate_predictions_file(args.ground_truth, args.documents, args.parser, predictions_output)
        
        # If evaluation script is provided, run it
        if args.eval_script:
            print(f"\nRunning official evaluation script...")
            import subprocess
            try:
                result = subprocess.run([
                    'python', args.eval_script,
                    '-g', args.ground_truth,
                    '-s', predictions_output
                ], capture_output=True, text=True)
                print("Evaluation output:")
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
            except Exception as e:
                print(f"Error running evaluation script: {e}")
        
        return
    
    if args.parser:
        # Benchmark specific parser
        print(f"Benchmarking {args.parser} parser...")
        results = benchmarker.benchmark_parser(args.ground_truth, args.documents, args.parser)
        all_results = {args.parser: results}
    else:
        # Benchmark all parsers
        print("Benchmarking all available parsers...")
        all_results = benchmarker.benchmark_all_parsers(args.ground_truth, args.documents)
    
    # Print results
    benchmarker.print_results(all_results)
    
    # Save results
    benchmarker.save_results(all_results, args.output)
    
    print("\nBenchmarking complete!")


if __name__ == "__main__":
    main() 