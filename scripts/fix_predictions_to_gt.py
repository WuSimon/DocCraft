import json
import sys
from pathlib import Path

# Paths (edit as needed)
gt_path = 'doccraft/tests/test_files/docvqa/test_public.json'
pred_path = 'doccraft/layoutlmv3_predictions.json'
out_path = 'doccraft/layoutlmv3_predictions_aligned.json'

# Load ground truth
with open(gt_path, 'r') as f:
    gt = json.load(f)
    gt_qids = [item['question_id'] for item in gt['data']]

# Load predictions
with open(pred_path, 'r') as f:
    preds = json.load(f)
    pred_by_qid = {p['question_id']: p for p in preds}

aligned = []
missing = []
empty_answers = []

for qid in gt_qids:
    pred = pred_by_qid.get(qid)
    if pred is None:
        missing.append(qid)
        continue
    # Check for empty answer
    ans = pred.get('answer', [])
    if isinstance(ans, str):
        ans = [ans]
    if not any(a.strip() for a in ans):
        empty_answers.append(qid)
    aligned.append(pred)

# Save aligned predictions
with open(out_path, 'w') as f:
    json.dump(aligned, f, indent=2)

print(f"Aligned predictions written to {out_path}")
if missing:
    print(f"Missing predictions for question_ids: {missing}")
if empty_answers:
    print(f"Predictions with empty answers for question_ids: {empty_answers}")
if not missing and not empty_answers:
    print("All predictions present and non-empty.") 