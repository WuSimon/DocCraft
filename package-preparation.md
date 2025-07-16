# DocCraft Package Preparation Checklist

This checklist guides the process of preparing DocCraft for robust, user-friendly release. It covers code hygiene, parser registry, dependencies, packaging, testing, and documentation.

---

## 1. Parser Refactoring and Registry Consistency
- [x] All references to the OCR parser use 'tesseract' (except for PaddleOCR or generic OCR)
- [x] `TesseractParser` class and file exist; all imports and registries updated
- [x] Parser registry in `doccraft/parsers/__init__.py` includes all concrete parsers with correct keys
- [x] `__all__` list includes all relevant parsers

## 2. Testing and Fixture Fixes
- [x] All test fixtures use proper pytest patterns
- [x] All tests pass (except expected skips for missing optional dependencies)

## 3. Codebase Hygiene and Documentation
- [x] Unused/legacy scripts deleted
- [x] All modules have docstrings and type hints
- [x] README and user-facing docs are up-to-date and consistent

## 4. Dependency and Packaging Hygiene
- [x] Core dependencies in `install_requires` in `setup.py`
- [x] Optional dependencies in `extras_require` (e.g., 'ai')
- [x] PaddleOCR is a core dependency
- [x] `requirements.txt` and `MANIFEST.in` are at project root and up-to-date
- [x] `MANIFEST.in` includes all necessary files (README, LICENSE, assets, etc.)
- [x] Fixed missing matplotlib dependency in AI extras (required by Qwen-VL)

## 5. Testing Installation and CLI
- [x] Install package in a fresh environment (core and with '[ai]')
- [x] Test CLI and minimal import
- [x] README has clear installation instructions (quotes around extras, etc.)

## 6. Optional AI Features and Testing
- [x] AI dependencies install and import cleanly
- [x] AI parser tests include all relevant parsers (QwenVL, LayoutLMv3, DeepSeekVL, etc.)
- [x] All tests pass for optional features if dependencies are present

## 7. General Project Structure and Best Practices
- [x] Project uses modern Python packaging (src layout, root-level manifest/requirements, clear README)
- [x] Release version and changelog updated
- [ ] Git tag created for release

---

## Notes
- Use quotes around extras in pip install: `pip install '.[ai]'`
- PaddleOCR is now a core dependency, not optional
- All parser keys in registries and CLI/configs are lowercase and consistent
- User-facing documentation refers to 'tesseract' as the parser name, not 'ocr'
- Example scripts and tests use updated parser names

---

## Release Steps
1. Final code and doc review
2. Update version and changelog
3. Run all tests
4. Build and check package
5. (Optional) Upload to TestPyPI
6. Upload to PyPI
7. Tag release in git 