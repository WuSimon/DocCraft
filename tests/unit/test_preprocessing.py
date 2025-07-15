import pytest
from pathlib import Path
from doccraft.preprocessing import ImagePreprocessor, PDFPreprocessor
import os

data_dir = Path(os.path.dirname(__file__)).parent / "data"

@pytest.mark.skipif(ImagePreprocessor is None, reason="ImagePreprocessor not available")
def test_image_preprocessor_instantiation():
    pre = ImagePreprocessor()
    assert pre.name == "Image Preprocessor"
    assert hasattr(pre, "process")

@pytest.mark.skipif(ImagePreprocessor is None, reason="ImagePreprocessor not available")
def test_image_preprocessor_process():
    pre = ImagePreprocessor()
    img_path = data_dir / "lenna.png"
    if not img_path.exists():
        pytest.skip("lenna.png not found")
    out_path, meta = pre.process(img_path, deskew=False, denoise=False, enhance_contrast=False, binarize=False)
    assert Path(out_path).exists()
    assert meta["enhancement_applied"]

@pytest.mark.skipif(PDFPreprocessor is None, reason="PDFPreprocessor not available")
def test_pdf_preprocessor_instantiation():
    pre = PDFPreprocessor()
    assert pre.name == "PDF Preprocessor"
    assert hasattr(pre, "process")

@pytest.mark.skipif(PDFPreprocessor is None, reason="PDFPreprocessor not available")
def test_pdf_preprocessor_noop():
    pre = PDFPreprocessor()
    pdf_path = data_dir / "dummy.pdf"
    if not pdf_path.exists():
        pytest.skip("dummy.pdf not found")
    out_path, meta = pre.process(pdf_path)
    assert Path(out_path) == pdf_path
    assert meta["operation"] == "noop" 