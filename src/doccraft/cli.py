import argparse
import json
import sys
from pathlib import Path

# Import DocCraft registries and classes
from doccraft.parsers import PARSER_REGISTRY
from doccraft.preprocessing import ImagePreprocessor, PDFPreprocessor
from doccraft.postprocessing import TextPostprocessor, TablePostprocessor
from doccraft.benchmarking import AccuracyBenchmarker, PerformanceBenchmarker, DocVQABenchmarker

# Registries for dynamic lookup
PREPROCESSOR_REGISTRY = {
    'image': ImagePreprocessor,
    'pdf': PDFPreprocessor,
}
POSTPROCESSOR_REGISTRY = {
    'text': TextPostprocessor,
    'table': TablePostprocessor,
}
BENCHMARKER_REGISTRY = {
    'accuracy': AccuracyBenchmarker,
    'performance': PerformanceBenchmarker,
    'docvqa': DocVQABenchmarker,
}

def run_pipeline(cfg):
    # Load preprocessor
    preprocessor = None
    if cfg.get('preprocessor'):
        preproc_cls = PREPROCESSOR_REGISTRY.get(cfg['preprocessor'])
        if not preproc_cls:
            print(f"Unknown preprocessor: {cfg['preprocessor']}")
            sys.exit(1)
        preprocessor = preproc_cls()

    # Load parser
    parser_cls = PARSER_REGISTRY.get(cfg['parser'])
    if not parser_cls:
        print(f"Unknown parser: {cfg['parser']}")
        sys.exit(1)
    parser = parser_cls()

    # Load postprocessor
    postprocessor = None
    if cfg.get('postprocessor'):
        postproc_cls = POSTPROCESSOR_REGISTRY.get(cfg['postprocessor'])
        if not postproc_cls:
            print(f"Unknown postprocessor: {cfg['postprocessor']}")
            sys.exit(1)
        postprocessor = postproc_cls()

    # Load benchmarker
    benchmarker = None
    if cfg.get('benchmarker'):
        bench_cls = BENCHMARKER_REGISTRY.get(cfg['benchmarker'])
        if not bench_cls:
            print(f"Unknown benchmarker: {cfg['benchmarker']}")
            sys.exit(1)
        if cfg['benchmarker'] == 'docvqa':
            # DocVQABenchmarker needs dataset and images
            benchmarker = bench_cls(cfg.get('benchmark_gt'), cfg.get('benchmark_images'))
        else:
            benchmarker = bench_cls()

    # Load input
    input_path = cfg['input']
    data = input_path
    if preprocessor:
        print(f"[Pipeline] Preprocessing with {preprocessor.__class__.__name__}")
        data = preprocessor.process(data)
        if isinstance(data, tuple):
            data, _ = data
    print(f"[Pipeline] Parsing with {parser.__class__.__name__}")
    parsed = parser.extract_text(data)
    result_text = parsed['text']
    if postprocessor:
        print(f"[Pipeline] Postprocessing with {postprocessor.__class__.__name__}")
        post_result = postprocessor.process(result_text)
        if isinstance(post_result, tuple):
            result_text, _ = post_result
        else:
            result_text = post_result
    print("[Pipeline] Extraction result:")
    print(result_text[:500] + ("..." if len(result_text) > 500 else ""))
    if benchmarker:
        print(f"[Pipeline] Benchmarking with {benchmarker.__class__.__name__}")
        # For accuracy, expects parser and file_path
        if cfg['benchmarker'] == 'accuracy':
            metrics = benchmarker.benchmark(parser, input_path)
        elif cfg['benchmarker'] == 'performance':
            metrics = benchmarker.benchmark(parser, input_path)
        elif cfg['benchmarker'] == 'docvqa':
            metrics = benchmarker.benchmark(parser, input_path)
        else:
            metrics = None
        print("[Pipeline] Benchmark results:")
        print(json.dumps(metrics, indent=2))

def main():
    parser = argparse.ArgumentParser(description="DocCraft Modular Pipeline CLI")
    parser.add_argument('--input', type=str, help='Input document path')
    parser.add_argument('--parser', type=str, help='Parser name (see doccraft.parsers)')
    parser.add_argument('--preprocessor', type=str, default=None, help='Preprocessor name (optional)')
    parser.add_argument('--postprocessor', type=str, default=None, help='Postprocessor name (optional)')
    parser.add_argument('--benchmarker', type=str, default=None, help='Benchmarker name (optional)')
    parser.add_argument('--benchmark_gt', type=str, default=None, help='Ground truth for benchmarking (if needed)')
    parser.add_argument('--benchmark_images', type=str, default=None, help='Images dir for DocVQA benchmarker (if needed)')
    parser.add_argument('--config', type=str, default=None, help='JSON config file (overrides CLI args)')
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            cfg = json.load(f)
    else:
        cfg = vars(args)
    # Remove None values
    cfg = {k: v for k, v in cfg.items() if v is not None}
    run_pipeline(cfg)

if __name__ == '__main__':
    main() 