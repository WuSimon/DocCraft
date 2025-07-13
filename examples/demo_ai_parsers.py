#!/usr/bin/env python3
"""
Demo script for AI-powered document parsers.

This script demonstrates the capabilities of the new AI parsers:
- LayoutLMv3: Structured document understanding with layout awareness
- Qwen-VL-Plus: Multimodal document understanding with complex reasoning

Usage:
    python demo_ai_parsers.py [--model layoutlmv3|qwen-vl] [--device cpu|cuda|mps]
"""

import argparse
import time
from pathlib import Path
from typing import Optional

# Import DocCraft parsers
from doccraft.parsers import (
    PDFParser, PDFPlumberParser, OCRParser, PaddleOCRParser
)

# Try to import AI parsers
try:
    from doccraft.parsers import LayoutLMv3Parser, QwenVLParser
    AI_PARSERS_AVAILABLE = True
except ImportError:
    AI_PARSERS_AVAILABLE = False
    print("⚠️  AI parsers not available. Install with: pip install doccraft[ai]")
    print("   Required: transformers>=4.30.0, torch>=2.0.0")


def demo_layoutlmv3_parser(device: str = "auto"):
    """
    Demonstrate LayoutLMv3 parser capabilities.
    
    Args:
        device: Device to use for inference
    """
    print("=" * 60)
    print("LAYOUTLMV3 PARSER DEMO")
    print("=" * 60)
    
    if not AI_PARSERS_AVAILABLE:
        print("❌ AI parsers not available")
        return
    
    try:
        # Initialize LayoutLMv3 parser
        print("🔄 Initializing LayoutLMv3 parser...")
        parser = LayoutLMv3Parser(
            model_name="microsoft/layoutlmv3-base",
            device=device,
            task="document_understanding"
        )
        print(f"✅ LayoutLMv3 parser initialized on {parser.device}")
        
        # Test with a sample document
        test_file = "tests/test_files/dummy.pdf"
        if not Path(test_file).exists():
            print(f"⚠️  Test file not found: {test_file}")
            print("   Using any available test file...")
            test_files = list(Path("tests/test_files").glob("*"))
            if test_files:
                test_file = str(test_files[0])
            else:
                print("❌ No test files found")
                return
        
        print(f"\n📄 Processing: {test_file}")
        
        # Basic text extraction
        print("\n1️⃣ Basic Text Extraction:")
        start_time = time.time()
        result = parser.extract_text(test_file)
        extraction_time = time.time() - start_time
        
        if result['error']:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success! Extracted {len(result['text'])} characters")
            print(f"⏱️  Time: {extraction_time:.2f}s")
            print(f"📊 Confidence: {result['metadata'].get('ai_model_output', {}).get('confidence', 'N/A')}")
            print(f"📝 Text preview: {result['text'][:200]}...")
        
        # Layout information extraction
        print("\n2️⃣ Layout Information Extraction:")
        layout_info = parser.extract_layout_info(test_file)
        if 'error' not in layout_info:
            print(f"✅ Image size: {layout_info.get('image_size', 'N/A')}")
            print(f"✅ Bounding boxes: {len(layout_info.get('bbox', []))} regions")
            print(f"✅ Attention mask shape: {layout_info.get('attention_mask', 'N/A')}")
        else:
            print(f"❌ Error: {layout_info['error']}")
        
        # Task switching demonstration
        print("\n3️⃣ Task Switching Demo:")
        tasks = ["document_understanding", "classification", "ner"]
        for task in tasks:
            print(f"\n   🔄 Switching to task: {task}")
            parser.set_task(task)
            print(f"   ✅ Current task: {parser.task}")
            print(f"   📋 Supported tasks: {parser.get_supported_tasks()}")
        
        print(f"\n🎉 LayoutLMv3 demo completed!")
        
    except Exception as e:
        print(f"❌ Error in LayoutLMv3 demo: {e}")


def demo_qwen_vl_parser(device: str = "auto"):
    """
    Demonstrate Qwen-VL-Plus parser capabilities.
    
    Args:
        device: Device to use for inference
    """
    print("=" * 60)
    print("QWEN-VL-PLUS PARSER DEMO")
    print("=" * 60)
    
    if not AI_PARSERS_AVAILABLE:
        print("❌ AI parsers not available")
        return
    
    try:
        # Initialize Qwen-VL-Plus parser
        print("🔄 Initializing Qwen-VL-Plus parser...")
        parser = QwenVLParser(
            model_name="Qwen/Qwen-VL-Plus",
            device=device,
            max_length=2048,
            temperature=0.1
        )
        print(f"✅ Qwen-VL-Plus parser initialized on {parser.device}")
        
        # Test with a sample document
        test_file = "tests/test_files/dummy.pdf"
        if not Path(test_file).exists():
            print(f"⚠️  Test file not found: {test_file}")
            print("   Using any available test file...")
            test_files = list(Path("tests/test_files").glob("*"))
            if test_files:
                test_file = str(test_files[0])
            else:
                print("❌ No test files found")
                return
        
        print(f"\n📄 Processing: {test_file}")
        
        # Basic text extraction
        print("\n1️⃣ Basic Text Extraction:")
        start_time = time.time()
        result = parser.extract_text(test_file)
        extraction_time = time.time() - start_time
        
        if result['error']:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success! Extracted {len(result['text'])} characters")
            print(f"⏱️  Time: {extraction_time:.2f}s")
            print(f"📝 Text preview: {result['text'][:200]}...")
        
        # Question answering
        print("\n2️⃣ Question Answering Demo:")
        questions = [
            "What type of document is this?",
            "What is the main topic of this document?",
            "Are there any numbers or dates mentioned?"
        ]
        
        for question in questions:
            print(f"\n   ❓ Question: {question}")
            start_time = time.time()
            answer_result = parser.ask_question(test_file, question)
            qa_time = time.time() - start_time
            
            if 'error' not in answer_result:
                print(f"   ✅ Answer: {answer_result['answer']}")
                print(f"   ⏱️  Time: {qa_time:.2f}s")
            else:
                print(f"   ❌ Error: {answer_result['error']}")
        
        # Structured information extraction
        print("\n3️⃣ Structured Information Extraction:")
        fields = ["document_type", "date", "amount", "sender"]
        print(f"   🔍 Extracting fields: {fields}")
        
        start_time = time.time()
        structured_result = parser.extract_structured_info(test_file, fields)
        struct_time = time.time() - start_time
        
        if 'error' not in structured_result:
            print(f"   ✅ Extracted data: {structured_result['data']}")
            print(f"   ⏱️  Time: {struct_time:.2f}s")
        else:
            print(f"   ❌ Error: {structured_result['error']}")
        
        # Document summarization
        print("\n4️⃣ Document Summarization:")
        start_time = time.time()
        summary_result = parser.summarize_document(test_file)
        summary_time = time.time() - start_time
        
        if 'error' not in summary_result:
            print(f"   ✅ Summary: {summary_result['answer']}")
            print(f"   ⏱️  Time: {summary_time:.2f}s")
        else:
            print(f"   ❌ Error: {summary_result['error']}")
        
        # Model capabilities
        print("\n5️⃣ Model Capabilities:")
        capabilities = parser.get_model_capabilities()
        for capability in capabilities:
            print(f"   ✅ {capability}")
        
        print(f"\n🎉 Qwen-VL-Plus demo completed!")
        
    except Exception as e:
        print(f"❌ Error in Qwen-VL-Plus demo: {e}")


