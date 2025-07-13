import json
import pandas as pd

def load_ground_truth(gt_path):
    """Load ground truth data and extract questions, answers, and image names."""
    with open(gt_path, 'r') as f:
        gt_data = json.load(f)
    
    results = []
    for item in gt_data['data']:
        # Try to extract image name from evidence or a dedicated field
        # Here, we assume 'evidence' is a list of dicts with 'image_id' or similar
        # If not, adjust as needed
        image_name = None
        if 'evidence' in item and item['evidence']:
            # Try to get the first image name from evidence
            if isinstance(item['evidence'][0], dict) and 'image_id' in item['evidence'][0]:
                image_name = item['evidence'][0]['image_id']
            elif isinstance(item['evidence'][0], str):
                image_name = item['evidence'][0]
        results.append({
            'question_id': item['question_id'],
            'question': item['question'],
            'ground_truth_answer': item['answer'][0] if item['answer'] else 'No answer',
            'image_name': image_name or 'Unknown'
        })
    
    return results

def load_predictions(pred_path):
    """Load predictions data and extract answers."""
    with open(pred_path, 'r') as f:
        pred_data = json.load(f)
    
    results = {}
    for item in pred_data:  # pred_data is a list, not a dict with 'data' key
        results[item['question_id']] = item['answer'][0] if item['answer'] else 'No answer'
    
    return results

def main():
    # Load data
    gt_path = "doccraft/tests/test_files/docvqa/Task 2/gt/.ipynb_checkpoints/gt-checkpoint.json"
    pred_path = "layoutlmv3_predictions.json"
    
    gt_data = load_ground_truth(gt_path)
    pred_data = load_predictions(pred_path)
    
    # Create comparison table
    comparison = []
    for gt_item in gt_data:
        question_id = gt_item['question_id']
        comparison.append({
            'Question ID': question_id,
            'Image Name': gt_item['image_name'],
            'Question': gt_item['question'],
            'Ground Truth Answer': gt_item['ground_truth_answer'],
            'Predicted Answer': pred_data.get(question_id, 'No prediction')
        })
    
    # Create DataFrame
    df = pd.DataFrame(comparison)
    
    # Output as markdown table
    print("| Question ID | Image Name | Question | Ground Truth Answer | Predicted Answer |")
    print("|-------------|------------|----------|---------------------|------------------|")
    for _, row in df.iterrows():
        q = str(row['Question']).replace("|", "\\|").replace("\n", " ")
        gt = str(row['Ground Truth Answer']).replace("|", "\\|")
        pred = str(row['Predicted Answer']).replace("|", "\\|")
        print(f"| {row['Question ID']} | {row['Image Name']} | {q} | {gt} | {pred} |")

if __name__ == "__main__":
    main() 