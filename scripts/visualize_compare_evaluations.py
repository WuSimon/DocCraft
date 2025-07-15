import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def load_eval(path):
    with open(path, 'r') as f:
        return json.load(f)

def extract_metrics(eval_data):
    return {
        'average_similarity': eval_data.get('average_similarity', eval_data.get('Average Similarity', 0)),
        'exact_matches': eval_data.get('exact_matches', eval_data.get('Exact Matches', 0)),
        'normalized_matches': eval_data.get('normalized_matches', eval_data.get('Normalized Matches', 0)),
        'high_similarity': eval_data.get('high_similarity', eval_data.get('High Similarity (≥0.8)', 0)),
        'medium_similarity': eval_data.get('medium_similarity', eval_data.get('Medium Similarity (≥0.5)', 0)),
        'low_similarity': eval_data.get('low_similarity', eval_data.get('Low Similarity (≥0.2)', 0)),
        'no_match': eval_data.get('no_match', eval_data.get('No Match (<0.2)', 0)),
        'total': eval_data.get('total_questions', eval_data.get('Total Questions', 0)),
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python visualize_compare_evaluations.py <deepseek_eval.json> <layoutlmv3_eval.json>")
        sys.exit(1)

    deepseek_path = sys.argv[1]
    layoutlmv3_path = sys.argv[2]

    deepseek_eval = load_eval(deepseek_path)
    layoutlmv3_eval = load_eval(layoutlmv3_path)

    # Try to extract metrics from both
    ds = extract_metrics(deepseek_eval)
    lm = extract_metrics(layoutlmv3_eval)

    labels = ['Average Similarity', 'Exact Match %', 'High Sim. %', 'Medium Sim. %', 'Low Sim. %', 'No Match %']
    ds_vals = [
        ds['average_similarity'],
        ds['exact_matches'] / ds['total'] * 100,
        ds['high_similarity'] / ds['total'] * 100,
        ds['medium_similarity'] / ds['total'] * 100,
        ds['low_similarity'] / ds['total'] * 100,
        ds['no_match'] / ds['total'] * 100,
    ]
    lm_vals = [
        lm['average_similarity'],
        lm['exact_matches'] / lm['total'] * 100,
        lm['high_similarity'] / lm['total'] * 100,
        lm['medium_similarity'] / lm['total'] * 100,
        lm['low_similarity'] / lm['total'] * 100,
        lm['no_match'] / lm['total'] * 100,
    ]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, ds_vals, width, label='DeepSeek-VL')
    rects2 = ax.bar(x + width/2, lm_vals, width, label='LayoutLMv3')

    ax.set_ylabel('Score / Percentage')
    ax.set_title('DocVQA Task 1: DeepSeek-VL vs LayoutLMv3')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    plt.tight_layout()
    plt.savefig('results/evaluations/deepseek_vs_layoutlmv3_comparison.png')
    plt.show()

    # Pie charts for match breakdown
    for name, metrics in [('DeepSeek-VL', ds), ('LayoutLMv3', lm)]:
        sizes = [metrics['high_similarity'], metrics['medium_similarity'], metrics['low_similarity'], metrics['no_match']]
        labels = ['High (≥0.8)', 'Medium (≥0.5)', 'Low (≥0.2)', 'No Match (<0.2)']
        plt.figure(figsize=(6,6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(f'{name} Similarity Breakdown')
        plt.savefig(f'results/evaluations/{name.lower().replace("-", "")}_similarity_pie.png')
        plt.show()

if __name__ == "__main__":
    main() 