def compare_parsers(test_file: str, device: str = "auto"):
    """
    Compare AI parsers with traditional parsers.
    
    Args:
        test_file: Path to test file
        device: Device to use for AI parsers
    """
    print("=" * 60)
    print("PARSER COMPARISON")
    print("=" * 60)
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    # Traditional parsers
    traditional_parsers = {
        'Tesseract': OCRParser(),
        'PaddleOCR': PaddleOCRParser(),
        'PyMuPDF': PDFParser(),
        'PDFPlumber': PDFPlumberParser()
    }
    
    # AI parsers (if available)
    ai_parsers = {}
    if AI_PARSERS_AVAILABLE:
        try:
            ai_parsers['LayoutLMv3'] = LayoutLMv3Parser(device=device)
            ai_parsers['Qwen-VL-Plus'] = QwenVLParser(device=device)
        except Exception as e:
            print(f"⚠️  Could not initialize AI parsers: {e}")
    
    all_parsers = {**traditional_parsers, **ai_parsers}
    
    print(f"📄 Testing file: {test_file}")
    print(f"🔧 Total parsers: {len(all_parsers)}")
    print(f"   Traditional: {len(traditional_parsers)}")
    print(f"   AI: {len(ai_parsers)}")
    
    results = {}
    
    for name, parser in all_parsers.items():
        print(f"\n🔄 Testing {name}...")
        try:
            start_time = time.time()
            result = parser.extract_text(test_file)
            extraction_time = time.time() - start_time
            
            if result['error']:
                print(f"   ❌ Error: {result['error']}")
                results[name] = {'error': result['error'], 'time': extraction_time}
            else:
                text_length = len(result['text'])
                print(f"   ✅ Success: {text_length} characters in {extraction_time:.2f}s")
                results[name] = {
                    'text_length': text_length,
                    'time': extraction_time,
                    'text_preview': result['text'][:100]
                }
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[name] = {'error': str(e), 'time': 0}
    
    # Summary
    print(f"\n📊 COMPARISON SUMMARY")
    print("-" * 40)
    
    successful_parsers = {k: v for k, v in results.items() if 'error' not in v}
    
    if successful_parsers:
        fastest = min(successful_parsers.items(), key=lambda x: x[1]['time'])
        longest_text = max(successful_parsers.items(), key=lambda x: x[1]['text_length'])
        
        print(f"🏆 Fastest: {fastest[0]} ({fastest[1]['time']:.2f}s)")
        print(f"📝 Most text: {longest_text[0]} ({longest_text[1]['text_length']} chars)")
        
        print(f"\n📋 Detailed Results:")
        for name, result in results.items():
            if 'error' in result:
                print(f"   {name}: ❌ {result['error']}")
            else:
                print(f"   {name}: ✅ {result['text_length']} chars, {result['time']:.2f}s")
    
    print(f"\n🎉 Comparison completed!")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Demo AI-powered document parsers")
    parser.add_argument('--model', choices=['layoutlmv3', 'qwen-vl', 'compare'], 
                       default='compare', help='Which model to demo')
    parser.add_argument('--device', choices=['cpu', 'cuda', 'mps', 'auto'], 
                       default='auto', help='Device to use for AI models')
    parser.add_argument('--test-file', type=str, 
                       default='tests/test_files/dummy.pdf',
                       help='Test file to use')
    
    args = parser.parse_args()
    
    print("🤖 DocCraft AI Parser Demo")
    print("=" * 60)
    
    if args.model == 'layoutlmv3':
        demo_layoutlmv3_parser(args.device)
    elif args.model == 'qwen-vl':
        demo_qwen_vl_parser(args.device)
    elif args.model == 'compare':
        compare_parsers(args.test_file, args.device)
    
    print(f"\n✨ Demo completed!")
    print(f"\n💡 Tips:")
    print(f"   - Install AI dependencies: pip install doccraft[ai]")
    print(f"   - Use GPU for better performance: --device cuda")
    print(f"   - Try different models: --model layoutlmv3|qwen-vl")


if __name__ == "__main__":
    main() 