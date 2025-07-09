#!/usr/bin/env python3
"""
Demo script for the PDF parser.

This script demonstrates how to use the PDFParser class to extract
text and metadata from PDF documents.
"""

import sys
from pathlib import Path
from doccraft.parsers import PDFParser


def demo_pdf_parser():
    """
    Demonstrate the PDF parser functionality.
    
    This function shows how to:
    1. Create a PDF parser instance
    2. Extract text from a PDF
    3. Extract metadata from a PDF
    4. Handle errors gracefully
    """
    print("🔍 DocCraft PDF Parser Demo")
    print("=" * 50)
    
    # Create a PDF parser instance
    parser = PDFParser()
    
    # Display parser information
    print(f"📋 Parser Information:")
    print(f"   Name: {parser.name}")
    print(f"   Version: {parser.version}")
    print(f"   Supported formats: {parser.supported_formats}")
    print()
    
    # Test with a sample PDF file
    # You can replace this with the path to your own PDF file
    sample_pdf = "sample_document.pdf"
    
    if Path(sample_pdf).exists():
        print(f"📄 Processing: {sample_pdf}")
        print("-" * 30)
        
        # Extract text and metadata
        result = parser.extract_text(sample_pdf)
        
        if result['error'] is None:
            print("✅ Text extraction successful!")
            print(f"⏱️  Extraction time: {result['extraction_time']:.3f} seconds")
            print(f"📊 Pages extracted: {len(result['metadata']['pages_extracted'])}")
            print(f"📄 Total pages: {result['metadata']['total_pages']}")
            print(f"📏 File size: {result['metadata']['file_size']:,} bytes")
            
            # Show a preview of the extracted text
            text_preview = result['text'][:500] + "..." if len(result['text']) > 500 else result['text']
            print(f"\n📝 Text preview:")
            print(f"   {text_preview}")
            
            # Show metadata
            print(f"\n📋 Document metadata:")
            if result['metadata']['document_title']:
                print(f"   Title: {result['metadata']['document_title']}")
            if result['metadata']['document_author']:
                print(f"   Author: {result['metadata']['document_author']}")
            if result['metadata']['document_subject']:
                print(f"   Subject: {result['metadata']['document_subject']}")
            
        else:
            print(f"❌ Error during extraction: {result['error']}")
    
    else:
        print(f"⚠️  Sample PDF file '{sample_pdf}' not found.")
        print("   Create a PDF file named 'sample_document.pdf' in the current directory to test.")
    
    print("\n" + "=" * 50)
    
    # Demonstrate error handling
    print("🧪 Testing error handling:")
    
    # Test with non-existent file
    print("   Testing with non-existent file...")
    result = parser.extract_text("nonexistent.pdf")
    if result['error']:
        print(f"   ✅ Correctly handled error: {result['error']}")
    
    # Test with unsupported file type
    print("   Testing with unsupported file type...")
    result = parser.extract_text("document.txt")
    if result['error']:
        print(f"   ✅ Correctly rejected unsupported format: {result['error']}")
    
    print("\n🎉 Demo completed!")


def demo_metadata_only():
    """
    Demonstrate metadata-only extraction (faster than full text extraction).
    """
    print("\n🔍 Metadata-Only Extraction Demo")
    print("=" * 50)
    
    parser = PDFParser()
    sample_pdf = "sample_document.pdf"
    
    if Path(sample_pdf).exists():
        print(f"📄 Extracting metadata from: {sample_pdf}")
        
        try:
            metadata = parser.extract_metadata_only(sample_pdf)
            
            print("✅ Metadata extraction successful!")
            print(f"📊 Total pages: {metadata['total_pages']}")
            print(f"📏 File size: {metadata['file_size']:,} bytes")
            
            if metadata['document_title']:
                print(f"📋 Title: {metadata['document_title']}")
            if metadata['document_author']:
                print(f"👤 Author: {metadata['document_author']}")
            if metadata['document_subject']:
                print(f"📝 Subject: {metadata['document_subject']}")
            if metadata['document_creator']:
                print(f"🛠️  Creator: {metadata['document_creator']}")
            
        except Exception as e:
            print(f"❌ Error extracting metadata: {e}")
    else:
        print(f"⚠️  Sample PDF file '{sample_pdf}' not found.")


if __name__ == "__main__":
    # Run the main demo
    demo_pdf_parser()
    
    # Run metadata-only demo
    demo_metadata_only()
    
    print("\n💡 Usage Tips:")
    print("   - Use extract_text() for full text extraction")
    print("   - Use extract_metadata_only() for faster metadata extraction")
    print("   - Check result['error'] to handle errors gracefully")
    print("   - Use result['extraction_time'] to measure performance") 