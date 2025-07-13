#!/usr/bin/env python3
"""
Run DocVQA Task 1 benchmark on first 100 questions and display results in table format.
"""

import json
import os
import pandas as pd
from pathlib import Path

# Import the parser
try:
    from doccraft.parsers.layoutlmv3_parser import LayoutLMv3Parser
except ImportError:
    print("Warning: Could not import LayoutLMv3Parser. Please check your environment.")
    LayoutLMv3Parser = None

def main():
    gt_path = "tests/data/docvqa/spdocvqa_qas/val_v1.0_withQT.json"
    images_dir = "tests/data/docvqa/spdocvqa_images"
    num_questions = 100

    with open(gt_path, 'r') as f:
        gt_data = json.load(f)
    
    questions = gt_data['data'][:num_questions]

    if LayoutLMv3Parser is None:
        print("Model not available. Exiting.")
        return

    parser = LayoutLMv3Parser()
    
    results = []
    
    print(f"Processing {num_questions} questions...")
    
    for i, item in enumerate(questions, 1):
        image_path = item['image']
        if image_path.startswith('documents/'):
            image_path = image_path.replace('documents/', '')
        full_image_path = os.path.join(images_dir, image_path)
        
        question = item['question']
        gt_answers = item.get('answers', [])
        question_id = item.get('questionId', i)
        
        if not os.path.exists(full_image_path):
            print(f"Image not found: {full_image_path}")
            continue
        
        # Run the model
        try:
            result = parser.ask_question(full_image_path, question)
            prediction = result.get('answer', 'No answer')
            confidence = result.get('confidence', 0.0)
        except Exception as e:
            prediction = f"Error: {e}"
            confidence = 0.0
        
        # Store results
        results.append({
            'Question ID': question_id,
            'Question': question,
            'Ground Truth': ' | '.join(gt_answers) if gt_answers else 'No answer',
            'Prediction': prediction,
            'Confidence': confidence,
            'Image': image_path
        })
        
        if i % 10 == 0:
            print(f"Processed {i}/{num_questions} questions...")
    
    # Create DataFrame and display
    df = pd.DataFrame(results)
    
    print(f"\n{'='*80}")
    print(f"DOCVQA TASK 1 BENCHMARK RESULTS - FIRST {num_questions} QUESTIONS")
    print(f"{'='*80}")
    
    # Display summary statistics
    print(f"\nSUMMARY:")
    print(f"Total Questions: {len(df)}")
    print(f"Average Confidence: {df['Confidence'].mean():.3f}")
    
    # Count exact matches
    exact_matches = 0
    for _, row in df.iterrows():
        gt = row['Ground Truth'].lower().strip()
        pred = row['Prediction'].lower().strip()
        if gt == pred:
            exact_matches += 1
    
    print(f"Exact Matches: {exact_matches} ({exact_matches/len(df)*100:.1f}%)")
    
    # Display the table
    print(f"\nDETAILED RESULTS:")
    print(f"{'='*80}")
    
    # Format the table for better readability
    pd.set_option('display.max_colwidth', 50)
    pd.set_option('display.width', None)
    
    # Create a more readable table
    display_df = df[['Question ID', 'Question', 'Ground Truth', 'Prediction', 'Confidence']].copy()
    
    # Truncate long text for display
    display_df['Question'] = display_df['Question'].apply(lambda x: x[:47] + '...' if len(x) > 50 else x)
    display_df['Ground Truth'] = display_df['Ground Truth'].apply(lambda x: x[:47] + '...' if len(x) > 50 else x)
    display_df['Prediction'] = display_df['Prediction'].apply(lambda x: x[:47] + '...' if len(x) > 50 else x)
    
    print(display_df.to_string(index=False))
    
    # Save detailed results to file
    output_file = f"results_first_{num_questions}_questions.csv"
    df.to_csv(output_file, index=False)
    print(f"\nDetailed results saved to: {output_file}")

if __name__ == "__main__":
    main() 