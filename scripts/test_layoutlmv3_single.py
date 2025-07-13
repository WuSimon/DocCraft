from doccraft.parsers import LayoutLMv3Parser
from PIL import Image
import numpy as np
import os

def print_ocr_output(parser, image_path):
    img = Image.open(image_path)
    words, boxes = parser._extract_ocr_text_and_boxes(img)
    print("\n--- OCR Output ---")
    for w, b in zip(words, boxes):
        print(f"  Word: {w:20} Box: {b}")
    print(f"Total words: {len(words)}")

def main():
    # Use a real DocVQA image and question
    image_path = "../doccraft/tests/test_files/docvqa/images/9733.jpg"
    question = "What is the name of the company?"
    
    print(f"Image: {image_path}")
    print(f"Question: {question}")
    
    parser = LayoutLMv3Parser()
    print_ocr_output(parser, image_path)
    
    result = parser.ask_question(image_path, question)
    print("\n--- Model Prediction ---")
    print(f"Answer: {result.get('answer', '')}")
    print(f"Confidence: {result.get('confidence', 0.0)}")
    print(f"Raw result: {result}")

if __name__ == "__main__":
    main() 