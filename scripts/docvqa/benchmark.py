#!/usr/bin/env python3
"""
DocVQA Comprehensive Benchmarking Script

This script provides comprehensive benchmarking of DocCraft parsers on the DocVQA dataset.
It includes evaluation metrics, detailed reporting, and various output formats.

Usage:
    python benchmark.py --ground_truth path/to/gt.json --documents path/to/documents
    python benchmark.py --ground_truth path/to/gt.json --documents path/to/documents --parser layoutlmv3 --max_questions 100
    python benchmark.py --ground_truth path/to/gt.json --documents path/to/documents --all_parsers --output-dir results/
"""

import json
import argparse
import os
import warnings
import time
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path
import pandas as pd
from datetime import datetime

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*image_processor_class.*")
warnings.filterwarnings("ignore", message=".*use_fast.*")
warnings.filterwarnings("ignore", message=".*legacy.*")
warnings.filterwarnings("ignore", message=".*device.*")

# Set environment variables to suppress tokenizer warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Import the unified DocVQABenchmarker
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'src'))
from doccraft.benchmarking.docvqa_benchmarker import DocVQABenchmarker


def calculate_metrics(predictions: List[Dict], ground_truth: Dict) -> Dict[str, float]:
    """Calculate evaluation metrics for DocVQA Task 1."""
    total_questions = len(predictions)
    exact_matches = 0
    partial_matches = 0
    
    for pred in predictions:
        question_id = pred['questionId']
        predicted_answer = pred['predicted_answer'].lower().strip()
        
        # Find corresponding ground truth
        gt_entry = None
        for item in ground_truth['data']:
            if item['questionId'] == question_id:
                gt_entry = item
                break
        
        if gt_entry:
            gt_answers = [ans.lower().strip() for ans in gt_entry['answer']]
            
            # Check for exact match
            if predicted_answer in gt_answers:
                exact_matches += 1
                partial_matches += 1
            # Check for partial match (substring)
            elif any(predicted_answer in gt_ans or gt_ans in predicted_answer for gt_ans in gt_answers):
                partial_matches += 1
    
    return {
        'exact_match_accuracy': exact_matches / total_questions if total_questions > 0 else 0,
        'partial_match_accuracy': partial_matches / total_questions if total_questions > 0 else 0,
        'total_questions': total_questions,
        'exact_matches': exact_matches,
        'partial_matches': partial_matches
    }


