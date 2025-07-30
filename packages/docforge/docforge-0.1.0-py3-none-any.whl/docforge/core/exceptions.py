# docforge/core/exceptions.py
"""
Comprehensive error handling system for DocForge
Custom exceptions with rich context and actionable messages
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import os
from typing import Optional, List, Dict, Any, Union

# ✨ ADD TYPE ALIASES HERE (module level)
FilePath = Union[str, Path]
OptionalStr = Optional[str]
OptionalDict = Optional[Dict[str, Any]]
ResultDict = Dict[str, Any]
FileList = List[str]


class DocForgeException(Exception):
    """Base exception for all DocForge operations."""

    def __init__(self,
                 message: str,
                 error_code: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None) -> None:
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.suggestions = suggestions or []
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for structured handling."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'suggestions': self.suggestions
        }


class FileNotFoundError(DocForgeException):
    """Raised when input file cannot be found."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        message = f"File not found: {file_path}"

        suggestions = [
            f"Check if the file path is correct: {file_path}",
            "Ensure the file exists and is accessible",
            "Check file permissions",
            "Try using an absolute path instead of relative path"
        ]

        context = {
            'file_path': file_path,
            'file_exists': os.path.exists(file_path),
            'parent_exists': os.path.exists(os.path.dirname(file_path)) if os.path.dirname(file_path) else True,
            'current_directory': os.getcwd()
        }

        super().__init__(message, 'FILE_NOT_FOUND', context, suggestions)


class InvalidFileFormatError(DocForgeException):
    """Raised when file format is not supported."""

    def __init__(self, file_path: str, expected_format: str, actual_format: Optional[str] = None):
        self.file_path = file_path
        self.expected_format = expected_format
        self.actual_format = actual_format

        if actual_format:
            message = f"Invalid file format: expected {expected_format}, got {actual_format}"
        else:
            message = f"Invalid file format: expected {expected_format}"

        suggestions = [
            f"Ensure the file is a valid {expected_format} file",
            "Check if the file is corrupted",
            f"Convert the file to {expected_format} format first",
            "Verify the file extension matches the content"
        ]

        context = {
            'file_path': file_path,
            'expected_format': expected_format,
            'actual_format': actual_format,
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }

        super().__init__(message, 'INVALID_FORMAT', context, suggestions)


class PermissionError(DocForgeException):
    """Raised when file permission issues occur."""

    def __init__(self, file_path: str, operation: str = "access"):
        self.file_path = file_path
        self.operation = operation

        message = f"Permission denied: cannot {operation} {file_path}"

        suggestions = [
            "Check file permissions and ownership",
            "Run DocForge with appropriate privileges",
            "Ensure the file is not locked by another application",
            "Try copying the file to a writable location"
        ]

        context = {
            'file_path': file_path,
            'operation': operation,
            'file_exists': os.path.exists(file_path)
        }

        super().__init__(message, 'PERMISSION_DENIED', context, suggestions)


