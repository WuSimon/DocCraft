"""
Test package structure and basic imports.
"""

import pytest


def test_package_import():
    """Test that the package can be imported."""
    try:
        import doccraft
        assert doccraft.__version__ == "0.1.0"
        assert doccraft.__author__ == "Simon"
    except ImportError as e:
        pytest.fail(f"Failed to import doccraft: {e}")


def test_submodules_exist():
    """Test that all submodules exist."""
    import doccraft
    
    # Check that submodules can be imported
    assert hasattr(doccraft, 'parsers')
    assert hasattr(doccraft, 'preprocessing')
    assert hasattr(doccraft, 'postprocessing')
    assert hasattr(doccraft, 'benchmarking')


def test_package_metadata():
    """Test package metadata."""
    import doccraft
    
    # Check version
    assert doccraft.__version__ == "0.1.0"
    
    # Check author
    assert doccraft.__author__ == "Simon"
    
    # Check that __all__ is defined
    assert hasattr(doccraft, '__all__') 