def generate_report(results: Dict[str, Any], output_dir: str, parser_name: str) -> None:
    """Generate comprehensive benchmark report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw results
    results_file = os.path.join(output_dir, f"{parser_name}_results_{timestamp}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create detailed CSV report
    if 'answers' in results:
        df_data = []
        for ans in results['answers']:
            df_data.append({
                'question_id': ans['questionId'],
                'question': ans['question'],
                'predicted_answer': ans['predicted_answer'],
                'confidence': ans.get('confidence', 0.0),
                'image': ans.get('image', ''),
                'processing_time': ans.get('processing_time', 0.0)
            })
        
        df = pd.DataFrame(df_data)
        csv_file = os.path.join(output_dir, f"{parser_name}_detailed_results_{timestamp}.csv")
        df.to_csv(csv_file, index=False)
        
        # Generate summary statistics
        summary = {
            'parser': parser_name,
            'timestamp': timestamp,
            'total_questions': len(df),
            'average_confidence': df['confidence'].mean(),
            'average_processing_time': df['processing_time'].mean(),
            'total_processing_time': df['processing_time'].sum()
        }
        
        # Add metrics if available
        if 'metrics' in results:
            summary.update(results['metrics'])
        
        summary_file = os.path.join(output_dir, f"{parser_name}_summary_{timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nResults saved to:")
        print(f"  - Raw results: {results_file}")
        print(f"  - Detailed CSV: {csv_file}")
        print(f"  - Summary: {summary_file}")


def compare_parsers(results_dict: Dict[str, Dict], output_dir: str) -> None:
    """Compare results across multiple parsers."""
    comparison_data = []
    
    for parser_name, results in results_dict.items():
        if 'metrics' in results:
            metrics = results['metrics']
            comparison_data.append({
                'parser': parser_name,
                'exact_match_accuracy': metrics.get('exact_match_accuracy', 0),
                'partial_match_accuracy': metrics.get('partial_match_accuracy', 0),
                'total_questions': metrics.get('total_questions', 0),
                'average_confidence': results.get('average_confidence', 0),
                'average_processing_time': results.get('average_processing_time', 0)
            })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_file = os.path.join(output_dir, f"parser_comparison_{timestamp}.csv")
        df.to_csv(comparison_file, index=False)
        
        print(f"\nParser comparison saved to: {comparison_file}")
        print("\nParser Comparison Summary:")
        print(df.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive DocVQA benchmarking with DocCraft parsers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Benchmark single parser
  python benchmark.py -g gt.json -d documents/ -p layoutlmv3
  
  # Benchmark all parsers
  python benchmark.py -g gt.json -d documents/ -a
  
  # Quick test with limited questions
  python benchmark.py -g gt.json -d documents/ -p tesseract --max_questions 50
  
  # Generate detailed report
  python benchmark.py -g gt.json -d documents/ -p deepseekvl --output-dir results/
        """
    )
    
    # Required arguments
    parser.add_argument('--ground_truth', '-g', required=True,
                       help="Path to DocVQA Task 1 ground truth JSON file")
    parser.add_argument('--documents', '-d', required=True,
                       help="Directory containing document images")
    
    # Optional arguments
    parser.add_argument('--parser', '-p', default='layoutlmv3',
                       choices=['layoutlmv3', 'deepseekvl', 'qwenvl', 'tesseract', 'paddleocr', 'pdfplumber'],
                       help="Parser to use (default: layoutlmv3)")
    parser.add_argument('--all_parsers', '-a', action='store_true',
                       help="Benchmark all available parsers")
    parser.add_argument('--max_questions', type=int,
                       help="Maximum number of questions to process (for testing)")
    parser.add_argument('--output_dir', '-o', default='results',
                       help="Output directory for results (default: results)")
    parser.add_argument('--verbose', '-v', action='store_true',
                       help="Enable verbose output")
    parser.add_argument('--save_predictions', action='store_true',
                       help="Save individual predictions to separate files")
    parser.add_argument('--compare', action='store_true',
                       help="Generate comparison report when using --all_parsers")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.ground_truth):
        print(f"Error: Ground truth file not found: {args.ground_truth}")
        return 1
    if not os.path.exists(args.documents):
        print(f"Error: Documents directory not found: {args.documents}")
        return 1
    
    # Load ground truth for evaluation
    try:
        with open(args.ground_truth, 'r') as f:
            ground_truth = json.load(f)
        print(f"Loaded ground truth with {len(ground_truth.get('data', []))} questions")
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return 1
    
    benchmarker = DocVQABenchmarker()
    
    print(f"\n{'='*80}")
    print(f"DOCVQA TASK 1 BENCHMARK")
    print(f"{'='*80}")
    print(f"Ground truth: {args.ground_truth}")
    print(f"Documents: {args.documents}")
    print(f"Max questions: {args.max_questions or 'All'}")
    print(f"Output directory: {args.output_dir}")
    
    if args.all_parsers:
        print(f"Benchmarking all available parsers...")
        parsers = ['layoutlmv3', 'deepseekvl', 'qwenvl', 'tesseract', 'paddleocr', 'pdfplumber']
        all_results = {}
        
        for parser_name in parsers:
            try:
                print(f"\n--- Benchmarking {parser_name.upper()} ---")
                start_time = time.time()
                
                results = benchmarker.benchmark(
                    args.ground_truth, args.documents, parser_name, args.max_questions
                )
                
                # Calculate metrics
                if 'answers' in results:
                    metrics = calculate_metrics(results['answers'], ground_truth)
                    results['metrics'] = metrics
                    
                    # Calculate average confidence and processing time
                    if results['answers']:
                        confidences = [ans.get('confidence', 0) for ans in results['answers']]
                        processing_times = [ans.get('processing_time', 0) for ans in results['answers']]
                        results['average_confidence'] = sum(confidences) / len(confidences)
                        results['average_processing_time'] = sum(processing_times) / len(processing_times)
                
                all_results[parser_name] = results
                
                # Generate individual report
                generate_report(results, args.output_dir, parser_name)
                
                elapsed_time = time.time() - start_time
                print(f"Completed in {elapsed_time:.2f} seconds")
                
                if args.verbose and 'metrics' in results:
                    metrics = results['metrics']
                    print(f"  Exact Match Accuracy: {metrics['exact_match_accuracy']:.3f}")
                    print(f"  Partial Match Accuracy: {metrics['partial_match_accuracy']:.3f}")
                
            except Exception as e:
                print(f"Error benchmarking {parser_name}: {e}")
                continue
        
        if args.compare:
            compare_parsers(all_results, args.output_dir)
    
    else:
        print(f"\n--- Benchmarking {args.parser.upper()} ---")
        start_time = time.time()
        
        try:
            results = benchmarker.benchmark(
                args.ground_truth, args.documents, args.parser, args.max_questions
            )
            
            # Calculate metrics
            if 'answers' in results:
                metrics = calculate_metrics(results['answers'], ground_truth)
                results['metrics'] = metrics
                
                # Calculate averages
                if results['answers']:
                    confidences = [ans.get('confidence', 0) for ans in results['answers']]
                    processing_times = [ans.get('processing_time', 0) for ans in results['answers']]
                    results['average_confidence'] = sum(confidences) / len(confidences)
                    results['average_processing_time'] = sum(processing_times) / len(processing_times)
            
            # Generate report
            generate_report(results, args.output_dir, args.parser)
            
            elapsed_time = time.time() - start_time
            print(f"\nBenchmark completed in {elapsed_time:.2f} seconds")
            
            if 'metrics' in results:
                metrics = results['metrics']
                print(f"\nResults Summary:")
                print(f"  Total Questions: {metrics['total_questions']}")
                print(f"  Exact Match Accuracy: {metrics['exact_match_accuracy']:.3f}")
                print(f"  Partial Match Accuracy: {metrics['partial_match_accuracy']:.3f}")
                print(f"  Average Confidence: {results.get('average_confidence', 0):.3f}")
                print(f"  Average Processing Time: {results.get('average_processing_time', 0):.3f}s")
        
        except Exception as e:
            print(f"Error during benchmarking: {e}")
            return 1
    
    print(f"\n{'='*80}")
    print(f"BENCHMARK COMPLETED")
    print(f"{'='*80}")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 