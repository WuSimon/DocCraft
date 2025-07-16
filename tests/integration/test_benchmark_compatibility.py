#!/usr/bin/env python3
"""
Test script to verify that all parsers work with the existing benchmarks.

This script tests the compatibility of all parsers with the benchmarking
infrastructure to ensure they can be properly evaluated.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import pytest

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from doccraft.parsers import (
    PDFParser, PDFPlumberParser, TesseractParser, PaddleOCRParser,
    LayoutLMv3Parser, DeepSeekVLParser
)
from doccraft.benchmarking import PerformanceBenchmarker, AccuracyBenchmarker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_parser_initialization():
    """Test that all parsers can be initialized correctly."""
    print("\n" + "="*60)
    print("TESTING PARSER INITIALIZATION")
    print("="*60)
    
    parsers = {}
    
    # Test traditional parsers
    traditional_parsers = [
        ("PDFParser", PDFParser),
        ("PDFPlumberParser", PDFPlumberParser),
        ("TesseractParser", TesseractParser),
        ("PaddleOCRParser", PaddleOCRParser),
    ]
    
    for parser_name, parser_class in traditional_parsers:
        try:
            print(f"\nTesting {parser_name} initialization...")
            parser = parser_class()
            parsers[parser_name] = parser
            print(f"✓ {parser_name} initialized successfully")
            print(f"  - Name: {parser.name}")
            print(f"  - Version: {parser.version}")
            print(f"  - Supported formats: {parser.supported_formats}")
            
        except Exception as e:
            print(f"✗ {parser_name} initialization failed: {e}")
            logger.error(f"{parser_name} initialization error: {e}")
    
    # Test AI parsers
    ai_parsers = [
        ("LayoutLMv3Parser", LayoutLMv3Parser, {"device": "cpu"}),
        ("DeepSeekVLParser", DeepSeekVLParser, {"device": "cpu"}),
    ]
    
    for parser_name, parser_class, kwargs in ai_parsers:
        try:
            print(f"\nTesting {parser_name} initialization...")
            parser = parser_class(**kwargs)
            parsers[parser_name] = parser
            print(f"✓ {parser_name} initialized successfully")
            print(f"  - Name: {parser.name}")
            print(f"  - Version: {parser.version}")
            print(f"  - Supported formats: {parser.supported_formats}")
            
        except Exception as e:
            print(f"✗ {parser_name} initialization failed: {e}")
            logger.error(f"{parser_name} initialization error: {e}")
    
    # Assert that at least some parsers were initialized successfully
    assert len(parsers) > 0, "No parsers were initialized successfully"


def test_benchmarker_initialization():
    """Test that benchmarkers can be initialized correctly."""
    print("\n" + "="*60)
    print("TESTING BENCHMARKER INITIALIZATION")
    print("="*60)
    
    benchmarkers = {}
    
    try:
        # Test PerformanceBenchmarker
        print("\nTesting PerformanceBenchmarker initialization...")
        perf_benchmarker = PerformanceBenchmarker()
        benchmarkers['PerformanceBenchmarker'] = perf_benchmarker
        print(f"✓ PerformanceBenchmarker initialized successfully")
        print(f"  - Name: {perf_benchmarker.name}")
        print(f"  - Version: {perf_benchmarker.version}")
        print(f"  - Supported metrics: {perf_benchmarker.supported_metrics}")
        
    except Exception as e:
        print(f"✗ PerformanceBenchmarker initialization failed: {e}")
        logger.error(f"PerformanceBenchmarker initialization error: {e}")
    
    try:
        # Test AccuracyBenchmarker
        print("\nTesting AccuracyBenchmarker initialization...")
        acc_benchmarker = AccuracyBenchmarker()
        benchmarkers['AccuracyBenchmarker'] = acc_benchmarker
        print(f"✓ AccuracyBenchmarker initialized successfully")
        print(f"  - Name: {acc_benchmarker.name}")
        print(f"  - Version: {acc_benchmarker.version}")
        print(f"  - Supported metrics: {acc_benchmarker.supported_metrics}")
        
    except Exception as e:
        print(f"✗ AccuracyBenchmarker initialization failed: {e}")
        logger.error(f"AccuracyBenchmarker initialization error: {e}")
    
    # Assert that at least some benchmarkers were initialized successfully
    assert len(benchmarkers) > 0, "No benchmarkers were initialized successfully"


def test_parser_benchmark_compatibility(parsers: Dict[str, Any], benchmarkers: Dict[str, Any]):
    """Test that parsers work with the benchmarking infrastructure."""
    print("\n" + "="*60)
    print("TESTING PARSER-BENCHMARK COMPATIBILITY")
    print("="*60)
    
    # Create test files for different parser types
    test_files = {}
    
    # Create a simple text file for testing
    text_file = project_root / "temp_test.txt"
    text_file.write_text("This is a test document for benchmarking compatibility.")
    test_files['text'] = text_file
    
    # Create a simple image file for OCR parsers
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a simple image with text
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((50, 50), "Test Document", fill='black', font=font)
        draw.text((50, 100), "For OCR Testing", fill='black', font=font)
        
        image_file = project_root / "temp_test.png"
        img.save(image_file)
        test_files['image'] = image_file
        
    except Exception as e:
        print(f"Could not create test image: {e}")
    
    # Create a simple PDF file for PDF parsers
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_file = project_root / "temp_test.pdf"
        c = canvas.Canvas(str(pdf_file), pagesize=letter)
        c.drawString(100, 750, "Test PDF Document")
        c.drawString(100, 700, "For PDF Parser Testing")
        c.drawString(100, 650, "This is a simple test document.")
        c.save()
        test_files['pdf'] = pdf_file
        
    except Exception as e:
        print(f"Could not create test PDF: {e}")
    
    print(f"Created {len(test_files)} test files: {list(test_files.keys())}")
    
    # Test each parser with each benchmarker
    for parser_name, parser in parsers.items():
        print(f"\n--- Testing {parser_name} with Benchmarks ---")
        
        # Find appropriate test file for this parser
        test_file = None
        for file_type, file_path in test_files.items():
            if parser.can_parse(str(file_path)):
                test_file = file_path
                break
        
        if not test_file:
            print(f"✗ No suitable test file found for {parser_name}")
            continue
        
        print(f"Testing basic extraction with {test_file.name}")
        
        try:
            start_time = time.time()
            result = parser.extract_text(str(test_file))
            extraction_time = time.time() - start_time
            
            extracted_text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            print(f"✓ Basic extraction successful")
            print(f"  - Extraction time: {extraction_time:.2f}s")
            print(f"  - Text length: {len(extracted_text)} characters")
            print(f"  - Metadata keys: {list(metadata.keys())}")
            
        except Exception as e:
            print(f"✗ Basic extraction failed: {e}")
            continue
        
        # Test with PerformanceBenchmarker
        if 'PerformanceBenchmarker' in benchmarkers:
            print(f"\nTesting with PerformanceBenchmarker...")
            try:
                perf_benchmarker = benchmarkers['PerformanceBenchmarker']
                results = perf_benchmarker.benchmark(
                    parser, 
                    str(test_file),
                    iterations=1,  # Quick test
                    warmup_runs=0,
                    measure_memory=True,
                    measure_cpu=True
                )
                
                print(f"✓ Performance benchmark successful")
                print(f"  - Execution time: {results.get('metrics', {}).get('execution_time', {}).get('mean', 'N/A')}s")
                print(f"  - Memory usage: {results.get('metrics', {}).get('memory_usage', {}).get('mean', 'N/A')}MB")
                
            except Exception as e:
                print(f"✗ Performance benchmark failed: {e}")
                logger.error(f"Performance benchmark error with {parser_name}: {e}")
        
        # Test with AccuracyBenchmarker
        if 'AccuracyBenchmarker' in benchmarkers:
            print(f"\nTesting with AccuracyBenchmarker...")
            try:
                acc_benchmarker = benchmarkers['AccuracyBenchmarker']
                
                # Create simple ground truth for testing
                ground_truth = "This is a test document for benchmarking compatibility."
                
                results = acc_benchmarker.benchmark(
                    parser,
                    str(test_file),
                    ground_truth,
                    normalize_text=True,
                    ignore_case=True,
                    ignore_whitespace=True
                )
                
                print(f"✓ Accuracy benchmark successful")
                print(f"  - Character accuracy: {results.get('metrics', {}).get('character_accuracy', 'N/A')}")
                print(f"  - Word accuracy: {results.get('metrics', {}).get('word_accuracy', 'N/A')}")
                print(f"  - Similarity ratio: {results.get('metrics', {}).get('similarity_ratio', 'N/A')}")
                
            except Exception as e:
                print(f"✗ Accuracy benchmark failed: {e}")
                logger.error(f"Accuracy benchmark error with {parser_name}: {e}")
    
    # Clean up temporary test files
    for file_path in test_files.values():
        if file_path.exists():
            file_path.unlink()


def test_benchmark_comparison(parsers: Dict[str, Any], benchmarkers: Dict[str, Any]):
    """Test benchmark comparison functionality."""
    print("\n" + "="*60)
    print("TESTING BENCHMARK COMPARISON")
    print("="*60)
    
    # Create test files for different parser types
    test_files = {}
    
    # Create a simple text file for testing
    text_file = project_root / "comparison_test.txt"
    text_file.write_text("This is a test document for comparing parser performance.")
    test_files['text'] = text_file
    
    # Create a simple image file for OCR parsers
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple image with text
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((50, 50), "Test Document", fill='black', font=font)
        draw.text((50, 100), "For Comparison Testing", fill='black', font=font)
        
        image_file = project_root / "comparison_test.png"
        img.save(image_file)
        test_files['image'] = image_file
        
    except Exception as e:
        print(f"Could not create test image: {e}")
    
    # Create a simple PDF file for PDF parsers
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_file = project_root / "comparison_test.pdf"
        c = canvas.Canvas(str(pdf_file), pagesize=letter)
        c.drawString(100, 750, "Test PDF Document")
        c.drawString(100, 700, "For Comparison Testing")
        c.drawString(100, 650, "This is a simple test document.")
        c.save()
        test_files['pdf'] = pdf_file
        
    except Exception as e:
        print(f"Could not create test PDF: {e}")
    
    # Test performance comparison
    if 'PerformanceBenchmarker' in benchmarkers and len(parsers) > 1:
        print("\nTesting performance comparison...")
        try:
            perf_benchmarker = benchmarkers['PerformanceBenchmarker']
            
            # Group parsers by supported file types
            pdf_parsers = []
            image_parsers = []
            text_parsers = []
            
            for parser in parsers.values():
                if any(parser.can_parse(str(f)) for f in test_files.values() if f.suffix == '.pdf'):
                    pdf_parsers.append(parser)
                elif any(parser.can_parse(str(f)) for f in test_files.values() if f.suffix in ['.png', '.jpg', '.jpeg']):
                    image_parsers.append(parser)
                elif any(parser.can_parse(str(f)) for f in test_files.values() if f.suffix == '.txt'):
                    text_parsers.append(parser)
            
            # Test with PDF parsers if available
            if pdf_parsers and 'pdf' in test_files:
                parser_list = pdf_parsers[:2]  # Use first 2 PDF parsers
                test_file = test_files['pdf']
                
                comparison_results = perf_benchmarker.compare_parsers(
                    parser_list,
                    str(test_file),
                    iterations=1,
                    warmup_runs=0
                )
                
                print(f"✓ Performance comparison successful (PDF parsers)")
                print(f"  - Compared {len(parser_list)} parsers")
                print(f"  - Results stored: {len(comparison_results.get('results', []))} parser results")
                
            # Test with image parsers if available
            elif image_parsers and 'image' in test_files:
                parser_list = image_parsers[:2]  # Use first 2 image parsers
                test_file = test_files['image']
                
                comparison_results = perf_benchmarker.compare_parsers(
                    parser_list,
                    str(test_file),
                    iterations=1,
                    warmup_runs=0
                )
                
                print(f"✓ Performance comparison successful (Image parsers)")
                print(f"  - Compared {len(parser_list)} parsers")
                print(f"  - Results stored: {len(comparison_results.get('results', []))} parser results")
                
            else:
                print("✗ No suitable parsers found for performance comparison")
                
        except Exception as e:
            print(f"✗ Performance comparison failed: {e}")
            logger.error(f"Performance comparison error: {e}")
    
    # Test accuracy comparison
    if 'AccuracyBenchmarker' in benchmarkers and len(parsers) > 1:
        print("\nTesting accuracy comparison...")
        try:
            acc_benchmarker = benchmarkers['AccuracyBenchmarker']
            
            # Group parsers by supported file types
            pdf_parsers = []
            image_parsers = []
            text_parsers = []
            
            for parser in parsers.values():
                if any(parser.can_parse(str(f)) for f in test_files.values() if f.suffix == '.pdf'):
                    pdf_parsers.append(parser)
                elif any(parser.can_parse(str(f)) for f in test_files.values() if f.suffix in ['.png', '.jpg', '.jpeg']):
                    image_parsers.append(parser)
                elif any(parser.can_parse(str(f)) for f in test_files.values() if f.suffix == '.txt'):
                    text_parsers.append(parser)
            
            # Test with PDF parsers if available
            if pdf_parsers and 'pdf' in test_files:
                parser_list = pdf_parsers[:2]  # Use first 2 PDF parsers
                test_file = test_files['pdf']
                ground_truth = "Test PDF Document For PDF Parser Testing This is a simple test document."
                
                comparison_results = acc_benchmarker.compare_parsers(
                    parser_list,
                    str(test_file),
                    ground_truth,
                    normalize_text=True,
                    ignore_case=True
                )
                
                print(f"✓ Accuracy comparison successful (PDF parsers)")
                print(f"  - Compared {len(parser_list)} parsers")
                print(f"  - Results stored: {len(comparison_results.get('results', []))} parser results")
                
            # Test with image parsers if available
            elif image_parsers and 'image' in test_files:
                parser_list = image_parsers[:2]  # Use first 2 image parsers
                test_file = test_files['image']
                ground_truth = "Test Document For Comparison Testing"
                
                comparison_results = acc_benchmarker.compare_parsers(
                    parser_list,
                    str(test_file),
                    ground_truth,
                    normalize_text=True,
                    ignore_case=True
                )
                
                print(f"✓ Accuracy comparison successful (Image parsers)")
                print(f"  - Compared {len(parser_list)} parsers")
                print(f"  - Results stored: {len(comparison_results.get('results', []))} parser results")
                
            else:
                print("✗ No suitable parsers found for accuracy comparison")
                
        except Exception as e:
            print(f"✗ Accuracy comparison failed: {e}")
            logger.error(f"Accuracy comparison error: {e}")
    
    # Clean up
    for file_path in test_files.values():
        if file_path.exists():
            file_path.unlink()


def test_benchmark_reporting(benchmarkers: Dict[str, Any]):
    """Test benchmark reporting functionality."""
    print("\n" + "="*60)
    print("TESTING BENCHMARK REPORTING")
    print("="*60)
    
    for benchmarker_name, benchmarker in benchmarkers.items():
        print(f"\nTesting {benchmarker_name} reporting...")
        
        try:
            # Test report generation
            report_path = project_root / f"test_{benchmarker_name.lower()}_report.txt"
            
            if hasattr(benchmarker, 'generate_report'):
                benchmarker.generate_report(str(report_path))
                print(f"✓ Report generated: {report_path}")
                
                # Check if report file exists and has content
                if report_path.exists():
                    content = report_path.read_text()
                    print(f"  - Report size: {len(content)} characters")
                else:
                    print(f"  - Warning: Report file not created")
                    
                # Clean up
                if report_path.exists():
                    report_path.unlink()
                    
        except Exception as e:
            print(f"✗ Report generation failed: {e}")
            logger.error(f"Report generation error with {benchmarker_name}: {e}")


@pytest.fixture
def parsers():
    """Fixture to provide initialized parsers for tests."""
    parsers = {}
    
    # Test traditional parsers
    traditional_parsers = [
        ("PDFParser", PDFParser),
        ("PDFPlumberParser", PDFPlumberParser),
        ("TesseractParser", TesseractParser),
        ("PaddleOCRParser", PaddleOCRParser),
    ]
    
    for parser_name, parser_class in traditional_parsers:
        try:
            parser = parser_class()
            parsers[parser_name] = parser
        except Exception as e:
            logger.error(f"{parser_name} initialization error: {e}")
    
    # Test AI parsers
    ai_parsers = [
        ("LayoutLMv3Parser", LayoutLMv3Parser, {"device": "cpu"}),
        ("DeepSeekVLParser", DeepSeekVLParser, {"device": "cpu"}),
    ]
    
    for parser_name, parser_class, kwargs in ai_parsers:
        try:
            parser = parser_class(**kwargs)
            parsers[parser_name] = parser
        except Exception as e:
            logger.error(f"{parser_name} initialization error: {e}")
    
    return parsers

@pytest.fixture
def benchmarkers():
    """Fixture to provide initialized benchmarkers for tests."""
    benchmarkers = {}
    
    try:
        perf_benchmarker = PerformanceBenchmarker()
        benchmarkers['PerformanceBenchmarker'] = perf_benchmarker
    except Exception as e:
        logger.error(f"PerformanceBenchmarker initialization error: {e}")
    
    try:
        acc_benchmarker = AccuracyBenchmarker()
        benchmarkers['AccuracyBenchmarker'] = acc_benchmarker
    except Exception as e:
        logger.error(f"AccuracyBenchmarker initialization error: {e}")
    
    return benchmarkers


def main():
    """Main test function."""
    print("BENCHMARK COMPATIBILITY TEST SUITE")
    print("="*60)
    print("This script tests that all parsers work correctly with")
    print("the existing benchmarking infrastructure.")
    print("="*60)
    
    # Test parser initialization
    parsers = test_parser_initialization()
    
    if not parsers:
        print("\n✗ No parsers could be initialized. Exiting.")
        return
    
    # Test benchmarker initialization
    benchmarkers = test_benchmarker_initialization()
    
    if not benchmarkers:
        print("\n✗ No benchmarkers could be initialized. Exiting.")
        return
    
    # Test parser-benchmark compatibility
    test_parser_benchmark_compatibility(parsers, benchmarkers)
    
    # Test benchmark comparison
    test_benchmark_comparison(parsers, benchmarkers)
    
    # Test benchmark reporting
    test_benchmark_reporting(benchmarkers)
    
    print("\n" + "="*60)
    print("BENCHMARK COMPATIBILITY TEST COMPLETED")
    print("="*60)
    print("Check the output above for any compatibility issues.")
    print("If all tests pass, all parsers work with the benchmarks!")


if __name__ == "__main__":
    main() 