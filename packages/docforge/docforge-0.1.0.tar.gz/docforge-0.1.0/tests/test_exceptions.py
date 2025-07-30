# tests/test_exceptions.py - Test error handling system
"""
Test the comprehensive error handling system
"""

import pytest
from docforge.core.exceptions import (
    DocForgeException, FileNotFoundError, InvalidFileFormatError,
    ValidationError, OCRError, ProcessingResult
)


class TestDocForgeException:
    """Test the base DocForge exception class."""

    def test_basic_exception_creation(self):
        """Test creating a basic exception."""
        exc = DocForgeException("Test error")
        assert exc.message == "Test error"
        assert exc.error_code == "DocForgeException"
        assert exc.context == {}
        assert exc.suggestions == []

    def test_exception_with_context(self):
        """Test exception with context and suggestions."""
        context = {"file_path": "/test/path"}
        suggestions = ["Try again", "Check file"]

        exc = DocForgeException(
            "Test error",
            error_code="TEST_ERROR",
            context=context,
            suggestions=suggestions
        )

        assert exc.error_code == "TEST_ERROR"
        assert exc.context == context
        assert exc.suggestions == suggestions

    def test_exception_to_dict(self):
        """Test converting exception to dictionary."""
        exc = DocForgeException("Test error", error_code="TEST")
        result = exc.to_dict()

        assert result['error_type'] == 'DocForgeException'
        assert result['error_code'] == 'TEST'
        assert result['message'] == 'Test error'
        assert 'context' in result
        assert 'suggestions' in result


class TestFileNotFoundError:
    """Test file not found error handling."""

    def test_file_not_found_error_creation(self):
        """Test creating file not found error."""
        exc = FileNotFoundError("/nonexistent/file.pdf")

        assert "File not found" in exc.message
        assert exc.file_path == "/nonexistent/file.pdf"
        assert exc.error_code == "FILE_NOT_FOUND"
        assert len(exc.suggestions) > 0
        assert any("Check if the file path is correct" in s for s in exc.suggestions)


class TestValidationError:
    """Test validation error handling."""

    def test_validation_error_creation(self):
        """Test creating validation error."""
        exc = ValidationError("quality", 150, "1-100")

        assert "Validation failed for quality" in exc.message
        assert exc.field == "quality"
        assert exc.value == 150
        assert exc.expected == "1-100"


class TestProcessingResult:
    """Test processing result objects."""

    def test_success_result_creation(self):
        """Test creating successful result."""
        result = ProcessingResult.success_result(
            "Operation completed",
            "test_operation",
            processing_time=1.5
        )

        assert result.success is True
        assert result.message == "Operation completed"
        assert result.operation == "test_operation"
        assert result.processing_time == 1.5
        assert result.error is None

    def test_error_result_creation(self):
        """Test creating error result."""
        exc = DocForgeException("Test error")
        result = ProcessingResult.error_result(exc, "test_operation")

        assert result.success is False
        assert result.error == exc
        assert result.operation == "test_operation"

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ProcessingResult.success_result("Test", "operation")
        result_dict = result.to_dict()

        assert result_dict['success'] is True
        assert result_dict['message'] == "Test"
        assert result_dict['operation'] == "operation"

