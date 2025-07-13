#!/usr/bin/env python3
"""
Test DeepSeek-VL parser on a few DocVQA questions
"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doccraft.parsers.deepseek_vl_parser import DeepSeekVLParser

def test_deepseek_vl():
    # Load test data
    with open('data/docvqa/val_v1.0_withQT.json', 'r') as f:
        data = json.load(f)
    
    # Take first 2 questions
    questions = data['data'][:2]
    
    # Initialize parser with device mode
    parser = DeepSeekVLParser(device_mode='cpu')  # Force CPU to avoid data type issues
    
    print("Testing DeepSeek-VL parser on 2 questions...")
    print("=" * 50)
    
    for i, qa in enumerate(questions):
        question = qa['question']
        image_name = qa['image']
        image_path = f"data/docvqa/spdocvqa_images/{image_name}"
        
        print(f"\nQuestion {i+1}: {question}")
        print(f"Image: {image_name}")
        
        try:
            # Use ask_question method
            answer = parser.ask_question(image_path, question)
            print(f"Answer: {answer}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_deepseek_vl() 