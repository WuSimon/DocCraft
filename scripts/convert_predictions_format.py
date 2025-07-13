#!/usr/bin/env python3
"""
Convert predictions format for evaluation.
"""

import json
import argparse

def convert_predictions_format(input_path: str, output_path: str):
    """Convert predictions from wrapped format to simple array format."""
    
    # Load the wrapped predictions
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    # Extract just the answers array and fix field names
    predictions = []
    for pred in data['answers']:
        # Create new prediction with correct field names
        new_pred = {
            'questionId': pred['question_id'],  # Rename field
            'question': pred['question'],
            'image': pred['image'],
            'predicted_answer': pred['predicted_answer'],
            'confidence': pred['confidence'],
            'extracted_text': pred.get('extracted_text', '')
        }
        predictions.append(new_pred)
    
    # Save in the expected format (simple array)
    with open(output_path, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"Converted {len(predictions)} predictions from {input_path} to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert predictions format")
    parser.add_argument('--input', '-i', required=True, help="Input predictions file")
    parser.add_argument('--output', '-o', required=True, help="Output predictions file")
    
    args = parser.parse_args()
    convert_predictions_format(args.input, args.output)

if __name__ == "__main__":
    main() 