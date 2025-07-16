#!/usr/bin/env python3
"""
DocCraft - All Options Demonstration

This script demonstrates how to use all the different options available
in the DocCraft package for each subcategory:
- Parsers: PyMuPDF, pdfplumber, Tesseract OCR, PaddleOCR
- Preprocessing: Image preprocessing, PDF preprocessing
- Postprocessing: Text postprocessing, Table postprocessing
- Benchmarking: Performance benchmarking, Accuracy benchmarking
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import doccraft
sys.path.insert(0, str(Path(__file__).parent))

from doccraft import (
    # Parsers
    PDFParser, PDFPlumberParser, TesseractParser, PaddleOCRParser,
    # Preprocessors
    ImagePreprocessor, PDFPreprocessor,
    # Postprocessors
    TextPostprocessor, TablePostprocessor,
    # Benchmarkers
    PerformanceBenchmarker, AccuracyBenchmarker
)


def demo_parsers():
    """Demonstrate different parser options."""
    print("=" * 60)
    print("PARSERS DEMONSTRATION")
    print("=" * 60)
    
    # Check if test files exist
    pdf_file = Path("tests/test_assets/dummy.pdf")
    image_file = Path("tests/test_assets/lenna.png")
    
    if not pdf_file.exists():
        print(f"PDF test file not found: {pdf_file}")
        return
    
    if not image_file.exists():
        print(f"Image test file not found: {image_file}")
        return
    
    # 1. PyMuPDF PDF Parser
    print("\n1. PyMuPDF PDF Parser")
    print("-" * 30)
    try:
        pdf_parser = PDFParser()
        text, metadata = pdf_parser.extract_text(pdf_file)
        print(f"✓ PyMuPDF extracted {len(text)} characters")
        print(f"  Pages: {metadata.get('total_pages', 'N/A')}")
        print(f"  Method: {metadata.get('extraction_method', 'N/A')}")
    except Exception as e:
        print(f"✗ PyMuPDF failed: {e}")
    
    # 2. pdfplumber PDF Parser
    print("\n2. pdfplumber PDF Parser")
    print("-" * 30)
    try:
        pdfplumber_parser = PDFPlumberParser()
        text, metadata = pdfplumber_parser.extract_text(pdf_file)
        print(f"✓ pdfplumber extracted {len(text)} characters")
        print(f"  Pages: {metadata.get('total_pages', 'N/A')}")
        print(f"  Method: {metadata.get('extraction_method', 'N/A')}")
        
        # Try table extraction
        tables = pdfplumber_parser.extract_tables(pdf_file)
        print(f"  Tables found: {tables.get('total_tables', 0)}")
    except Exception as e:
        print(f"✗ pdfplumber failed: {e}")
    
    # 3. Tesseract OCR Parser
    print("\n3. Tesseract OCR Parser")
    print("-" * 30)
    try:
        ocr_parser = TesseractParser()
        text, metadata = ocr_parser.extract_text(image_file)
        print(f"✓ Tesseract extracted {len(text)} characters")
        print(f"  Confidence: {metadata.get('ocr_confidence', 'N/A'):.2f}%")
        print(f"  Language: {metadata.get('ocr_language', 'N/A')}")
    except Exception as e:
        print(f"✗ Tesseract failed: {e}")
    
    # 4. PaddleOCR Parser
    print("\n4. PaddleOCR Parser")
    print("-" * 30)
    try:
        paddle_parser = PaddleOCRParser()
        text, metadata = paddle_parser.extract_text(image_file)
        print(f"✓ PaddleOCR extracted {len(text)} characters")
        print(f"  Confidence: {metadata.get('ocr_confidence', 'N/A'):.2f}%")
        print(f"  Language: {metadata.get('ocr_language', 'N/A')}")
        
        # Try bounding box extraction
        bbox_result = paddle_parser.extract_text_with_bbox(image_file)
        print(f"  Text blocks: {bbox_result.get('total_blocks', 0)}")
    except Exception as e:
        print(f"✗ PaddleOCR failed: {e}")


def demo_preprocessors():
    """Demonstrate different preprocessor options."""
    print("\n" + "=" * 60)
    print("PREPROCESSORS DEMONSTRATION")
    print("=" * 60)
    
    # Check if test files exist
    image_file = Path("tests/test_assets/lenna.png")
    pdf_file = Path("tests/test_assets/dummy.pdf")
    
    if not image_file.exists():
        print(f"Image test file not found: {image_file}")
        return
    
    # 1. Image Preprocessor
    print("\n1. Image Preprocessor")
    print("-" * 30)
    try:
        img_preprocessor = ImagePreprocessor()
        
        # Process image with various options
        output_path, metadata = img_preprocessor.process(
            image_file,
            deskew=True,
            denoise=True,
            enhance_contrast=True,
            resize_factor=1.5
        )
        
        print(f"✓ Image processed successfully")
        print(f"  Output: {output_path}")
        print(f"  Steps applied: {metadata.get('processing_steps', [])}")
        print(f"  Original size: {metadata.get('image_info', {}).get('original_size', 'N/A')}")
        print(f"  Final size: {metadata.get('final_size', 'N/A')}")
        
        # OCR-optimized processing
        ocr_output, ocr_metadata = img_preprocessor.enhance_for_ocr(image_file)
        print(f"  OCR-optimized output: {ocr_output}")
        
    except Exception as e:
        print(f"✗ Image preprocessing failed: {e}")
    
    # 2. PDF Preprocessor
    print("\n2. PDF Preprocessor")
    print("-" * 30)
    try:
        pdf_preprocessor = PDFPreprocessor()
        
        # Split PDF
        split_output, split_metadata = pdf_preprocessor.process(
            pdf_file,
            operation='split',
            pages=[[0, 0]]  # Split first page only
        )
        
        print(f"✓ PDF split successfully")
        print(f"  Output directory: {split_output}")
        print(f"  Files created: {len(split_metadata.get('output_files', []))}")
        
        # Convert PDF to images
        convert_output, convert_metadata = pdf_preprocessor.process(
            pdf_file,
            operation='convert',
            format='png',
            dpi=150
        )
        
        print(f"✓ PDF converted to images")
        print(f"  Output directory: {convert_output}")
        print(f"  Images created: {len(convert_metadata.get('output_files', []))}")
        
    except Exception as e:
        print(f"✗ PDF preprocessing failed: {e}")


def demo_postprocessors():
    """Demonstrate different postprocessor options."""
    print("\n" + "=" * 60)
    print("POSTPROCESSORS DEMONSTRATION")
    print("=" * 60)
    
    # Sample text for processing
    sample_text = """
    This is a sample text with some formatting issues.
    
    There are multiple    spaces    here.
    
    And some "smart quotes" and 'curly apostrophes'.
    
    Teh text has some common OCR errors like "teh" instead of "the".
    
    Line breaks are inconsistent.
    
    """
    
    # 1. Text Postprocessor
    print("\n1. Text Postprocessor")
    print("-" * 30)
    try:
        text_postprocessor = TextPostprocessor()
        
        # Process text with various options
        processed_text, metadata = text_postprocessor.process(
            sample_text,
            remove_extra_whitespace=True,
            fix_line_breaks=True,
            normalize_quotes=True,
            fix_common_ocr_errors=True,
            extract_paragraphs=True
        )
        
        print(f"✓ Text processed successfully")
        print(f"  Original length: {metadata.get('original_length', 0)}")
        print(f"  Final length: {metadata.get('final_length', 0)}")
        print(f"  Steps applied: {metadata.get('processing_steps', [])}")
        
        # Convert to JSON
        json_text, json_metadata = text_postprocessor.process(
            sample_text,
            output_format='json'
        )
        print(f"  JSON output length: {len(json_text)}")
        
        # OCR-specific cleaning
        ocr_text, ocr_metadata = text_postprocessor.clean_for_ocr(sample_text)
        print(f"  OCR-cleaned length: {len(ocr_text)}")
        
    except Exception as e:
        print(f"✗ Text postprocessing failed: {e}")
    
    # 2. Table Postprocessor
    print("\n2. Table Postprocessor")
    print("-" * 30)
    try:
        table_postprocessor = TablePostprocessor()
        
        # Sample table data
        sample_table = [
            ["Name", "Age", "City"],
            ["John Doe", "30", "New York"],
            ["Jane Smith", "25", "Los Angeles"],
            ["Bob Johnson", "35", "Chicago"],
            ["", "", ""],  # Empty row
            ["Alice Brown", "28", "Boston"]
        ]
        
        # Process table
        output_path, metadata = table_postprocessor.process(
            sample_table,
            clean_cells=True,
            remove_empty_rows=True,
            normalize_headers=True,
            output_format='csv'
        )
        
        print(f"✓ Table processed successfully")
        print(f"  Output: {output_path}")
        print(f"  Original rows: {metadata.get('original_rows', 0)}")
        print(f"  Final rows: {metadata.get('final_rows', 0)}")
        print(f"  Steps applied: {metadata.get('processing_steps', [])}")
        
        # Convert to different formats
        json_path, _ = table_postprocessor.process(
            sample_table,
            output_format='json'
        )
        print(f"  JSON output: {json_path}")
        
        html_path, _ = table_postprocessor.process(
            sample_table,
            output_format='html'
        )
        print(f"  HTML output: {html_path}")
        
    except Exception as e:
        print(f"✗ Table postprocessing failed: {e}")


def demo_benchmarkers():
    """Demonstrate different benchmarker options."""
    print("\n" + "=" * 60)
    print("BENCHMARKERS DEMONSTRATION")
    print("=" * 60)
    
    # Check if test files exist
    pdf_file = Path("tests/test_assets/dummy.pdf")
    image_file = Path("tests/test_assets/lenna.png")
    
    if not pdf_file.exists():
        print(f"PDF test file not found: {pdf_file}")
        return
    
    # 1. Performance Benchmarker
    print("\n1. Performance Benchmarker")
    print("-" * 30)
    try:
        perf_benchmarker = PerformanceBenchmarker()
        
        # Benchmark PDF parsers
        pdf_parser = PDFParser()
        pdfplumber_parser = PDFPlumberParser()
        
        # Individual benchmark
        pdf_results = perf_benchmarker.benchmark(
            pdf_parser,
            pdf_file,
            iterations=2,
            warmup_runs=1
        )
        
        print(f"✓ Performance benchmark completed")
        print(f"  Parser: {pdf_results.get('parser_name', 'N/A')}")
        if 'metrics' in pdf_results and 'execution_time' in pdf_results['metrics']:
            et = pdf_results['metrics']['execution_time']
            print(f"  Mean execution time: {et.get('mean', 0):.3f}s")
            print(f"  Min execution time: {et.get('min', 0):.3f}s")
            print(f"  Max execution time: {et.get('max', 0):.3f}s")
        
        # Compare parsers
        comparison = perf_benchmarker.compare_parsers(
            [pdf_parser, pdfplumber_parser],
            pdf_file,
            iterations=2
        )
        
        print(f"  Comparison completed")
        if 'comparison' in comparison and 'fastest_parser' in comparison['comparison']:
            fastest = comparison['comparison']['fastest_parser']
            print(f"  Fastest parser: {fastest.get('name', 'N/A')}")
        
        # Generate report
        report_path = perf_benchmarker.generate_report("performance_report.md")
        print(f"  Report generated: {report_path}")
        
    except Exception as e:
        print(f"✗ Performance benchmarking failed: {e}")
    
    # 2. Accuracy Benchmarker
    print("\n2. Accuracy Benchmarker")
    print("-" * 30)
    try:
        acc_benchmarker = AccuracyBenchmarker()
        
        # Sample ground truth text
        ground_truth = "This is a sample document for testing OCR accuracy."
        
        # Benchmark OCR parsers
        ocr_parser = TesseractParser()
        
        # Individual accuracy benchmark
        acc_results = acc_benchmarker.benchmark(
            ocr_parser,
            image_file,
            ground_truth,
            normalize_text=True,
            ignore_case=True
        )
        
        print(f"✓ Accuracy benchmark completed")
        print(f"  Parser: {acc_results.get('parser_name', 'N/A')}")
        if 'metrics' in acc_results:
            metrics = acc_results['metrics']
            print(f"  Character accuracy: {metrics.get('character_accuracy', 0):.3f}")
            print(f"  Word accuracy: {metrics.get('word_accuracy', 0):.3f}")
            print(f"  Similarity ratio: {metrics.get('similarity_ratio', 0):.3f}")
        
        # Generate detailed report
        report_path = acc_benchmarker.generate_detailed_report("accuracy_report.md")
        print(f"  Detailed report generated: {report_path}")
        
    except Exception as e:
        print(f"✗ Accuracy benchmarking failed: {e}")


def main():
    """Run all demonstrations."""
    print("DocCraft - All Options Demonstration")
    print("This script shows how to use all available options in DocCraft")
    print("=" * 80)
    
    # Run demonstrations
    demo_parsers()
    demo_preprocessors()
    demo_postprocessors()
    demo_benchmarkers()
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETED")
    print("=" * 80)
    print("\nSummary of available options:")
    print("\nParsers:")
    print("  - PDFParser (PyMuPDF): Fast PDF text extraction")
    print("  - PDFPlumberParser: PDF text and table extraction")
    print("  - TesseractParser (Tesseract): Traditional OCR engine")
    print("  - PaddleOCRParser: Modern OCR with better accuracy")
    
    print("\nPreprocessors:")
    print("  - ImagePreprocessor: Image enhancement for OCR")
    print("  - PDFPreprocessor: PDF splitting, merging, conversion")
    
    print("\nPostprocessors:")
    print("  - TextPostprocessor: Text cleaning and formatting")
    print("  - TablePostprocessor: Table data extraction and formatting")
    
    print("\nBenchmarkers:")
    print("  - PerformanceBenchmarker: Speed and resource usage")
    print("  - AccuracyBenchmarker: Accuracy against ground truth")
    
    print("\nEach component is modular and can be used independently!")
    print("Check the generated reports for detailed results.")


if __name__ == "__main__":
    main() 