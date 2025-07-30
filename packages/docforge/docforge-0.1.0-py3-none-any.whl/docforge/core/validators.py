# docforge/core/validators.py - Unified validation system (no circular imports)
"""
Comprehensive validation system with smart features - unified to avoid circular imports
"""

import os
import re
import shutil
import mimetypes
import time
from pathlib import Path
from typing import Union, List, Optional, Tuple, Dict, Any
from functools import wraps
from typing import Union, List, Optional, Tuple, Dict, Any

from .exceptions import (
    ValidationError, FileNotFoundError, InvalidFileFormatError,
    PermissionError, DiskSpaceError, PDFCorruptedError, DocForgeException, ProcessingResult
)


class FileValidator:
    """Validator for file operations."""

    @staticmethod
    def validate_input_file(file_path: Union[str, Path],
                            expected_extensions: Optional[List[str]] = None) -> Path:
        """Validate input file exists and has correct format."""
        """
        Validate input file exists and has correct format.

        Args:
            file_path: Path to the input file
            expected_extensions: List of valid file extensions (e.g., ['.pdf', '.PDF'])

        Returns:
            Path object of validated file

        Raises:
            FileNotFoundError: If file doesn't exist
            InvalidFileFormatError: If file has wrong extension
        """
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(str(path))

        # Check if it's a file (not directory)
        if not path.is_file():
            raise ValidationError(
                'input_file',
                str(path),
                'a file (not a directory)',
                [f"'{path}' is a directory, not a file",
                 "Provide the path to a specific file"]
            )

        # Check file extension if specified
        if expected_extensions:
            if path.suffix.lower() not in [ext.lower() for ext in expected_extensions]:
                raise InvalidFileFormatError(
                    str(path),
                    f"one of {expected_extensions}",
                    path.suffix
                )

        return path

    @staticmethod
    def validate_output_path(output_path: Union[str, Path],
                             create_dirs: bool = True) -> Path:
        """Validate output path and create directories if needed."""
        """
        Validate output path and create directories if needed.

        Args:
            output_path: Path for output file
            create_dirs: Whether to create parent directories

        Returns:
            Path object of validated output path

        Raises:
            PermissionError: If cannot write to output location
        """
        path = Path(output_path)

        # Create parent directories if they don't exist
        if create_dirs and not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise PermissionError(str(path.parent), "create directory")

        # Check if parent directory exists and is writable
        if not path.parent.exists():
            raise FileNotFoundError(str(path.parent))

        if not os.access(path.parent, os.W_OK):
            raise PermissionError(str(path.parent), "write")

        return path

    @staticmethod
    def validate_directory(dir_path: Union[str, Path],
                           must_exist: bool = True,
                           must_be_readable: bool = True) -> Path:
        """Validate directory path."""
        """
        Validate directory path.

        Args:
            dir_path: Path to directory
            must_exist: Whether directory must already exist
            must_be_readable: Whether directory must be readable

        Returns:
            Path object of validated directory

        Raises:
            FileNotFoundError: If directory doesn't exist when required
            PermissionError: If directory not accessible
        """
        path = Path(dir_path)

        if must_exist and not path.exists():
            raise FileNotFoundError(str(path))

        if path.exists() and not path.is_dir():
            raise ValidationError(
                'directory_path',
                str(path),
                'a directory (not a file)',
                [f"'{path}' is a file, not a directory",
                 "Provide the path to a directory"]
            )

        if must_be_readable and path.exists() and not os.access(path, os.R_OK):
            raise PermissionError(str(path), "read")

        return path


