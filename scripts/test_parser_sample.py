#!/usr/bin/env python3
"""
Test different parsers on a few DocVQA questions
"""

import warnings
import os

# Suppress warnings BEFORE any other imports
warnings.filterwarnings("ignore")
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import json
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_parser(parser_name, num_questions=2):
    """Test a specific parser on DocVQA questions"""
    
    # Load test data
    with open('tests/data/docvqa/spdocvqa_qas/val_v1.0_withQT.json', 'r') as f:
        data = json.load(f)
    
    # Take specified number of questions
    questions = data['data'][:num_questions]
    
    # Initialize parser based on name
    if parser_name.lower() == 'layoutlmv3':
        from doccraft.parsers.layoutlmv3_parser import LayoutLMv3Parser
        parser = LayoutLMv3Parser()
    elif parser_name.lower() == 'deepseek':
        from doccraft.parsers.deepseek_vl_parser import DeepSeekVLParser
        parser = DeepSeekVLParser(device_mode='cpu')  # Force CPU to avoid data type issues
    elif parser_name.lower() == 'paddleocr':
        from doccraft.parsers.paddle_ocr_parser import PaddleOCRParser
        parser = PaddleOCRParser()
    elif parser_name.lower() == 'tesseract':
        from doccraft.parsers.ocr_parser import TesseractParser
        parser = TesseractParser()
    elif parser_name.lower() == 'pdfplumber':
        from doccraft.parsers.pdfplumber_parser import PDFPlumberParser
        parser = PDFPlumberParser()
    else:
        print(f"Unknown parser: {parser_name}")
        print("Available parsers: layoutlmv3, deepseek, paddleocr, tesseract, pdfplumber")
        return
    
    print(f"Testing {parser_name} parser on {num_questions} questions...")
    print("=" * 60)
    
    for i, qa in enumerate(questions):
        question = qa['question']
        image_name = qa['image']
        # Remove 'documents/' prefix if present in image name
        clean_image_name = image_name.replace('documents/', '')
        image_path = f"tests/data/docvqa/spdocvqa_images/{clean_image_name}"
        ground_truth = qa['answers'][0] if qa['answers'] else "No answer"
        
        print(f"\nQuestion {i+1}: {question}")
        print(f"Image: {image_name}")
        print(f"Ground Truth: {ground_truth}")
        
        try:
            # Use ask_question method for AI parsers, extract_text for others
            if hasattr(parser, 'ask_question'):
                answer = parser.ask_question(image_path, question)
            else:
                # For non-AI parsers, extract text and show it
                text = parser.extract_text_from_image(image_path)
                answer = f"[Extracted text: {text[:200]}{'...' if len(text) > 200 else ''}]"
            
            print(f"Answer: {answer}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description='Test different parsers on DocVQA questions')
    parser.add_argument('--parser', '-p', type=str, default='layoutlmv3',
                       choices=['layoutlmv3', 'deepseek', 'paddleocr', 'tesseract', 'pdfplumber'],
                       help='Parser to test')
    parser.add_argument('--num-questions', '-n', type=int, default=2,
                       help='Number of questions to test')
    
    args = parser.parse_args()
    
    test_parser(args.parser, args.num_questions)

if __name__ == "__main__":
    main() 