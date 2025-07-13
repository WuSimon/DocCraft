import json

# Paths
PRED_PATH = "layoutlmv3_predictions.json"
GT_PATH = "../doccraft/tests/test_files/docvqa/sample_public_v02.json"

# Load predictions
with open(PRED_PATH, "r") as f:
    preds = json.load(f)

# Load ground truth
with open(GT_PATH, "r") as f:
    gt_data = json.load(f)["data"]

# Build a lookup for predictions by question_id
pred_lookup = {p["question_id"]: p for p in preds}

print("\n--- LayoutLMv3 Predictions vs Ground Truths ---\n")
for item in gt_data:
    qid = item["question_id"]
    question = item["question"]
    gt_answers = item.get("answer", [])
    if isinstance(gt_answers, str):
        gt_answers = [gt_answers]
    pred = pred_lookup.get(qid, {})
    pred_answer = pred.get("answer", [""])
    if isinstance(pred_answer, list):
        pred_answer = ", ".join(pred_answer)
    print(f"Q{qid}: {question}")
    print(f"  Ground Truth: {gt_answers}")
    print(f"  Prediction  : {pred_answer}")
    print("-") 