# DocCraft

A comprehensive document processing and question-answering toolkit.

## Project Structure

```
DocCraft/
├── doccraft/                    # Main package source code
├── tests/                       # Test files organized by type
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── data/                    # Test data and files
├── scripts/                     # Utility scripts and tools
│   └── docvqa/                  # DocVQA-specific scripts
├── docs/                        # Documentation and processed data
├── results/                     # Benchmark results and predictions
├── examples/                    # Example usage and demos
├── presentation/                # Presentation materials
└── Roadmap.md                  # Project roadmap
```

## Quick Start

1. Install the package:
   ```bash
   cd doccraft
   pip install -e .
   ```

2. Run examples:
   ```bash
   python examples/demo_ai_parsers.py
   ```

3. Run DocVQA benchmarks:
   ```bash
   python scripts/docvqa/docvqa_benchmark.py --parser layoutlmv3 --documents path/to/documents
   ```

4. Run tests:
   ```bash
   # Unit tests
   python -m pytest tests/unit/
   
   # Integration tests
   python -m pytest tests/integration/
   ```

## Key Files

- **Main Package**: `doccraft/` - Core functionality
- **DocVQA Scripts**: `scripts/docvqa/` - DocVQA benchmarking and evaluation
- **Examples**: `examples/` - Usage examples and demos
- **Results**: `results/` - Benchmark outputs and predictions
- **Scripts**: `scripts/` - Utility tools and analysis scripts
- **Tests**: `tests/` - Organized test suites

## Documentation

See `docs/` for detailed documentation and integration guides. 