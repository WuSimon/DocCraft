#!/usr/bin/env python3
"""
Check LayoutLMv3 benchmark results.
"""

import json
from pathlib import Path

def analyze_predictions(predictions_file, ground_truth_file):
    """Analyze the predictions and calculate basic metrics."""
    
    # Load predictions
    with open(predictions_file, 'r') as f:
        predictions = json.load(f)
    
    # Load ground truth
    with open(ground_truth_file, 'r') as f:
        ground_truth = json.load(f)
    
    print(f"Total predictions: {len(predictions)}")
    print(f"Total ground truth questions: {len(ground_truth['data'])}")
    
    # Analyze answers
    empty_answers = 0
    non_empty_answers = 0
    total_evidence_score = 0
    
    for pred in predictions:
        if not pred.get('answer') or pred['answer'] == [''] or pred['answer'] == ['']:
            empty_answers += 1
        else:
            non_empty_answers += 1
        
        # Calculate average evidence score
        evidence = pred.get('evidence', [])
        if evidence:
            total_evidence_score += sum(evidence) / len(evidence)
    
    print(f"\nAnswer Analysis:")
    print(f"Empty answers: {empty_answers}")
    print(f"Non-empty answers: {non_empty_answers}")
    print(f"Answer success rate: {non_empty_answers / len(predictions) * 100:.2f}%")
    
    print(f"\nEvidence Analysis:")
    print(f"Average evidence score: {total_evidence_score / len(predictions):.4f}")
    
    # Check a few sample predictions
    print(f"\nSample Predictions:")
    for i in range(min(5, len(predictions))):
        pred = predictions[i]
        print(f"Question {pred['question_id']}:")
        print(f"  Answer: {pred.get('answer', 'N/A')}")
        print(f"  Evidence score: {sum(pred.get('evidence', [])) / len(pred.get('evidence', [1])):.4f}")
        print()

if __name__ == "__main__":
    predictions_file = "doccraft/layoutlmv3_predictions.json"
    ground_truth_file = "doccraft/tests/test_files/docvqa/sample_public_v02.json"
    
    if Path(predictions_file).exists() and Path(ground_truth_file).exists():
        analyze_predictions(predictions_file, ground_truth_file)
    else:
        print(f"Files not found:")
        print(f"  Predictions: {Path(predictions_file).exists()}")
        print(f"  Ground truth: {Path(ground_truth_file).exists()}") 