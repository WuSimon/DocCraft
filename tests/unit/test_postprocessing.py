import pytest
from doccraft.postprocessing import TextPostprocessor, TablePostprocessor
from pathlib import Path

def test_text_postprocessor_instantiation():
    post = TextPostprocessor()
    assert post.name == "Text Postprocessor" or hasattr(post, "process")

def test_text_postprocessor_process():
    post = TextPostprocessor()
    text = "This is a test.\n\nNew paragraph!"
    cleaned, meta = post.process(text)
    assert isinstance(cleaned, str)
    assert "word_count" in meta.get("text_statistics", {})

def test_table_postprocessor_instantiation():
    post = TablePostprocessor()
    assert post.name == "Table Postprocessor" or hasattr(post, "process")

def test_table_postprocessor_process():
    post = TablePostprocessor()
    table_text = "A,B\n1,2\n3,4"
    processed, meta = post.process(table_text)
    assert isinstance(processed, (str, Path))
    assert isinstance(meta, dict) 