class DiskSpaceError(DocForgeException):
    """Raised when insufficient disk space is available."""

    def __init__(self, required_space: int, available_space: int, output_path: str):
        self.required_space = required_space
        self.available_space = available_space
        self.output_path = output_path

        message = f"Insufficient disk space: need {self._format_bytes(required_space)}, have {self._format_bytes(available_space)}"

        suggestions = [
            "Free up disk space on the target drive",
            "Choose a different output location with more space",
            "Use a more aggressive compression option",
            "Split the operation into smaller chunks"
        ]

        context = {
            'required_space_bytes': required_space,
            'available_space_bytes': available_space,
            'output_path': output_path,
            'required_space_formatted': self._format_bytes(required_space),
            'available_space_formatted': self._format_bytes(available_space)
        }

        super().__init__(message, 'INSUFFICIENT_DISK_SPACE', context, suggestions)

    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """Format bytes in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"


class OCRError(DocForgeException):
    """Raised when OCR processing fails."""

    def __init__(self, file_path: str, details: Optional[str] = None):
        self.file_path = file_path
        self.details = details

        message = f"OCR processing failed for {file_path}"
        if details:
            message += f": {details}"

        suggestions = [
            "Check if the PDF contains scannable text/images",
            "Try a different OCR language setting",
            "Ensure Tesseract is properly installed",
            "Check if the PDF is password-protected",
            "Try using a different layout mode (standard, precise, text_only)"
        ]

        context = {
            'file_path': file_path,
            'details': details,
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }

        super().__init__(message, 'OCR_FAILED', context, suggestions)


class PDFCorruptedError(DocForgeException):
    """Raised when PDF file is corrupted or malformed."""

    def __init__(self, file_path: str, details: Optional[str] = None):
        self.file_path = file_path
        self.details = details

        message = f"PDF file appears to be corrupted: {file_path}"
        if details:
            message += f" ({details})"

        suggestions = [
            "Try opening the PDF in a PDF viewer to verify it's valid",
            "Re-download or re-create the PDF file",
            "Try using a PDF repair tool",
            "Use a different PDF file for testing"
        ]

        context = {
            'file_path': file_path,
            'details': details,
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }

        super().__init__(message, 'PDF_CORRUPTED', context, suggestions)


class DependencyError(DocForgeException):
    """Raised when required dependencies are missing."""

    def __init__(self, dependency: str, operation: str, install_command: Optional[str] = None):
        self.dependency = dependency
        self.operation = operation
        self.install_command = install_command

        message = f"Missing dependency '{dependency}' required for {operation}"

        suggestions = []
        if install_command:
            suggestions.append(f"Install {dependency}: {install_command}")
        suggestions.extend([
            "Check the installation guide in the documentation",
            "Verify your system meets the requirements",
            "Try reinstalling DocForge dependencies"
        ])

        context = {
            'dependency': dependency,
            'operation': operation,
            'install_command': install_command
        }

        super().__init__(message, 'MISSING_DEPENDENCY', context, suggestions)


class ValidationError(DocForgeException):
    """Raised when input validation fails."""

    def __init__(self,
                 field: str,
                 value: Any,
                 expected: str,
                 suggestions: Optional[List[str]] = None) -> None:
        self.field = field
        self.value = value
        self.expected = expected

        message = f"Validation failed for {field}: expected {expected}, got {repr(value)}"

        if not suggestions:
            suggestions = [
                f"Provide a valid value for {field}",
                f"Expected format: {expected}",
                "Check the documentation for valid values"
            ]

        context = {
            'field': field,
            'value': value,
            'expected': expected
        }

        super().__init__(message, 'VALIDATION_ERROR', context, suggestions)


@dataclass
class ProcessingResult:
    """Structured result object for DocForge operations."""

    success: bool
    message: str
    operation: str
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    error: Optional[DocForgeException] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        result = {
            'success': self.success,
            'message': self.message,
            'operation': self.operation,
            'input_file': self.input_file,
            'output_file': self.output_file,
            'processing_time': self.processing_time,
            'metadata': self.metadata,
            'warnings': self.warnings
        }

        if self.error:
            result['error'] = self.error.to_dict()

        return result

    @classmethod
    def success_result(cls, message: str, operation: str, **kwargs) -> 'ProcessingResult':
        """Create a successful result."""
        return cls(success=True, message=message, operation=operation, **kwargs)

    @classmethod
    def error_result(cls, error: DocForgeException, operation: str, **kwargs) -> 'ProcessingResult':
        """Create an error result."""
        return cls(
            success=False,
            message=error.message,
            operation=operation,
            error=error,
            **kwargs
        )

    @classmethod
    def warning_result(cls, message: str, operation: str, warnings: List[str], **kwargs) -> 'ProcessingResult':
        """Create a result with warnings."""
        return cls(
            success=True,
            message=message,
            operation=operation,
            warnings=warnings,
            **kwargs
        )


def safe_execute(operation_func: callable, *args: Any, **kwargs: Any) -> 'ProcessingResult':
    """
    Safely execute an operation with comprehensive error handling.

    Args:
        operation_func: Function to execute
        *args, **kwargs: Arguments for the function

    Returns:
        ProcessingResult with success/error information
    """
    import time
    from functools import wraps

    start_time = time.time()
    operation_name = kwargs.pop('_operation_name', operation_func.__name__)

    try:
        result = operation_func(*args, **kwargs)
        processing_time = time.time() - start_time

        if isinstance(result, ProcessingResult):
            result.processing_time = processing_time
            return result
        else:
            # Handle legacy return values
            return ProcessingResult.success_result(
                message=f"{operation_name} completed successfully",
                operation=operation_name,
                processing_time=processing_time,
                metadata=result if isinstance(result, dict) else {}
            )

    except DocForgeException as e:
        processing_time = time.time() - start_time
        return ProcessingResult.error_result(
            error=e,
            operation=operation_name,
            processing_time=processing_time
        )
    except Exception as e:
        processing_time = time.time() - start_time
        # Wrap unexpected exceptions
        wrapped_error = DocForgeException(
            message=f"Unexpected error in {operation_name}: {str(e)}",
            error_code='UNEXPECTED_ERROR',
            context={'original_error': str(e), 'error_type': type(e).__name__},
            suggestions=[
                'This is an unexpected error - please report it',
                'Try the operation again',
                'Check if your input file is valid',
                'Contact support if the problem persists'
            ]
        )

        return ProcessingResult.error_result(
            error=wrapped_error,
            operation=operation_name,
            processing_time=processing_time
        )


class DocForgeError(Exception):
    """Base exception for DocForge errors."""
    pass


class PDFProcessingError(DocForgeError):
    """Exception raised during PDF processing."""
    pass


class OCRProcessingError(DocForgeError):
    """Exception raised during OCR processing."""
    pass


class OptimizationError(DocForgeError):
    """Exception raised during optimization."""
    pass


# AT THE VERY END:
DocForgeError = DocForgeException
