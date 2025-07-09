"""
Setup configuration for DocCraft package.
"""

from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="doccraft",
    version="0.1.0",
    author="Simon",
    author_email="your.email@example.com",
    description="Intelligent Document Processing & Benchmarking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WuSimon/DocCraft",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "numpy>=1.21.0",
        "Pillow>=8.0.0",
        
        # PDF processing
        "PyMuPDF>=1.18.0",
        "pdf2image>=1.16.0",
        
        # OCR
        "pytesseract>=0.3.8",
        
        # Image processing
        "opencv-python>=4.5.0",
        
        # Data processing
        "pandas>=1.3.0",
        
        # Testing
        "pytest>=6.0.0",
        "pytest-cov>=2.0.0",
    ],
    extras_require={
        "dev": [
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "pre-commit>=2.15.0",
        ],
        "ai": [
            "transformers>=4.0.0",
            "torch>=1.9.0",
            "torchvision>=0.10.0",
        ],
        "benchmarking": [
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "doccraft=doccraft.cli:main",
        ],
    },
) 