class ParameterValidator:
    """Validator for command parameters."""

    @staticmethod
    def validate_language_code(language: str) -> str:
        """
        Validate OCR language code.

        Args:
            language: Language code (e.g., 'eng', 'fra', 'deu')

        Returns:
            Validated language code

        Raises:
            ValidationError: If language code is invalid
        """
        # Common language codes
        valid_languages = {
            'eng': 'English',
            'fra': 'French',
            'deu': 'German',
            'spa': 'Spanish',
            'ita': 'Italian',
            'por': 'Portuguese',
            'rus': 'Russian',
            'chi_sim': 'Chinese Simplified',
            'chi_tra': 'Chinese Traditional',
            'jpn': 'Japanese',
            'kor': 'Korean'
        }

        if language not in valid_languages:
            raise ValidationError(
                'language',
                language,
                f"one of {list(valid_languages.keys())}",
                [f"Available languages: {', '.join(valid_languages.keys())}",
                 "Use 'eng' for English (most common)",
                 "Check Tesseract documentation for more language codes"]
            )

        return language

    @staticmethod
    def validate_optimization_type(opt_type: str) -> str:
        """
        Validate optimization type.

        Args:
            opt_type: Optimization type

        Returns:
            Validated optimization type

        Raises:
            ValidationError: If optimization type is invalid
        """
        valid_types = ['standard', 'aggressive', 'scanned', 'scale_only', 'high_quality']

        if opt_type not in valid_types:
            raise ValidationError(
                'optimization_type',
                opt_type,
                f"one of {valid_types}",
                [f"Available types: {', '.join(valid_types)}",
                 "Use 'standard' for balanced quality/size",
                 "Use 'aggressive' for maximum compression"]
            )

        return opt_type

    @staticmethod
    def validate_page_range(page_range: str) -> List[Tuple[int, int]]:
        """
        Validate and parse page range string.

        Args:
            page_range: Page range string (e.g., "1-5,10-15,20")

        Returns:
            List of (start, end) tuples

        Raises:
            ValidationError: If page range format is invalid
        """
        if not page_range.strip():
            raise ValidationError(
                'page_range',
                page_range,
                'non-empty page range (e.g., "1-5,10-15")',
                ['Provide a page range like "1-5" or "1-5,10-15"',
                 'Use single numbers for individual pages',
                 'Use ranges like "1-5" for page ranges']
            )

        try:
            ranges = []
            for part in page_range.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = part.split('-', 1)
                    start, end = int(start.strip()), int(end.strip())
                    if start > end:
                        raise ValidationError(
                            'page_range',
                            page_range,
                            'start page ≤ end page',
                            [f"In range '{part}', start page ({start}) is greater than end page ({end})",
                             'Use format "start-end" where start ≤ end']
                        )
                    ranges.append((start, end))
                else:
                    page = int(part)
                    ranges.append((page, page))

            return ranges

        except ValueError as e:
            raise ValidationError(
                'page_range',
                page_range,
                'valid page range format (e.g., "1-5,10-15")',
                ['Use numbers only in page ranges',
                 'Separate ranges with commas',
                 'Use hyphens for ranges: "1-5"',
                 'Example: "1-5,10-15,20"']
            )

    @staticmethod
    def validate_quality(quality: int) -> int:
        """
        Validate image quality parameter.

        Args:
            quality: Quality value (1-100)

        Returns:
            Validated quality value

        Raises:
            ValidationError: If quality is out of range
        """
        if not (1 <= quality <= 100):
            raise ValidationError(
                'quality',
                quality,
                'integer between 1 and 100',
                ['Quality must be between 1 (lowest) and 100 (highest)',
                 'Use 85 for good balance of quality and size',
                 'Use 95+ for high quality, 60- for small file size']
            )

        return quality


