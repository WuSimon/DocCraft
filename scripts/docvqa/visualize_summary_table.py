import json
import matplotlib.pyplot as plt
from tabulate import tabulate
import numpy as np

SUMMARY_FILE = 'results/multifile_eval_summary_table.json'
BAR_CHART_FILE = 'results/multifile_eval_summary_bar.png'
AVGSIM_CHART_FILE = 'results/multifile_eval_summary_avgsim.png'

# Load summary data
with open(SUMMARY_FILE, 'r') as f:
    summary = json.load(f)

# Prepare table data
headers = [
    'Model', 'Exact', 'Norm', 'High', 'Med', 'Low', 'NoMatch', 'AvgSim'
]
table = []
model_names = []
for entry in summary:
    # Use the filename (last part) as model name
    model = entry['file'].split('/')[-1].replace('_task1_predictions_full_eval.json','').replace('_task1_predictions.json','').replace('.json','')
    model_names.append(model)
    table.append([
        model,
        f"{entry['exact_match_rate']*100:.2f}%",
        f"{entry['normalized_match_rate']*100:.2f}%",
        f"{entry['high_similarity_rate']*100:.2f}%",
        f"{entry['medium_similarity_rate']*100:.2f}%",
        f"{entry['low_similarity_rate']*100:.2f}%",
        f"{entry['no_match_rate']*100:.2f}%",
        f"{entry['average_similarity']:.3f}",
    ])

print(tabulate(table, headers=headers, tablefmt='github'))

# Bar chart for main rates (excluding Total and AvgSim)
metrics = [
    ('Exact', 'exact_match_rate'),
    ('Norm', 'normalized_match_rate'),
    ('High (≥0.8)', 'high_similarity_rate'),
    ('Med (≥0.5)', 'medium_similarity_rate'),
    ('Low (≥0.2)', 'low_similarity_rate'),
    ('NoMatch (<0.2)', 'no_match_rate'),
]

x = np.arange(len(model_names))
width = 0.13
fig, ax = plt.subplots(figsize=(12,6))
for i, (label, key) in enumerate(metrics):
    values = [entry[key] for entry in summary]
    ax.bar(x + (i - len(metrics)/2)*width, values, width, label=label)

ax.set_ylabel('Rate')
ax.set_title('DocVQA Benchmark: Main Match & Similarity Rates')
ax.set_xticks(x)
ax.set_xticklabels(model_names)
ax.legend()
plt.tight_layout()
plt.savefig(BAR_CHART_FILE)
print(f"Bar chart saved to {BAR_CHART_FILE}")

# Separate bar chart for AvgSim
fig2, ax2 = plt.subplots(figsize=(8,5))
avgsim_values = [entry['average_similarity'] for entry in summary]
ax2.bar(model_names, avgsim_values, color='gray', width=0.5)
ax2.set_ylabel('Average Similarity')
ax2.set_title('DocVQA Benchmark: Average Similarity')
plt.tight_layout()
plt.savefig(AVGSIM_CHART_FILE)
print(f"AvgSim bar chart saved to {AVGSIM_CHART_FILE}") 