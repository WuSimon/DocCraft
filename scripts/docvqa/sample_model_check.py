import json
import os
from pathlib import Path

# Import the parser (adjust import as needed for your setup)
try:
    from doccraft.parsers.layoutlmv3_parser import LayoutLMv3Parser
except ImportError:
    print("Warning: Could not import LayoutLMv3Parser. Please check your environment.")
    LayoutLMv3Parser = None

def main():
    gt_path = "tests/data/docvqa/spdocvqa_qas/val_v1.0_withQT.json"
    images_dir = "tests/data/docvqa/spdocvqa_images"
    num_samples = 3  # Reduced for detailed debugging

    with open(gt_path, 'r') as f:
        gt_data = json.load(f)
    
    questions = gt_data['data'][:num_samples]

    if LayoutLMv3Parser is None:
        print("Model not available. Exiting.")
        return

    parser = LayoutLMv3Parser()

    for i, item in enumerate(questions, 1):
        image_path = item['image']
        if image_path.startswith('documents/'):
            image_path = image_path.replace('documents/', '')
        full_image_path = os.path.join(images_dir, image_path)
        
        question = item['question']
        gt_answers = item.get('answers', [])
        
        if not os.path.exists(full_image_path):
            print(f"Image not found: {full_image_path}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Sample {i}")
        print(f"Image: {image_path}")
        print(f"Question: {question}")
        print(f"Ground Truth Answers: {gt_answers}")
        print(f"{'='*60}")
        
        # Run the model and get detailed output
        try:
            result = parser.ask_question(full_image_path, question)
            prediction = result.get('answer', 'No answer')
            raw_answer = result.get('raw_answer', 'No raw answer')
            
            print(f"Model Prediction: {prediction}")
            print(f"Raw Answer: {raw_answer}")
            
            # Print detailed debugging info if available
            if 'predictions' in result:
                predictions = result['predictions']
                print(f"\nDEBUG INFO:")
                print(f"  Answer Start: {predictions.get('answer_start', 'N/A')}")
                print(f"  Answer End: {predictions.get('answer_end', 'N/A')}")
                print(f"  Logits Shape: {len(predictions.get('logits', []))}")
                
                # Print first few logits to see if they're all the same
                logits = predictions.get('logits', [])
                if logits:
                    print(f"  First 10 logits: {logits[:10]}")
            else:
                print(f"\nDEBUG INFO:")
                print(f"  No 'predictions' field found in result")
                print(f"  Available keys: {list(result.keys())}")
                
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            
            # Print full result structure for debugging
            print(f"\nFULL RESULT STRUCTURE:")
            for key, value in result.items():
                if key == 'predictions' and isinstance(value, dict):
                    print(f"  {key}: {list(value.keys())}")
                else:
                    print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main() 