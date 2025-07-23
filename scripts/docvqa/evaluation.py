#!/usr/bin/env python3
"""
Simple evaluation script for DocVQA Task 1 predictions.

This script evaluates predictions by comparing predicted answers with ground truth answers.
For Task 1, we use simple string matching and similarity metrics.
"""

import json
import argparse
import re
from typing import Dict, List, Any
from difflib import SequenceMatcher
from num2words import num2words
import inflect
p = inflect.engine()


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove punctuation (keep alphanumeric and spaces)
    text = re.sub(r'[^\w\s]', '', text)
    
    return text

def get_normalized_forms(text: str) -> set:
    """Return a set of normalized forms, including numeric and written forms if applicable."""
    forms = set()
    norm = normalize_text(text)
    forms.add(norm)
    # Try to add numeric <-> word forms
    # If norm is a number, add its word form
    try:
        # Remove commas for thousands
        num = float(norm.replace(",", ""))
        # Integer or float
        if num.is_integer():
            word = num2words(int(num))
        else:
            word = num2words(num)
        forms.add(normalize_text(word))
    except Exception:
        pass
    # If norm is a word, try to parse as number
    try:
        # inflect can parse written numbers to numeric
        num = p.number_to_words(norm)
        if num != norm:
            # Try to parse the result as a number
            num_val = float(num.replace(",", ""))
            forms.add(normalize_text(str(int(num_val)) if num_val.is_integer() else str(num_val)))
    except Exception:
        pass
    return forms


