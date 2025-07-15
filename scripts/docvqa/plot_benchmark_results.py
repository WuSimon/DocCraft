import json
import matplotlib.pyplot as plt
import numpy as np

models = ['Qwen-VL', 'DeepSeek-VL', 'LayoutLMv3']
files = [
    'results/evaluations/qwenvl_task1_eval_full.json',
    'results/evaluations/deepseekvl_task1_eval_full.json',
    'results/evaluations/layoutlmv3_task1_eval_full.json',
]

results = [json.load(open(f)) for f in files]

# Bar chart for match rates
match_rates = np.array([
    [
        r['exact_matches']/r['total_questions'],
        r['normalized_matches']/r['total_questions'],
        r['matches_total']/r['total_questions']
    ] for r in results
])
labels = ['Exact', 'Normalized', 'Total']
x = np.arange(len(models))
width = 0.25
fig, ax = plt.subplots(figsize=(10,6))
for i in range(3):
    ax.bar(x + (i-1)*width, match_rates[:,i], width, label=labels[i])
ax.set_ylabel('Proportion of Questions')
ax.set_title('DocVQA Benchmark results')
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend()
plt.tight_layout()
plt.savefig('results/evaluations/docvqa_benchmark_results_bar.png')

# Line chart for average similarity
plt.figure(figsize=(8,5))
plt.plot(models, [r['average_similarity'] for r in results], marker='o')
plt.title('DocVQA Benchmark results: Average Similarity')
plt.ylabel('Average Similarity')
plt.ylim(0,1)
plt.grid(True)
plt.tight_layout()
plt.savefig('results/evaluations/docvqa_benchmark_results_similarity.png')

# Pie charts for similarity breakdown
sim_labels = ['High (≥0.8)', 'Medium (≥0.5)', 'Low (≥0.2)', 'No Match (<0.2)']
sim_keys = ['high_similarity', 'medium_similarity', 'low_similarity', 'no_match']
colors = ['#4daf4a', '#377eb8', '#ff7f00', '#e41a1c']
for model, r in zip(models, results):
    sizes = [r[k] for k in sim_keys]
    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=sim_labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title(f'{model} Similarity Breakdown')
    plt.tight_layout()
    plt.savefig(f'results/evaluations/docvqa_benchmark_results_pie_{model.lower().replace("-","")}.png')

print('Saved bar, line, and pie charts to results/evaluations/') 