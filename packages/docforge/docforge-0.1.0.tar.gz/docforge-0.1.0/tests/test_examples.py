# tests/test_examples.py - Example test patterns
"""
Example test patterns and common testing scenarios for DocForge
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from docforge.core.exceptions import DocForgeException, ProcessingResult
from docforge.cli.interface import CLIInterface


class TestExamplePatterns:
    """Example test patterns for common DocForge scenarios."""

    def test_mock_file_operations(self, temp_dir):
        """Example: Testing file operations with temporary files."""
        # Create test files
        test_file = temp_dir / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4\ntest\n%%EOF")

        # Test file exists
        assert test_file.exists()
        assert test_file.stat().st_size > 0

    @patch('docforge.cli.interface.DocumentProcessor')  # Fixed path
    def test_mock_processor(self, mock_processor_class):
        """Example: Mocking the DocumentProcessor."""
        # Setup mock
        mock_processor = Mock()
        mock_processor.ocr_pdf.return_value = {
            'success': True,
            'message': 'OCR completed',
            'pages_processed': 5
        }
        mock_processor_class.return_value = mock_processor

        # Use in CLI
        cli = CLIInterface(use_rich=False)

        # Verify mock is used (updated assertion)
        mock_processor_class.assert_called_once()

    def test_exception_handling_pattern(self):
        """Example: Testing exception handling patterns."""

        def function_that_raises():
            raise DocForgeException("Test error", error_code="TEST")

        # Test exception is raised
        with pytest.raises(DocForgeException) as exc_info:
            function_that_raises()

        # Verify exception details
        assert exc_info.value.error_code == "TEST"
        assert "Test error" in str(exc_info.value)

    def test_processing_result_patterns(self):
        """Example: Testing ProcessingResult patterns."""

        # Test successful result
        success_result = ProcessingResult.success_result(
            "Operation completed",
            "test_operation",
            input_file="input.pdf",
            output_file="output.pdf",
            processing_time=1.5,
            metadata={"pages": 10}
        )

        assert success_result.success is True
        assert success_result.processing_time == 1.5
        assert success_result.metadata["pages"] == 10

        # Test error result
        error = DocForgeException("Test failed")
        error_result = ProcessingResult.error_result(error, "test_operation")

        assert error_result.success is False
        assert error_result.error == error

    @pytest.mark.parametrize("language,expected", [
        ("en", "eng"),
        ("english", "eng"),
        ("fr", "fra"),
        ("french", "fra"),
        ("de", "deu"),
        ("german", "deu"),
    ])
    def test_parametrized_language_correction(self, language, expected):
        """Example: Parametrized testing for language auto-correction."""
        from docforge.core.validators import SmartParameterValidator

        result, suggestions = SmartParameterValidator.validate_and_suggest_language(language)
        assert result == expected

    def test_cli_argument_parsing_pattern(self):
        """Example: Testing CLI argument patterns."""
        import argparse

        # Mock args object
        args = argparse.Namespace()
        args.input = "test.pdf"
        args.output = "output.pdf"
        args.language = "eng"
        args.command = "ocr"

        # Test args
        assert args.input == "test.pdf"
        assert args.language == "eng"

    def test_rich_ui_pattern(self):
        """Example: Testing Rich UI without actual console output."""
        from docforge.cli.rich_interface import DocForgeUI

        ui = DocForgeUI()

        # Test methods don't raise exceptions
        try:
            ui.print_success("Test message")
            ui.print_error("Test error")
            ui.print_warning("Test warning")
            ui.print_info("Test info")
        except Exception as e:
            pytest.fail(f"UI methods should not raise: {e}")
