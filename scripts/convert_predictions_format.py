#!/usr/bin/env python3
"""
Convert predictions format for evaluation.
"""

import json
import sys

if len(sys.argv) != 3:
    print("Usage: python convert_predictions_format.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r') as f:
    data = json.load(f)

# Extract and reformat answers
flat_answers = []
for entry in data.get('answers', []):
    flat_answers.append({
        'questionId': entry['question_id'],
        'predicted_answer': entry['predicted_answer']
    })

with open(output_file, 'w') as f:
    json.dump(flat_answers, f, indent=2)

print(f"Converted predictions saved to: {output_file}") 