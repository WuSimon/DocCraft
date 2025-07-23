#!/usr/bin/env python3
"""
Example: How to add custom components to DocCraft registries

This example demonstrates how to extend DocCraft with custom parsers,
preprocessors, postprocessors, and benchmarkers.
"""

from pathlib import Path
import sys

# Add the src directory to the path so we can import doccraft
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from doccraft.parsers.base_parser import BaseParser
from doccraft.preprocessing.base_preprocessor import BasePreprocessor
from doccraft.postprocessing.base_postprocessor import BasePostprocessor
from doccraft.benchmarking.base_benchmarker import BaseBenchmarker

# Example 1: Custom Parser
class CustomTextParser(BaseParser):
    """A simple custom parser that just returns a fixed text."""
    
    def __init__(self):
        super().__init__(
            name="CustomTextParser",
            version="1.0.0",
            supported_formats=['.txt', '.md', '.py']
        )
    
    def _extract_text_impl(self, file_path, **kwargs):
        """Implement the abstract method for text extraction."""
        # In a real implementation, you would read the file here
        # For this example, we'll just return a fixed text
        text = 'This is custom extracted text from my parser!'
        metadata = {
            'parser': 'custom_text',
            'file_path': str(file_path),
            'custom_metadata': 'example'
        }
        return text, metadata
    
    def can_parse(self, input_data):
        """Check if this parser can handle the input."""
        return isinstance(input_data, (str, Path))
    
    def get_parser_info(self):
        """Get information about this parser."""
        return {
            'name': 'custom_text',
            'description': 'A custom text parser example',
            'version': '1.0.0'
        }

# Example 2: Custom Preprocessor
class CustomImagePreprocessor(BasePreprocessor):
    """A custom image preprocessor that adds a watermark."""
    
    def __init__(self):
        super().__init__(name="CustomImagePreprocessor")
    
    def process(self, input_data):
        """Process the input data."""
        # In a real implementation, you would process the image here
        processed_path = str(input_data) + "_processed"
        metadata = {
            'original_path': str(input_data),
            'processed_path': processed_path,
            'operations': ['watermark_added']
        }
        return processed_path, metadata
    
    def can_process(self, input_data):
        """Check if this preprocessor can handle the input."""
        return str(input_data).lower().endswith(('.jpg', '.jpeg', '.png'))
    
    def get_preprocessor_info(self):
        """Get information about this preprocessor."""
        return {
            'name': 'custom_image',
            'description': 'A custom image preprocessor with watermark',
            'version': '1.0.0'
        }

# Example 3: Custom Postprocessor
class CustomTextPostprocessor(BasePostprocessor):
    """A custom text postprocessor that converts to uppercase."""
    
    def __init__(self):
        super().__init__(
            name="CustomTextPostprocessor",
            version="1.0.0",
            supported_formats=['text', 'string']
        )
    
    def process(self, input_data):
        """Process the input text."""
        processed_text = input_data.upper()
        metadata = {
            'original_length': len(input_data),
            'processed_length': len(processed_text),
            'operations': ['uppercase_conversion']
        }
        return processed_text, metadata
    
    def can_process(self, input_data):
        """Check if this postprocessor can handle the input."""
        return isinstance(input_data, str)
    
    def get_postprocessor_info(self):
        """Get information about this postprocessor."""
        return {
            'name': 'custom_text',
            'description': 'A custom text postprocessor that converts to uppercase',
            'version': '1.0.0'
        }

