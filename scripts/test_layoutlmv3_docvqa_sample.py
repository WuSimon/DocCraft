import json
import os
from doccraft.parsers import LayoutLMv3Parser
from PIL import Image

def find_image_path(image_id, images_dir):
    """Find the actual image file for a given image_id."""
    for ext in [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"]:
        image_path = os.path.join(images_dir, f"{image_id}{ext}")
        if os.path.exists(image_path):
            return image_path
    return None

def main():
    # Load DocVQA sample data
    gt_path = "../doccraft/tests/test_files/docvqa/sample_public_v02.json"
    images_dir = "../doccraft/tests/test_files/docvqa/images"
    
    with open(gt_path, 'r') as f:
        data = json.load(f)["data"]
    
    parser = LayoutLMv3Parser()
    
    print("=== LayoutLMv3Parser with DocVQA Sample Questions ===\n")
    
    for i, item in enumerate(data[:5]):  # Test first 5 questions
        question_id = item["question_id"]
        question = item["question"]
        gt_answers = item.get("answer", [])
        if isinstance(gt_answers, str):
            gt_answers = [gt_answers]
        
        # Find the image
        image_id = item.get("image_id") or item.get("image") or str(question_id)
        image_path = find_image_path(image_id, images_dir)
        
        print(f"Question {i+1} (ID: {question_id}):")
        print(f"  Question: {question}")
        print(f"  Ground Truth: {gt_answers}")
        print(f"  Image ID: {image_id}")
        print(f"  Image Path: {image_path}")
        
        if image_path and os.path.exists(image_path):
            # Test OCR on this image
            img = Image.open(image_path)
            words, boxes = parser._extract_ocr_text_and_boxes(img)
            print(f"  OCR Words: {len(words)} words extracted")
            print(f"  First 5 words: {words[:5]}")
            
            # Get model prediction
            result = parser.ask_question(image_path, question)
            pred_answer = result.get('answer', '')
            confidence = result.get('confidence', 0.0)
            
            print(f"  Prediction: {pred_answer}")
            print(f"  Confidence: {confidence:.4f}")
        else:
            print(f"  ERROR: Image not found!")
        
        print("-" * 80)

if __name__ == "__main__":
    main() 