import pytest
from doccraft.benchmarking import AccuracyBenchmarker, PerformanceBenchmarker, DocVQABenchmarker
from pathlib import Path

def test_accuracy_benchmarker_instantiation():
    bench = AccuracyBenchmarker()
    assert hasattr(bench, "benchmark")

def test_performance_benchmarker_instantiation():
    bench = PerformanceBenchmarker()
    assert hasattr(bench, "benchmark")

def test_docvqa_benchmarker_instantiation():
    gt = Path("tests/data/docvqa/dummy_gt.json")
    images = Path("tests/data/docvqa/dummy_images/")
    if not gt.exists() or not images.exists():
        pytest.skip("DocVQA dummy ground truth or images not found")
    bench = DocVQABenchmarker(str(gt), str(images))
    assert hasattr(bench, "benchmark")

# Optionally, add minimal functional tests if you have a mock parser and data 