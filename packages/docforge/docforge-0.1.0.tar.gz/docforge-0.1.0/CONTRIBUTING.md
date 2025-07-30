# Contributing to DocForge

Thank you for your interest in contributing to DocForge! This guide will help you get started.

## 🚀 Quick Start for Contributors

### Development Setup
```bash
git clone https://github.com/oscar2song/docforge.git
cd docforge
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-test.txt
Testing Your Changes
bash# Run the full test suite (must pass 47/47 tests)
pytest tests/ -v

# Test specific components
pytest tests/test_rich_interface.py -v
pytest tests/test_exceptions.py -v

# Test the Rich CLI interface
docforge test-validation
docforge test-errors
🎯 Contribution Guidelines
Code Quality Standards

✅ All tests must pass (47/47)
✅ Type hints required for new code
✅ Rich CLI integration for user-facing features
✅ Comprehensive error handling with suggestions
✅ Smart input validation

Pull Request Process

Fork the repository
Create a descriptive branch name
Add tests for new functionality
Ensure all existing tests pass
Update documentation if needed
Submit PR with clear description

🏗️ Architecture Guidelines
Follow the established patterns:

Rich UI: Use DocForgeUI for user interaction
Error Handling: Extend DocForgeException classes
Validation: Use SmartValidator classes
Testing: Add comprehensive test coverage

🤝 Code of Conduct
Be respectful, inclusive, and collaborative.
