#!/usr/bin/env python3
"""
Run DocVQA Task 1 benchmark on first 100 questions and display results in table format.
"""

import json
import os
import pandas as pd
from pathlib import Path
import sys

# Import the unified DocVQABenchmarker
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'src'))
from doccraft.benchmarking.docvqa_benchmarker import DocVQABenchmarker

def main():
    gt_path = "tests/data/docvqa/spdocvqa_qas/val_v1.0_withQT.json"
    images_dir = "tests/data/docvqa/spdocvqa_images"
    num_questions = 100
    parser_name = "layoutlmv3"

    benchmarker = DocVQABenchmarker()
    results = benchmarker.benchmark(gt_path, images_dir, parser_name, max_questions=num_questions)

    # Convert results to DataFrame
    df = pd.DataFrame([
        {
            'Question ID': ans['question_id'],
            'Question': ans['question'],
            'Ground Truth': '',  # Optionally load GT if needed
            'Prediction': ans['predicted_answer'],
            'Confidence': ans['confidence'],
            'Image': ans['image']
        }
        for ans in results['answers']
    ])

    print(f"\n{'='*80}")
    print(f"DOCVQA TASK 1 BENCHMARK RESULTS - FIRST {num_questions} QUESTIONS")
    print(f"{'='*80}")

    # Display summary statistics
    print(f"\nSUMMARY:")
    print(f"Total Questions: {len(df)}")
    print(f"Average Confidence: {df['Confidence'].mean():.3f}")

    # Count exact matches (if GT available)
    exact_matches = 0
    for _, row in df.iterrows():
        gt = row['Ground Truth'].lower().strip()
        pred = row['Prediction'].lower().strip()
        if gt and gt == pred:
            exact_matches += 1
    if 'Ground Truth' in df.columns and df['Ground Truth'].any():
        print(f"Exact Matches: {exact_matches} ({exact_matches/len(df)*100:.1f}%)")

    # Display the table
    print(f"\nDETAILED RESULTS:")
    print(f"{'='*80}")

    # Format the table for better readability
    pd.set_option('display.max_colwidth', 50)
    pd.set_option('display.width', None)

    display_df = df[['Question ID', 'Question', 'Ground Truth', 'Prediction', 'Confidence']].copy()
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