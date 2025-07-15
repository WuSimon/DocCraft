"""
Document benchmarking module.

Contains tools for performance evaluation:
- Speed and accuracy metrics
- Comparison across different parsers
- Performance reporting and visualization
"""

# Import the base benchmarker class
from .base_benchmarker import BaseBenchmarker

# Import specific benchmarker implementations
from .performance_benchmarker import PerformanceBenchmarker
from .accuracy_benchmarker import AccuracyBenchmarker
from .docvqa_benchmarker import DocVQABenchmarker

# Define what gets imported when someone does "from doccraft.benchmarking import *"
__all__ = [
    'BaseBenchmarker',
    'PerformanceBenchmarker',
    'AccuracyBenchmarker',
    'DocVQABenchmarker',
] 