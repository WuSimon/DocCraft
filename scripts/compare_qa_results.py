#!/usr/bin/env python3
"""
Compare DocVQA questions, ground truths, and predicted answers.
"""

import json
from pathlib import Path
from tabulate import tabulate

def load_ground_truth(gt_file):
    """Load ground truth data."""
    with open(gt_file, 'r') as f:
        data = json.load(f)
    return data['data']

def load_predictions(pred_file):
    """Load predictions data."""
    with open(pred_file, 'r') as f:
        data = json.load(f)
    return data

def compare_qa_results(gt_file, pred_file):
    """Compare ground truth and predictions."""
    
    # Load data
    gt_data = load_ground_truth(gt_file)
    pred_data = load_predictions(pred_file)
    
    # Create a mapping from question_id to prediction
    pred_map = {pred['question_id']: pred for pred in pred_data}
    
    # Prepare table data
    table_data = []
    
    for item in gt_data:
        question_id = item['question_id']
        question = item['question']
        
        # Get ground truth answers
        gt_answers = item.get('answer', [])
        if isinstance(gt_answers, str):
            gt_answers = [gt_answers]
        gt_answers = [str(ans) for ans in gt_answers]  # Ensure all are strings
        gt_answer_str = '; '.join(gt_answers) if gt_answers else 'N/A'
        
        # Get predicted answer
        pred = pred_map.get(question_id, {})
        pred_answers = pred.get('answer', [])
        if isinstance(pred_answers, str):
            pred_answers = [pred_answers]
        pred_answers = [str(ans) for ans in pred_answers]  # Ensure all are strings
        pred_answer_str = '; '.join(pred_answers) if pred_answers else 'N/A'
        
        # Get evidence scores
        evidence_scores = pred.get('evidence', [])
        avg_evidence = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0.0
        
        table_data.append([
            question_id,
            question,
            gt_answer_str,
            pred_answer_str,
            f"{avg_evidence:.3f}"
        ])
    
    # Create table
    headers = ['ID', 'Question', 'Ground Truth', 'Predicted Answer', 'Avg Evidence']
    table = tabulate(table_data, headers=headers, tablefmt='grid', maxcolwidths=[5, 30, 25, 25, 10])
    
    print("DocVQA Question-Answer Comparison")
    print("=" * 80)
    print(table)
    
    # Summary statistics
    print(f"\nSummary:")
    print(f"Total questions: {len(gt_data)}")
    print(f"Questions with predictions: {len(pred_map)}")
    
    # Count non-empty predictions
    non_empty_preds = sum(1 for pred in pred_data if pred.get('answer') and pred['answer'] != [''])
    print(f"Non-empty predictions: {non_empty_preds}")
    print(f"Answer success rate: {non_empty_preds/len(gt_data)*100:.1f}%")

if __name__ == "__main__":
    gt_file = "doccraft/tests/test_files/docvqa/sample_public_v02.json"
    pred_file = "doccraft/layoutlmv3_predictions.json"
    
    if Path(gt_file).exists() and Path(pred_file).exists():
        compare_qa_results(gt_file, pred_file)
    else:
        print(f"Files not found:")
        print(f"  Ground truth: {Path(gt_file).exists()}")
        print(f"  Predictions: {Path(pred_file).exists()}") 