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
        'question_details': []
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
        
        # Normalize answers
        gt_normalized = normalize_text(gt_answer)
        pred_normalized = normalize_text(pred_answer)
        
        # Calculate similarity
        similarity = calculate_similarity(gt_normalized, pred_normalized)
        total_similarity += similarity
        
        # Categorize results
        if gt_answer == pred_answer:
            results['exact_matches'] += 1
        elif gt_normalized == pred_normalized:
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
            'normalized_match': gt_normalized == pred_normalized
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


def main():
    parser = argparse.ArgumentParser(description="Evaluate DocVQA Task 1 predictions")
    parser.add_argument('--ground_truth', '-g', required=True,
                       help="Path to ground truth JSON file")
    parser.add_argument('--predictions', '-p', required=True,
                       help="Path to predictions JSON file")
    parser.add_argument('--output', '-o',
                       help="Path to save detailed results JSON file")
    
    args = parser.parse_args()
    
    # Evaluate predictions
    results = evaluate_predictions(args.ground_truth, args.predictions)
    
    # Print results
    print_results(results)
    
    # Save detailed results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")


if __name__ == "__main__":
    main() 