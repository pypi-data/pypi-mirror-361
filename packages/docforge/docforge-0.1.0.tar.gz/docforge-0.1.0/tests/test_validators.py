# tests/test_validators.py - Test validation system
"""
Test the enhanced validation system
"""

import pytest
from docforge.core.validators import (
    FileValidator, ParameterValidator, SmartFileValidator, SmartParameterValidator
)
from docforge.core.exceptions import ValidationError, FileNotFoundError
from docforge.core.exceptions import InvalidFileFormatError


class TestFileValidator:
    """Test basic file validation."""

    def test_validate_existing_file(self, sample_pdf_path):
        """Test validating an existing file."""
        result = FileValidator.validate_input_file(sample_pdf_path, ['.pdf'])
        assert result == sample_pdf_path

    def test_validate_nonexistent_file(self, nonexistent_pdf_path):
        """Test validating a nonexistent file."""
        with pytest.raises(FileNotFoundError):
            FileValidator.validate_input_file(nonexistent_pdf_path)

    def test_validate_wrong_extension(self, temp_dir):
        """Test validating file with wrong extension."""
        txt_file = temp_dir / "document.txt"
        txt_file.write_text("test content")

        with pytest.raises(InvalidFileFormatError):
            FileValidator.validate_input_file(txt_file, ['.pdf'])

    def test_validate_output_path(self, temp_dir):
        """Test validating output path."""
        output_path = temp_dir / "output.pdf"
        result = FileValidator.validate_output_path(output_path)
        assert result == output_path


class TestParameterValidator:
    """Test parameter validation."""

    def test_valid_language_code(self):
        """Test validating valid language codes."""
        assert ParameterValidator.validate_language_code('eng') == 'eng'
        assert ParameterValidator.validate_language_code('fra') == 'fra'

    def test_invalid_language_code(self):
        """Test validating invalid language code."""
        with pytest.raises(ValidationError) as exc_info:
            ParameterValidator.validate_language_code('xyz')

        assert exc_info.value.field == 'language'
        assert len(exc_info.value.suggestions) > 0

    def test_valid_quality(self):
        """Test validating valid quality values."""
        assert ParameterValidator.validate_quality(85) == 85
        assert ParameterValidator.validate_quality(1) == 1
        assert ParameterValidator.validate_quality(100) == 100

    def test_invalid_quality(self):
        """Test validating invalid quality values."""
        with pytest.raises(ValidationError):
            ParameterValidator.validate_quality(150)

        with pytest.raises(ValidationError):
            ParameterValidator.validate_quality(0)

    def test_page_range_validation(self):
        """Test page range validation."""
        # Valid ranges
        ranges = ParameterValidator.validate_page_range("1-5,10-15,20")
        expected = [(1, 5), (10, 15), (20, 20)]
        assert ranges == expected

        # Invalid range
        with pytest.raises(ValidationError):
            ParameterValidator.validate_page_range("10-5")  # Start > end


class TestSmartParameterValidator:
    """Test smart parameter validation with auto-correction."""

    def test_language_auto_correction(self):
        """Test language auto-correction."""
        # Should auto-correct
        result, suggestions = SmartParameterValidator.validate_and_suggest_language("en")
        assert result == "eng"
        assert len(suggestions) > 0

        result, suggestions = SmartParameterValidator.validate_and_suggest_language("french")
        assert result == "fra"

        # Should accept valid codes
        result, suggestions = SmartParameterValidator.validate_and_suggest_language("eng")
        assert result == "eng"
        assert len(suggestions) == 0

    def test_invalid_language_with_suggestions(self):
        """Test invalid language provides suggestions."""
        with pytest.raises(ValidationError) as exc_info:
            SmartParameterValidator.validate_and_suggest_language("xyz")

        assert len(exc_info.value.suggestions) > 0
        assert any("eng" in s for s in exc_info.value.suggestions)