# Example 4: Custom Benchmarker
class CustomBenchmarker(BaseBenchmarker):
    """A custom benchmarker that measures text length."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="CustomBenchmarker",
            version="1.0.0",
            supported_metrics=['text_length', 'word_count', 'character_count']
        )
        self.results = []
    
    def benchmark(self, parser, input_data, **kwargs):
        """Run the benchmark."""
        # Extract text using the parser
        result = parser.extract_text(input_data, **kwargs)
        text = result.get('text', '')
        
        # Calculate metrics
        metrics = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'character_count': len(text.replace(' ', '')),
            'parser_name': parser.__class__.__name__
        }
        
        self.results.append(metrics)
        return metrics
    
    def calculate_metrics(self, results, ground_truth=None):
        """Calculate aggregate metrics."""
        if not results:
            return {}
        
        avg_length = sum(r['text_length'] for r in results) / len(results)
        avg_words = sum(r['word_count'] for r in results) / len(results)
        
        return {
            'average_text_length': avg_length,
            'average_word_count': avg_words,
            'total_benchmarks': len(results)
        }
    
    def generate_report(self, results, output_dir, parser_name):
        """Generate a report."""
        print(f"Custom benchmark report for {parser_name}:")
        print(f"Average text length: {results.get('average_text_length', 0):.2f}")
        print(f"Average word count: {results.get('average_word_count', 0):.2f}")
    
    def get_benchmarker_info(self):
        """Get information about this benchmarker."""
        return {
            'name': 'custom',
            'description': 'A custom benchmarker that measures text length',
            'version': '1.0.0'
        }

def demonstrate_registration():
    """Demonstrate how to register custom components."""
    
    print("=== DocCraft Custom Component Registration Example ===\n")
    
    # Create instances of our custom components
    custom_parser = CustomTextParser()
    custom_preprocessor = CustomImagePreprocessor()
    custom_postprocessor = CustomTextPostprocessor()
    custom_benchmarker = CustomBenchmarker()
    
    # Test the components
    print("1. Testing Custom Parser:")
    result = custom_parser.extract_text("test_input.txt")
    print(f"   Result: {result['text']}")
    print(f"   Can parse 'test.txt': {custom_parser.can_parse('test.txt')}")
    
    print("\n2. Testing Custom Preprocessor:")
    processed, metadata = custom_preprocessor.process("image.jpg")
    print(f"   Processed: {processed}")
    print(f"   Metadata: {metadata}")
    print(f"   Can process 'image.jpg': {custom_preprocessor.can_process('image.jpg')}")
    
    print("\n3. Testing Custom Postprocessor:")
    processed_text, metadata = custom_postprocessor.process("hello world")
    print(f"   Processed: {processed_text}")
    print(f"   Metadata: {metadata}")
    print(f"   Can process 'hello': {custom_postprocessor.can_process('hello')}")
    
    print("\n4. Testing Custom Benchmarker:")
    metrics = custom_benchmarker.benchmark(custom_parser, "test_input.txt")
    print(f"   Metrics: {metrics}")
    
    print("\n=== Registration Instructions ===")
    print("To register these components, add the following to the respective __init__.py files:")
    print("\nIn src/doccraft/parsers/__init__.py:")
    print("from .custom_parser import CustomTextParser")
    print("PARSER_REGISTRY['custom_text'] = CustomTextParser")
    print("__all__.append('CustomTextParser')")
    
    print("\nIn src/doccraft/preprocessing/__init__.py:")
    print("from .custom_preprocessor import CustomImagePreprocessor")
    print("PREPROCESSOR_REGISTRY['custom_image'] = CustomImagePreprocessor")
    print("__all__.append('CustomImagePreprocessor')")
    
    print("\nIn src/doccraft/postprocessing/__init__.py:")
    print("from .custom_postprocessor import CustomTextPostprocessor")
    print("POSTPROCESSOR_REGISTRY['custom_text'] = CustomTextPostprocessor")
    print("__all__.append('CustomTextPostprocessor')")
    
    print("\nIn src/doccraft/benchmarking/__init__.py:")
    print("from .custom_benchmarker import CustomBenchmarker")
    print("BENCHMARKER_REGISTRY['custom'] = CustomBenchmarker")
    print("__all__.append('CustomBenchmarker')")
    
    print("\nAfter registration, you can use them via:")
    print("doccraft pipeline --parser custom_text --input file.txt")
    print("doccraft pipeline --preprocessor custom_image --input image.jpg")
    print("doccraft pipeline --postprocessor custom_text --input 'some text'")
    print("doccraft pipeline --benchmarker custom --input file.txt")

if __name__ == "__main__":
    demonstrate_registration() 