class SmartFileValidator(FileValidator):
    """Enhanced file validator with smart content checking and suggestions."""

    @staticmethod
    def validate_pdf_content(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Validate PDF file content and extract metadata."""
        """
        Validate PDF file content and extract metadata.

        Returns:
            Dict with PDF metadata and validation info

        Raises:
            PDFCorruptedError: If PDF is corrupted or invalid
            DependencyError: If PDF processing libraries are missing
        """
        path = Path(file_path)

        try:
            # Try to import PDF libraries
            try:
                import PyPDF2
                import fitz  # PyMuPDF
            except ImportError as e:
                from .exceptions import DependencyError
                raise DependencyError(
                    dependency="PyPDF2 and PyMuPDF",
                    operation="PDF validation",
                    install_command="pip install PyPDF2 PyMuPDF"
                )

            metadata = {
                'file_size': path.stat().st_size,
                'is_valid': False,
                'page_count': 0,
                'has_text': False,
                'has_images': False,
                'is_encrypted': False,
                'creation_date': None,
                'title': None,
                'author': None,
                'estimated_ocr_time': 0,
                'estimated_optimization_savings': 0
            }

            # Basic PDF structure validation with PyPDF2
            try:
                with open(path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)

                    metadata['page_count'] = len(pdf_reader.pages)
                    metadata['is_encrypted'] = pdf_reader.is_encrypted

                    # Extract basic metadata
                    if pdf_reader.metadata:
                        metadata['title'] = pdf_reader.metadata.get('/Title', '')
                        metadata['author'] = pdf_reader.metadata.get('/Author', '')
                        metadata['creation_date'] = pdf_reader.metadata.get('/CreationDate', '')

                    # Check if PDF has extractable text
                    text_found = False
                    for i, page in enumerate(pdf_reader.pages[:3]):  # Check first 3 pages
                        try:
                            text = page.extract_text()
                            if text and text.strip():
                                text_found = True
                                break
                        except:
                            continue

                    metadata['has_text'] = text_found
                    metadata['is_valid'] = True

            except Exception as e:
                # Try with PyMuPDF as fallback
                try:
                    doc = fitz.open(path)
                    metadata['page_count'] = doc.page_count
                    metadata['is_encrypted'] = doc.needs_pass

                    # Check for text and images
                    if doc.page_count > 0:
                        page = doc[0]
                        text = page.get_text()
                        metadata['has_text'] = bool(text.strip())

                        # Check for images
                        image_list = page.get_images()
                        metadata['has_images'] = len(image_list) > 0

                    metadata['is_valid'] = True
                    doc.close()

                except Exception as e2:
                    raise PDFCorruptedError(str(path), f"Cannot open PDF: {str(e2)}")

            # Estimate processing times
            metadata['estimated_ocr_time'] = SmartFileValidator._estimate_ocr_time(metadata)
            metadata['estimated_optimization_savings'] = SmartFileValidator._estimate_optimization_savings(metadata)

            return metadata

        except Exception as e:
            if isinstance(e, (PDFCorruptedError, DocForgeException)):
                raise
            raise PDFCorruptedError(str(path), f"PDF validation failed: {str(e)}")

    @staticmethod
    def _estimate_ocr_time(metadata: Dict[str, Any]) -> float:
        """Estimate OCR processing time in seconds."""
        base_time_per_page = 2.0  # Base time per page in seconds

        # Adjust based on file size (larger files usually have higher resolution images)
        size_factor = min(metadata['file_size'] / (1024 * 1024), 10)  # Max 10x factor for very large files

        # Adjust based on whether it already has text
        text_factor = 0.3 if metadata['has_text'] else 1.0

        estimated_time = metadata['page_count'] * base_time_per_page * size_factor * text_factor
        return max(estimated_time, 1.0)  # Minimum 1 second

    @staticmethod
    def _estimate_optimization_savings(metadata: Dict[str, Any]) -> float:
        """Estimate potential file size savings from optimization (0-1)."""
        if metadata['file_size'] < 1024 * 1024:  # Less than 1MB
            return 0.1
        elif metadata['has_images']:
            return 0.4  # Images can be compressed significantly
        elif metadata['file_size'] > 10 * 1024 * 1024:  # Greater than 10MB
            return 0.6  # Large files often have optimization potential
        else:
            return 0.2

    @staticmethod
    def validate_disk_space(output_path: Union[str, Path], required_space: int = None,
                            operation: str = "processing") -> bool:
        """
        Validate sufficient disk space is available.

        Args:
            output_path: Path where output will be written
            required_space: Required space in bytes (estimated if None)
            operation: Operation description for error messages

        Returns:
            True if sufficient space available

        Raises:
            DiskSpaceError: If insufficient disk space
        """
        output_path = Path(output_path)

        # Get parent directory for disk space check
        check_path = output_path.parent if output_path.parent.exists() else output_path

        try:
            # Get available disk space
            total, used, free = shutil.disk_usage(check_path)

            # Estimate required space if not provided
            if required_space is None:
                required_space = 100 * 1024 * 1024  # Default 100MB

            # Add 50MB buffer for safety
            required_with_buffer = required_space + (50 * 1024 * 1024)

            if free < required_with_buffer:
                raise DiskSpaceError(
                    required_space=required_with_buffer,
                    available_space=free,
                    output_path=str(output_path)
                )

            return True

        except Exception as e:
            if isinstance(e, DiskSpaceError):
                raise
            # If we can't check disk space, assume it's fine but warn
            return True

    @staticmethod
    def suggest_similar_files(file_path: str,
                              extensions: Optional[List[str]] = None) -> List[str]:
        """Suggest similar files when specified file is not found."""
        """
        Suggest similar files when the specified file is not found.

        Args:
            file_path: The file that wasn't found
            extensions: Valid extensions to look for

        Returns:
            List of similar file paths
        """
        if extensions is None:
            extensions = ['.pdf', '.PDF']

        directory = os.path.dirname(file_path) or "."
        filename = os.path.basename(file_path)

        if not os.path.exists(directory):
            return []

        suggestions = []
        filename_lower = filename.lower()
        filename_no_ext = os.path.splitext(filename_lower)[0]

        try:
            for file in os.listdir(directory):
                file_lower = file.lower()
                file_no_ext = os.path.splitext(file_lower)[0]

                # Check if it has a valid extension
                if not any(file.endswith(ext) for ext in extensions):
                    continue

                # Exact match (different case)
                if file_lower == filename_lower:
                    suggestions.insert(0, os.path.join(directory, file))
                    continue

                # Filename without extension matches
                if file_no_ext == filename_no_ext:
                    suggestions.insert(0, os.path.join(directory, file))
                    continue

                # Partial matches
                if (filename_no_ext in file_no_ext or
                        file_no_ext in filename_no_ext or
                        SmartFileValidator._strings_similar(filename_no_ext, file_no_ext)):
                    suggestions.append(os.path.join(directory, file))

            return suggestions[:5]  # Return top 5 suggestions

        except PermissionError:
            return []

    @staticmethod
    def _strings_similar(s1: str, s2: str, threshold: float = 0.6) -> bool:
        """Check if two strings are similar using simple similarity metric."""
        if not s1 or not s2:
            return False

        # Simple character-based similarity
        set1, set2 = set(s1), set(s2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return (intersection / union) >= threshold if union > 0 else False


class SmartParameterValidator(ParameterValidator):
    """Enhanced parameter validator with smart suggestions and auto-correction."""

    @staticmethod
    def validate_and_suggest_language(language: str) -> Tuple[str, List[str]]:
        """
        Validate language code and provide suggestions if invalid.

        Returns:
            Tuple of (validated_language, suggestions)
        """
        # Extended language mapping
        language_map = {
            'eng': 'English',
            'fra': 'French',
            'fre': 'French',  # Alternative code
            'deu': 'German',
            'ger': 'German',  # Alternative code
            'spa': 'Spanish',
            'ita': 'Italian',
            'por': 'Portuguese',
            'rus': 'Russian',
            'chi_sim': 'Chinese Simplified',
            'chs': 'Chinese Simplified',  # Alternative
            'chi_tra': 'Chinese Traditional',
            'cht': 'Chinese Traditional',  # Alternative
            'jpn': 'Japanese',
            'kor': 'Korean',
            'ara': 'Arabic',
            'hin': 'Hindi',
            'tha': 'Thai',
            'vie': 'Vietnamese'
        }

        # Normalize input
        lang_lower = language.lower().strip()

        # Direct match
        if lang_lower in language_map:
            return lang_lower, []

        # Find suggestions for typos or partial matches
        suggestions = []

        # Check for common typos
        typo_corrections = {
            'en': 'eng',
            'english': 'eng',
            'fr': 'fra',
            'french': 'fra',
            'de': 'deu',
            'german': 'deu',
            'es': 'spa',
            'spanish': 'spa',
            'it': 'ita',
            'italian': 'ita',
            'pt': 'por',
            'portuguese': 'por',
            'ru': 'rus',
            'russian': 'rus',
            'zh': 'chi_sim',
            'chinese': 'chi_sim',
            'ja': 'jpn',
            'japanese': 'jpn',
            'ko': 'kor',
            'korean': 'kor'
        }

        if lang_lower in typo_corrections:
            corrected = typo_corrections[lang_lower]
            suggestions.append(f"Did you mean '{corrected}' ({language_map[corrected]})?")
            return corrected, suggestions

        # Find partial matches
        for code, name in language_map.items():
            if (lang_lower in code or
                    lang_lower in name.lower() or
                    code in lang_lower or
                    name.lower().startswith(lang_lower)):
                suggestions.append(f"'{code}' for {name}")

        # If no suggestions found, provide common ones
        if not suggestions:
            suggestions = [
                "'eng' for English (most common)",
                "'fra' for French",
                "'deu' for German",
                "'spa' for Spanish"
            ]

        raise ValidationError(
            'language',
            language,
            f"valid language code (e.g., {', '.join(list(language_map.keys())[:5])})",
            suggestions
        )

    @staticmethod
    def validate_page_range_for_pdf(page_range: str, pdf_page_count: int) -> List[Tuple[int, int]]:
        """
        Validate page range against actual PDF page count.

        Args:
            page_range: Page range string (e.g., "1-5,10-15")
            pdf_page_count: Actual number of pages in PDF

        Returns:
            List of validated (start, end) tuples

        Raises:
            ValidationError: If page ranges are invalid for the PDF
        """
        # First validate basic format
        ranges = ParameterValidator.validate_page_range(page_range)

        # Then validate against PDF page count
        validated_ranges = []
        invalid_ranges = []

        for start, end in ranges:
            if start > pdf_page_count or end > pdf_page_count:
                invalid_ranges.append(f"{start}-{end}")
            elif start < 1:
                invalid_ranges.append(f"{start}-{end}")
            else:
                validated_ranges.append((start, end))

        if invalid_ranges:
            suggestions = [
                f"PDF has {pdf_page_count} pages",
                f"Valid page numbers: 1-{pdf_page_count}",
                "Use page numbers within the PDF's page count",
                "Example valid ranges: '1-5', '10-15', '20'"
            ]

            raise ValidationError(
                'page_range',
                page_range,
                f"page ranges within 1-{pdf_page_count}",
                suggestions
            )

        return validated_ranges


def safe_execute(operation_func, *args, **kwargs) -> ProcessingResult:
    """
    Safely execute an operation with comprehensive error handling.

    Args:
        operation_func: Function to execute
        *args, **kwargs: Arguments for the function

    Returns:
        ProcessingResult with success/error information
    """
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
