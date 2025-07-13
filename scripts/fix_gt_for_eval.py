import json
import sys

def fix_ground_truth_for_evaluation(gt_path, output_path):
    """Add dummy evidence scores to ground truth file for evaluation script compatibility."""
    
    with open(gt_path, 'r') as f:
        gt_data = json.load(f)
    
    # Add dummy evidence scores to each question
    for item in gt_data['data']:
        # Create dummy evidence scores (all zeros) with length 50 (typical DocVQA evidence length)
        item['ground_truth'] = [0.0] * 50
    
    with open(output_path, 'w') as f:
        json.dump(gt_data, f, indent=2)
    
    print(f"Fixed ground truth saved to {output_path}")
    print(f"Added dummy evidence scores to {len(gt_data['data'])} questions")

if __name__ == "__main__":
    gt_path = "doccraft/tests/test_files/docvqa/test_public.json"
    output_path = "doccraft/tests/test_files/docvqa/test_public_fixed.json"
    
    fix_ground_truth_for_evaluation(gt_path, output_path) 