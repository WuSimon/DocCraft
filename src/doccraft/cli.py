import sys
import os
from pathlib import Path
import argparse

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
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    # Default pipeline command (legacy)
    parser_pipeline = subparsers.add_parser('pipeline', help='Run a custom pipeline (default)')
    parser_pipeline.add_argument('--input', type=str, help='Input document path')
    parser_pipeline.add_argument('--parser', type=str, help='Parser name (e.g., tesseract, paddleocr, pdf, pdfplumber, layoutlmv3, etc.)')
    parser_pipeline.add_argument('--preprocessor', type=str, default=None, help='Preprocessor name (optional)')
    parser_pipeline.add_argument('--postprocessor', type=str, default=None, help='Postprocessor name (optional)')
    parser_pipeline.add_argument('--benchmarker', type=str, default=None, help='Benchmarker name (optional)')
    parser_pipeline.add_argument('--benchmark_gt', type=str, default=None, help='Ground truth for benchmarking (if needed)')
    parser_pipeline.add_argument('--benchmark_images', type=str, default=None, help='Images dir for DocVQA benchmarker (if needed)')
    parser_pipeline.add_argument('--config', type=str, default=None, help='JSON config file (overrides CLI args)')
    parser_pipeline.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Benchmark command
    parser_benchmark = subparsers.add_parser('benchmark', help='Run DocVQA benchmarks')
    parser_benchmark.add_argument('--ground_truth', '-g', required=True, help='Path to DocVQA ground truth JSON file')
    parser_benchmark.add_argument('--documents', '-d', required=True, help='Directory containing document images')
    parser_benchmark.add_argument('--parser', '-p', default='layoutlmv3', help='Parser to use')
    parser_benchmark.add_argument('--all_parsers', '-a', action='store_true', help='Benchmark all available parsers')
    parser_benchmark.add_argument('--max_questions', type=int, help='Maximum number of questions to process')
    parser_benchmark.add_argument('--output_dir', '-o', default='results', help='Output directory for results')
    parser_benchmark.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser_benchmark.add_argument('--save_predictions', action='store_true', help='Save individual predictions to separate files')
    parser_benchmark.add_argument('--compare', action='store_true', help='Generate comparison report when using --all_parsers')

    args = parser.parse_args()

    if args.command == 'benchmark':
        # Import and call the unified benchmarker
        from doccraft.benchmarking.docvqa_benchmarker import DocVQABenchmarker
        import json
        import time
        
        # Validate inputs
        if not os.path.exists(args.ground_truth):
            print(f"Error: Ground truth file not found: {args.ground_truth}")
            return 1
        if not os.path.exists(args.documents):
            print(f"Error: Documents directory not found: {args.documents}")
            return 1
        
        # Load ground truth for evaluation
        try:
            with open(args.ground_truth, 'r') as f:
                ground_truth = json.load(f)
            print(f"Loaded ground truth with {len(ground_truth.get('data', []))} questions")
        except Exception as e:
            print(f"Error loading ground truth: {e}")
            return 1
        
        benchmarker = DocVQABenchmarker()
        
        print(f"\n{'='*80}")
        print(f"DOCVQA TASK 1 BENCHMARK")
        print(f"{'='*80}")
        print(f"Ground truth: {args.ground_truth}")
        print(f"Documents: {args.documents}")
        print(f"Max questions: {args.max_questions or 'All'}")
        print(f"Output directory: {args.output_dir}")
        
        if args.all_parsers:
            print(f"Benchmarking all available parsers...")
            parsers = ['layoutlmv3', 'deepseekvl', 'qwenvl', 'tesseract', 'paddleocr', 'pdfplumber']
            all_results = {}
            
            for parser_name in parsers:
                try:
                    print(f"\n--- Benchmarking {parser_name.upper()} ---")
                    start_time = time.time()
                    
                    results = benchmarker.benchmark(
                        args.ground_truth, args.documents, parser_name, args.max_questions
                    )
                    
                    # Calculate metrics
                    if 'answers' in results:
                        metrics = DocVQABenchmarker.calculate_metrics(results['answers'], ground_truth)
                        results['metrics'] = metrics
                        
                        # Calculate average confidence and processing time
                        if results['answers']:
                            confidences = [ans.get('confidence', 0) for ans in results['answers']]
                            processing_times = [ans.get('processing_time', 0) for ans in results['answers']]
                            results['average_confidence'] = sum(confidences) / len(confidences)
                            results['average_processing_time'] = sum(processing_times) / len(processing_times)
                    
                    all_results[parser_name] = results
                    
                    # Generate individual report
                    DocVQABenchmarker.generate_report(results, args.output_dir, parser_name)
                    
                    elapsed_time = time.time() - start_time
                    print(f"Completed in {elapsed_time:.2f} seconds")
                    
                    if args.verbose and 'metrics' in results:
                        metrics = results['metrics']
                        print(f"  Exact Match Rate: {metrics['exact_match_rate']:.3f}")
                        print(f"  Normalized Match Rate: {metrics['normalized_match_rate']:.3f}")
                        print(f"  Average Similarity: {metrics['average_similarity']:.3f}")
                    
                except Exception as e:
                    print(f"Error benchmarking {parser_name}: {e}")
                    continue
            
            if args.compare:
                DocVQABenchmarker.compare_parsers(all_results, args.output_dir)
        
        else:
            print(f"\n--- Benchmarking {args.parser.upper()} ---")
            start_time = time.time()
            
            try:
                results = benchmarker.benchmark(
                    args.ground_truth, args.documents, args.parser, args.max_questions
                )
                
                # Calculate metrics
                if 'predictions' in results:
                    metrics = DocVQABenchmarker.calculate_metrics(results['predictions'], ground_truth)
                    results['metrics'] = metrics
                    
                    # Calculate averages
                    if results['predictions']:
                        confidences = [pred.get('confidence', 0) for pred in results['predictions']]
                        processing_times = [pred.get('processing_time', 0) for pred in results['predictions']]
                        results['average_confidence'] = sum(confidences) / len(confidences)
                        results['average_processing_time'] = sum(processing_times) / len(processing_times)
                
                # Generate report
                DocVQABenchmarker.generate_report(results, args.output_dir, args.parser)
                
                elapsed_time = time.time() - start_time
                print(f"\nBenchmark completed in {elapsed_time:.2f} seconds")
                
                if 'metrics' in results:
                    metrics = results['metrics']
                    print(f"\nResults Summary:")
                    print(f"  Total Questions: {metrics['total_questions']}")
                    print(f"  Exact Match Rate: {metrics['exact_match_rate']:.3f}")
                    print(f"  Normalized Match Rate: {metrics['normalized_match_rate']:.3f}")
                    print(f"  Average Similarity: {metrics['average_similarity']:.3f}")
                    print(f"  High Similarity Rate: {metrics['high_similarity_rate']:.3f}")
                    print(f"  Average Confidence: {results.get('average_confidence', 0):.3f}")
                    print(f"  Average Processing Time: {results.get('average_processing_time', 0):.3f}s")
            
            except Exception as e:
                print(f"Error during benchmarking: {e}")
                return 1
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK COMPLETED")
        print(f"{'='*80}")
        return 0

    elif args.command == 'pipeline' or not args.command:
        # Legacy pipeline functionality
        if not args.input:
            print("Error: --input is required for pipeline command")
            return 1
        
        if not args.parser:
            print("Error: --parser is required for pipeline command")
            return 1
        
        # Import and run pipeline
        try:
            from doccraft.parsers import get_parser
            parser_instance = get_parser(args.parser)
            result = parser_instance.extract_text(args.input)
            
            if args.verbose:
                print(f"Parser: {args.parser}")
                print(f"Input: {args.input}")
                print(f"Result: {result}")
            else:
                print(result.get('text', 'No text extracted'))
            
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 