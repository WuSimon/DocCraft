#!/usr/bin/env python3
"""
Simple test script to verify the DocCraft package structure.
"""

def test_package_import():
    """Test that the package can be imported."""
    try:
        import doccraft
        print(f"✅ Package imported successfully!")
        print(f"   Version: {doccraft.__version__}")
        print(f"   Author: {doccraft.__author__}")
    except ImportError as e:
        print(f"❌ Failed to import doccraft: {e}")
        assert False, f"Package import failed: {e}"

def test_submodules_exist():
    """Test that all submodules exist."""
    try:
        import doccraft
        
        # Check that submodules can be imported
        assert hasattr(doccraft, 'parsers')
        assert hasattr(doccraft, 'preprocessing')
        assert hasattr(doccraft, 'postprocessing')
        assert hasattr(doccraft, 'benchmarking')
        
        print("✅ All submodules exist:")
        print("   - doccraft.parsers")
        print("   - doccraft.preprocessing")
        print("   - doccraft.postprocessing")
        print("   - doccraft.benchmarking")
    except Exception as e:
        print(f"❌ Submodule test failed: {e}")
        assert False, f"Submodule test failed: {e}"

def test_package_metadata():
    """Test package metadata."""
    try:
        import doccraft
        
        # Check version
        assert doccraft.__version__ == "0.1.0"
        
        # Check author
        assert doccraft.__author__ == "Simon"
        
        # Check that __all__ is defined
        assert hasattr(doccraft, '__all__')
        
        print("✅ Package metadata is correct")
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        assert False, f"Metadata test failed: {e}"

if __name__ == "__main__":
    print("🧪 Testing DocCraft package structure...\n")
    
    tests = [
        test_package_import,
        test_submodules_exist,
        test_package_metadata,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package structure is correct.")
    else:
        print("⚠️  Some tests failed. Please check the package structure.") 