def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity between two strings."""
    if not str1 or not str2:
        return 0.0
    
    return SequenceMatcher(None, str1, str2).ratio()


def evaluate_predictions(ground_truth_path: str, predictions_path: str) -> Dict[str, Any]:
    """
    Evaluate predictions against ground truth.
    
    Args:
        ground_truth_path: Path to ground truth JSON file
        predictions_path: Path to predictions JSON file
    
    Returns:
        Dictionary with evaluation metrics
    """
    print("Loading ground truth and predictions...")
    
    # Load ground truth
    with open(ground_truth_path, 'r') as f:
        gt_data = json.load(f)
    
    # Load predictions
    with open(predictions_path, 'r') as f:
        predictions = json.load(f)
    
    # Create lookup for predictions
    pred_lookup = {pred['questionId']: pred for pred in predictions}
    
    print(f"Evaluating {len(gt_data['data'])} questions...")
    
    results = {
        'total_questions': len(gt_data['data']),
        'evaluated_questions': 0,
        'exact_matches': 0,
        'normalized_matches': 0,
        'high_similarity': 0,
        'medium_similarity': 0,
        'low_similarity': 0,
        'no_match': 0,
        'average_similarity': 0.0,
        'question_details': [],
        'matches_total': 0,
        'best_matches': [],
        'worst_matches': [],
    }
    
    total_similarity = 0.0
    
    for gt_item in gt_data['data']:
        question_id = gt_item['questionId']
        
        if question_id not in pred_lookup:
            print(f"Warning: No prediction found for question {question_id}")
            continue
        
        pred_item = pred_lookup[question_id]
        
        # Get answers
        gt_answer = gt_item.get('answers', [''])[0] if gt_item.get('answers') else ''
        pred_answer = pred_item.get('predicted_answer', '')
        
        # Enhanced normalization: numeric and written forms
        gt_forms = get_normalized_forms(gt_answer)
        pred_forms = get_normalized_forms(pred_answer)
        # Calculate similarity using the main normalized form
        gt_normalized = normalize_text(gt_answer)
        pred_normalized = normalize_text(pred_answer)
        similarity = calculate_similarity(gt_normalized, pred_normalized)
        total_similarity += similarity
        # Categorize results
        if gt_answer == pred_answer:
            results['exact_matches'] += 1
        elif gt_forms & pred_forms:
            results['normalized_matches'] += 1
        if similarity >= 0.8:
            results['high_similarity'] += 1
        elif similarity >= 0.5:
            results['medium_similarity'] += 1
        elif similarity >= 0.2:
            results['low_similarity'] += 1
        else:
            results['no_match'] += 1
        # Store details
        results['question_details'].append({
            'question_id': question_id,
            'question': gt_item['question'],
            'ground_truth': gt_answer,
            'predicted': pred_answer,
            'similarity': similarity,
            'exact_match': gt_answer == pred_answer,
            'normalized_match': bool(gt_forms & pred_forms)
        })
        results['evaluated_questions'] += 1
    
    # Calculate average similarity
    if results['evaluated_questions'] > 0:
        results['average_similarity'] = total_similarity / results['evaluated_questions']
    
    # Calculate percentages
    total = results['evaluated_questions']
    if total > 0:
        results['exact_match_rate'] = results['exact_matches'] / total
        results['normalized_match_rate'] = results['normalized_matches'] / total
        results['high_similarity_rate'] = results['high_similarity'] / total
        results['medium_similarity_rate'] = results['medium_similarity'] / total
        results['low_similarity_rate'] = results['low_similarity'] / total
        results['no_match_rate'] = results['no_match'] / total
        results['matches_total'] = results['exact_matches'] + results['normalized_matches']
    
    # Sort question_details for best/worst matches
    results['question_details'].sort(key=lambda x: x['similarity'], reverse=True)
    results['best_matches'] = results['question_details'][:5]
    results['worst_matches'] = results['question_details'][-5:]
    
    return results


def print_results(results: Dict[str, Any]):
    """Print evaluation results in a formatted way."""
    print("\n" + "="*60)
    print("DOCVQA TASK 1 EVALUATION RESULTS")
    print("="*60)
    
    print(f"Total Questions: {results['total_questions']}")
    print(f"Evaluated Questions: {results['evaluated_questions']}")
    print(f"Average Similarity: {results['average_similarity']:.3f}")
    print()
    
    print("MATCHING RESULTS:")
    print(f"  Exact Matches: {results['exact_matches']} ({results.get('exact_match_rate', 0):.1%})")
    print(f"  Normalized Matches: {results['normalized_matches']} ({results.get('normalized_match_rate', 0):.1%})")
    print(f"  Matches Total (Exact + Normalized): {results['matches_total']} ({(results['matches_total']/results['total_questions']):.1%})")
    print()
    
    print("SIMILARITY BREAKDOWN:")
    print(f"  High Similarity (≥0.8): {results['high_similarity']} ({results.get('high_similarity_rate', 0):.1%})")
    print(f"  Medium Similarity (≥0.5): {results['medium_similarity']} ({results.get('medium_similarity_rate', 0):.1%})")
    print(f"  Low Similarity (≥0.2): {results['low_similarity']} ({results.get('low_similarity_rate', 0):.1%})")
    print(f"  No Match (<0.2): {results['no_match']} ({results.get('no_match_rate', 0):.1%})")
    print()
    
    # Show some examples
    print("SAMPLE RESULTS:")
    print("-" * 60)
    
    # Show best matches
    best_matches = sorted(results['question_details'], key=lambda x: x['similarity'], reverse=True)[:5]
    print("Top 5 Best Matches:")
    for i, item in enumerate(best_matches, 1):
        print(f"{i}. Q{item['question_id']}: Similarity {item['similarity']:.3f}")
        print(f"   GT: {item['ground_truth']}")
        print(f"   PR: {item['predicted']}")
        print()
    
    # Show worst matches
    worst_matches = sorted(results['question_details'], key=lambda x: x['similarity'])[:5]
    print("Top 5 Worst Matches:")
    for i, item in enumerate(worst_matches, 1):
        print(f"{i}. Q{item['question_id']}: Similarity {item['similarity']:.3f}")
        print(f"   GT: {item['ground_truth']}")
        print(f"   PR: {item['predicted']}")
        print()


def evaluate_multiple_predictions(ground_truth_path: str, predictions_paths: list) -> list:
    """Evaluate multiple prediction files and return a list of results with metrics."""
    all_results = []
    for pred_path in predictions_paths:
        print(f"\nEvaluating: {pred_path}")
        results = evaluate_predictions(ground_truth_path, pred_path)
        results['file'] = pred_path
        all_results.append(results)
    return all_results

def print_comparison_table(all_results: list):
    """Print a table comparing main metrics for all evaluated files."""
    print("\n" + "="*60)
    print("DOCVQA TASK 1 BENCHMARK COMPARISON")
    print("="*60)
    header = f"{'File':40}  {'Exact':>7}  {'Norm':>7}  {'Total':>7}  {'AvgSim':>7}  {'High':>7}  {'Med':>7}  {'Low':>7}  {'NoMatch':>7}"
    print(header)
    print("-"*len(header))
    for res in all_results:
        print(f"{res['file'][:40]:40}  {res.get('exact_match_rate',0):7.2%}  {res.get('normalized_match_rate',0):7.2%}  {(res.get('exact_match_rate',0)+res.get('normalized_match_rate',0)):7.2%}  {res.get('average_similarity',0):7.3f}  {res.get('high_similarity_rate',0):7.2%}  {res.get('medium_similarity_rate',0):7.2%}  {res.get('low_similarity_rate',0):7.2%}  {res.get('no_match_rate',0):7.2%}")

def main():
    parser = argparse.ArgumentParser(description="Evaluate DocVQA Task 1 predictions (supports multiple predictions files)")
    parser.add_argument('--ground_truth', '-g', required=True,
                       help="Path to ground truth JSON file")
    parser.add_argument('--predictions', '-p', required=True, nargs='+',
                       help="Path(s) to predictions JSON file(s)")
    parser.add_argument('--output', '-o',
                       help="Path to save detailed results JSON file")
    parser.add_argument('--summary_output', '-s',
                       help="Path to save summary table JSON file (main metrics only)")
    args = parser.parse_args()
    if len(args.predictions) == 1:
        # Single file: behave as before
        results = evaluate_predictions(args.ground_truth, args.predictions[0])
        results['file'] = args.predictions[0]  # Ensure 'file' key is present
        print_comparison_table([results])
        print_results(results)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nDetailed results saved to: {args.output}")
        if args.summary_output:
            summary = [{
                'file': results['file'],
                'exact_match_rate': results.get('exact_match_rate', 0),
                'normalized_match_rate': results.get('normalized_match_rate', 0),
                'total_match_rate': results.get('exact_match_rate', 0) + results.get('normalized_match_rate', 0),
                'average_similarity': results.get('average_similarity', 0),
                'high_similarity_rate': results.get('high_similarity_rate', 0),
                'medium_similarity_rate': results.get('medium_similarity_rate', 0),
                'low_similarity_rate': results.get('low_similarity_rate', 0),
                'no_match_rate': results.get('no_match_rate', 0),
            }]
            with open(args.summary_output, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\nSummary table saved to: {args.summary_output}")
    else:
        # Multiple files: print comparison table first, then per-file details
        all_results = evaluate_multiple_predictions(args.ground_truth, args.predictions)
        print_comparison_table(all_results)
        for res in all_results:
            print(f"\n{'='*60}\nResults for: {res['file']}\n{'='*60}")
            print_results(res)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"\nDetailed results saved to: {args.output}")
        if args.summary_output:
            summary = []
            for res in all_results:
                summary.append({
                    'file': res['file'],
                    'exact_match_rate': res.get('exact_match_rate', 0),
                    'normalized_match_rate': res.get('normalized_match_rate', 0),
                    'total_match_rate': res.get('exact_match_rate', 0) + res.get('normalized_match_rate', 0),
                    'average_similarity': res.get('average_similarity', 0),
                    'high_similarity_rate': res.get('high_similarity_rate', 0),
                    'medium_similarity_rate': res.get('medium_similarity_rate', 0),
                    'low_similarity_rate': res.get('low_similarity_rate', 0),
                    'no_match_rate': res.get('no_match_rate', 0),
                })
            with open(args.summary_output, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\nSummary table saved to: {args.summary_output}")


if __name__ == "__main__":
    main() 