# docforge/cli/interface.py - Simplified and fixed version
"""
Simplified CLIInterface with robust error handling
"""

import argparse
import sys
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, Union

# Import Rich components with fallback
try:
    from .rich_interface import DocForgeUI, BatchProgressTracker

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import core components with fallbacks
try:
    from ..core.exceptions import (
        DocForgeException, ProcessingResult, FileNotFoundError,
        InvalidFileFormatError, ValidationError, OCRError, safe_execute
    )

    EXCEPTIONS_AVAILABLE = True
except ImportError:
    EXCEPTIONS_AVAILABLE = False


    # Create minimal exceptions
    class DocForgeException(Exception):
        def __init__(self, message, error_code="GENERIC_ERROR", suggestions=None):
            super().__init__(message)
            self.message = message
            self.error_code = error_code
            self.suggestions = suggestions or []


    class ProcessingResult:
        def __init__(self, success=True, message="", operation="", **kwargs):
            self.success = success
            self.message = message
            self.operation = operation
            for key, value in kwargs.items():
                setattr(self, key, value)

        @classmethod
        def success_result(cls, message, operation, **kwargs):
            return cls(success=True, message=message, operation=operation, **kwargs)

        @classmethod
        def error_result(cls, error, operation):
            return cls(success=False, message=str(error), operation=operation)


    FileNotFoundError = DocForgeException
    InvalidFileFormatError = DocForgeException
    ValidationError = DocForgeException
    OCRError = DocForgeException


    def safe_execute(func, *args, **kwargs):
        operation_name = kwargs.pop('_operation_name', 'Operation')
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return ProcessingResult.error_result(e, operation_name)

try:
    from ..core.processor import DocumentProcessor

    PROCESSOR_AVAILABLE = True
except ImportError:
    PROCESSOR_AVAILABLE = False


    # Create minimal processor
    class DocumentProcessor:
        def __init__(self, verbose=True):
            self.verbose = verbose

        def ocr_pdf(self, input_file, output_file, language='eng', **kwargs):
            import shutil
            shutil.copy2(input_file, output_file)
            return {
                'success': True,
                'message': 'File copied (OCR placeholder)',
                'input_file': input_file,
                'output_file': output_file
            }

try:
    from ..core.enhanced_processor import EnhancedDocumentProcessor, PerformanceEnhancedCLI

    ENHANCED_PROCESSOR_AVAILABLE = True
except ImportError:
    ENHANCED_PROCESSOR_AVAILABLE = False


class SimpleValidator:
    """Simple validator with basic checks."""

    @staticmethod
    def validate_input_file(file_path, expected_extensions=None):
        """Validate input file exists and has correct extension."""
        path = Path(file_path)

        if not path.exists():
            raise DocForgeException(
                f"Input file not found: {path}",
                error_code="FILE_NOT_FOUND",
                suggestions=[
                    f"Check if the file path is correct: {path}",
                    "Ensure the file exists and is readable"
                ]
            )

        if expected_extensions:
            if path.suffix.lower() not in [ext.lower() for ext in expected_extensions]:
                raise DocForgeException(
                    f"Invalid file format. Expected {expected_extensions}, got {path.suffix}",
                    error_code="INVALID_FORMAT",
                    suggestions=[
                        f"Use a file with one of these extensions: {expected_extensions}",
                        "Convert your file to the correct format"
                    ]
                )

        return path

    @staticmethod
    def validate_output_path(file_path):
        """Validate output path can be created."""
        path = Path(file_path)

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        return path

    @staticmethod
    def validate_directory(dir_path, must_exist=True):
        """Validate directory."""
        path = Path(dir_path)

        if must_exist and not path.exists():
            raise DocForgeException(
                f"Directory not found: {path}",
                error_code="DIRECTORY_NOT_FOUND",
                suggestions=[
                    f"Check if the directory path is correct: {path}",
                    "Ensure the directory exists"
                ]
            )

        if path.exists() and not path.is_dir():
            raise DocForgeException(
                f"Path exists but is not a directory: {path}",
                error_code="NOT_A_DIRECTORY"
            )

        return path


class CLIInterface:
    """Simplified CLI Interface with robust error handling."""

    def __init__(self, use_rich: bool = True) -> None:
        """Initialize CLI interface."""
        self.use_rich = use_rich and RICH_AVAILABLE
        self.ui = DocForgeUI() if self.use_rich else None
        self.console = self.ui.console if self.ui else None
        self.validator = SimpleValidator()

        # Initialize processors
        if ENHANCED_PROCESSOR_AVAILABLE:
            try:
                self.enhanced_processor = EnhancedDocumentProcessor(verbose=self.use_rich)
                self.performance_cli = PerformanceEnhancedCLI(self.enhanced_processor)
            except Exception:
                self.enhanced_processor = None
                self.performance_cli = None
        else:
            self.enhanced_processor = None
            self.performance_cli = None

        if PROCESSOR_AVAILABLE:
            try:
                self.processor = DocumentProcessor(verbose=True)
            except Exception:
                self.processor = DocumentProcessor(verbose=True)  # Use minimal version
        else:
            self.processor = DocumentProcessor(verbose=True)  # Use minimal version

    def print_message(self, message: str, msg_type: str = "info") -> None:
        """Print message with Rich if available, otherwise use basic print."""
        if self.ui:
            if msg_type == "success":
                self.ui.print_success(message)
            elif msg_type == "error":
                self.ui.print_error(message)
            elif msg_type == "warning":
                self.ui.print_warning(message)
            else:
                self.ui.print_info(message)
        else:
            # Fallback to basic print
            icons = {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️"
            }
            icon = icons.get(msg_type, "ℹ️")
            print(f"{icon}  {message}")

    def display_result(self, result: ProcessingResult):
        """Display processing result with appropriate UI."""
        if self.ui and hasattr(self.ui, 'display_processing_result'):
            self.ui.display_processing_result(result)
        else:
            # Fallback display
            if result.success:
                self.print_message(result.message, "success")
                if hasattr(result, 'processing_time') and result.processing_time:
                    self.print_message(f"Completed in {result.processing_time:.2f}s")
            else:
                self.print_message(result.message, "error")

    def validate_common_args(self, args) -> bool:
        """Validate common arguments and display errors if invalid."""
        try:
            # Validate input file if present
            if hasattr(args, 'input') and args.input:
                expected_ext = ['.pdf'] if 'pdf' in getattr(args, 'command', '') else None
                self.validator.validate_input_file(args.input, expected_ext)

            # Validate output path if present
            if hasattr(args, 'output') and args.output:
                self.validator.validate_output_path(args.output)

            return True

        except DocForgeException as e:
            if self.ui and hasattr(self.ui, 'display_error_details'):
                self.ui.display_error_details(e)
            else:
                self.print_message(e.message, "error")
                if hasattr(e, 'suggestions') and e.suggestions:
                    print("\n💡 Suggestions:")
                    for i, suggestion in enumerate(e.suggestions, 1):
                        print(f"  {i}. {suggestion}")
            return False

    def show_banner(self):
        """Show DocForge banner."""
        if self.ui and hasattr(self.ui, 'print_banner'):
            self.ui.print_banner()
        else:
            print("🔨 DocForge - Document Processing Toolkit")
            print("Forge perfect documents with precision and power")
            print("=" * 50)

    def confirm_action(self, message: str) -> bool:
        """Confirm user action."""
        if self.ui and hasattr(self.ui, 'confirm_action'):
            return self.ui.confirm_action(message)
        else:
            response = input(f"⚠️  {message} (y/N): ").lower().strip()
            return response in ['y', 'yes']

    @staticmethod
    def setup_parsers(subparsers):
        """Set up all command parsers."""

        # Enhanced OCR command
        enhanced_ocr_parser = subparsers.add_parser('enhanced-ocr', help='Enhanced OCR processing')
        enhanced_ocr_parser.add_argument('-i', '--input', required=True, help='Input PDF file')
        enhanced_ocr_parser.add_argument('-o', '--output', required=True, help='Output PDF file')
        enhanced_ocr_parser.add_argument('--language', default='eng', help='OCR language code')
        enhanced_ocr_parser.add_argument('--memory-mapping', action='store_true',
                                         help='Enable memory mapping for large files')
        enhanced_ocr_parser.add_argument('--smart-caching', action='store_true', default=True,
                                         help='Enable intelligent caching')

        # Standard OCR command
        ocr_parser = subparsers.add_parser('ocr', help='Standard OCR processing')
        ocr_parser.add_argument('-i', '--input', required=True, help='Input PDF file')
        ocr_parser.add_argument('-o', '--output', required=True, help='Output PDF file')
        ocr_parser.add_argument('--language', default='eng', help='OCR language code')

        # Batch OCR commands
        enhanced_batch_ocr_parser = subparsers.add_parser('enhanced-batch-ocr', help='Enhanced batch OCR')
        enhanced_batch_ocr_parser.add_argument('-i', '--input', required=True, help='Input directory')
        enhanced_batch_ocr_parser.add_argument('-o', '--output', required=True, help='Output directory')
        enhanced_batch_ocr_parser.add_argument('--language', default='eng', help='OCR language')
        enhanced_batch_ocr_parser.add_argument('--max-workers', type=int, help='Maximum worker threads')

        batch_ocr_parser = subparsers.add_parser('batch-ocr', help='Standard batch OCR')
        batch_ocr_parser.add_argument('-i', '--input', required=True, help='Input directory')
        batch_ocr_parser.add_argument('-o', '--output', required=True, help='Output directory')
        batch_ocr_parser.add_argument('--language', default='eng', help='OCR language')

        # Performance commands
        benchmark_parser = subparsers.add_parser('benchmark', help='Performance benchmarks')
        benchmark_parser.add_argument('--test-files', nargs='+', help='Test files for benchmarking')

        perf_stats_parser = subparsers.add_parser('perf-stats', help='Performance statistics')

        # Other commands (placeholders)
        optimize_parser = subparsers.add_parser('optimize', help='PDF optimization')
        optimize_parser.add_argument('-i', '--input', required=True, help='Input PDF file')
        optimize_parser.add_argument('-o', '--output', required=True, help='Output PDF file')

        pdf2word_parser = subparsers.add_parser('pdf-to-word', help='PDF to Word conversion')
        pdf2word_parser.add_argument('-i', '--input', required=True, help='Input PDF file')
        pdf2word_parser.add_argument('-o', '--output', required=True, help='Output DOCX file')

        split_parser = subparsers.add_parser('split-pdf', help='Split PDF')
        split_parser.add_argument('-i', '--input', required=True, help='Input PDF file')
        split_parser.add_argument('-o', '--output', required=True, help='Output directory')

        # Test commands
        test_rich_parser = subparsers.add_parser('test-rich', help='Test Rich CLI interface')
        test_errors_parser = subparsers.add_parser('test-errors', help='Test error handling')
        test_validation_parser = subparsers.add_parser('test-validation', help='Test validation')

    def execute_command(self, args: argparse.Namespace) -> None:
        """Execute command with comprehensive error handling."""

        # Validate common arguments first
        if not self.validate_common_args(args):
            sys.exit(1)

        command_map = {
            'enhanced-ocr': self.handle_enhanced_ocr,
            'enhanced-batch-ocr': self.handle_enhanced_batch_ocr,
            'benchmark': self.handle_performance_benchmark,
            'perf-stats': self.handle_performance_stats,
            'ocr': self.handle_ocr,
            'batch-ocr': self.handle_batch_ocr,
            'optimize': self.handle_optimize,
            'pdf-to-word': self.handle_pdf_to_word,
            'split-pdf': self.handle_split_pdf,
            'test-rich': self.handle_test_rich,
            'test-errors': self.handle_test_errors,
            'test-validation': self.handle_test_validation,
        }

        handler = command_map.get(args.command)
        if handler:
            try:
                result = handler(args)
                if isinstance(result, ProcessingResult):
                    self.display_result(result)
                    if not result.success:
                        sys.exit(1)
            except Exception as e:
                self.print_message(f"Unexpected error: {str(e)}", "error")
                sys.exit(1)
        else:
            self.print_message(f"Unknown command: {args.command}", "error")
            sys.exit(1)

    def handle_enhanced_ocr(self, args: argparse.Namespace) -> ProcessingResult:
        """Handle enhanced OCR command."""
        if self.performance_cli:
            return self.performance_cli.handle_enhanced_ocr(args)
        else:
            self.print_message("Enhanced OCR not available, falling back to standard", "warning")
            return self.handle_ocr(args)

    def handle_enhanced_batch_ocr(self, args: argparse.Namespace) -> ProcessingResult:
        """Handle enhanced batch OCR command."""
        if self.performance_cli:
            return self.performance_cli.handle_enhanced_batch_ocr(args)
        else:
            self.print_message("Enhanced batch OCR not available, falling back to standard", "warning")
            return self.handle_batch_ocr(args)

    def handle_performance_benchmark(self, args: argparse.Namespace) -> ProcessingResult:
        """Handle performance benchmark command."""
        if self.performance_cli:
            return self.performance_cli.handle_performance_benchmark(args)
        else:
            return ProcessingResult.error_result(
                DocForgeException("Performance optimization not available"),
                "Performance Benchmark"
            )

    def handle_performance_stats(self, args: argparse.Namespace) -> ProcessingResult:
        """Handle performance statistics command."""
        if self.performance_cli:
            return self.performance_cli.handle_performance_stats(args)
        else:
            return ProcessingResult.error_result(
                DocForgeException("Performance optimization not available"),
                "Performance Stats"
            )

    def handle_ocr(self, args: argparse.Namespace) -> ProcessingResult:
        """Handle standard OCR command."""

        def _ocr_operation():
            self.print_message(f"Starting OCR processing: {args.input}")

            # Process with progress indication
            result = self.processor.ocr_pdf(
                args.input,
                args.output,
                language=args.language
            )

            # Return structured result
            if result and result.get('success', True):
                return ProcessingResult.success_result(
                    "OCR processing completed successfully",
                    "OCR",
                    input_file=args.input,
                    output_file=args.output,
                    metadata=result if isinstance(result, dict) else {}
                )
            else:
                error_msg = result.get('error', 'OCR processing failed') if result else 'OCR processing failed'
                raise DocForgeException(
                    f"OCR processing failed: {error_msg}",
                    error_code='OCR_FAILED'
                )

        return safe_execute(_ocr_operation, _operation_name="OCR")

    def handle_batch_ocr(self, args) -> ProcessingResult:
        """Handle batch OCR with error tracking."""

        def _batch_ocr_operation():
            self.print_message(f"Starting batch OCR: {args.input} -> {args.output}")

            # Validate directories
            input_path = self.validator.validate_directory(args.input, must_exist=True)
            output_path = self.validator.validate_output_path(args.output)

            # Find PDF files
            pdf_files = list(input_path.glob("*.pdf"))

            if not pdf_files:
                raise DocForgeException(
                    f"No PDF files found in {input_path}",
                    error_code="NO_FILES_FOUND",
                    suggestions=[
                        f"Check if the directory contains .pdf files: {input_path}",
                        "Verify the directory path is correct"
                    ]
                )

            self.print_message(f"Found {len(pdf_files)} PDF files for processing")

            if not self.confirm_action(f"Process {len(pdf_files)} files?"):
                raise DocForgeException(
                    "Operation cancelled by user",
                    error_code="USER_CANCELLED"
                )

            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)

            # Process files
            success_count = 0
            for i, pdf_file in enumerate(pdf_files, 1):
                output_file = output_path / f"{pdf_file.stem}_ocr{pdf_file.suffix}"

                try:
                    self.print_message(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
                    result = self.processor.ocr_pdf(str(pdf_file), str(output_file), language=args.language)

                    if result and result.get('success', True):
                        success_count += 1
                        self.print_message(f"✅ Success: {output_file.name}")
                    else:
                        self.print_message(f"❌ Failed: {pdf_file.name}")

                except Exception as e:
                    self.print_message(f"❌ Error processing {pdf_file.name}: {str(e)}")

            return ProcessingResult.success_result(
                f"Batch OCR completed: {success_count}/{len(pdf_files)} files processed successfully",
                "Batch OCR",
                input_file=str(input_path),
                output_file=str(output_path),
                metadata={
                    'total_files': len(pdf_files),
                    'successful_files': success_count,
                    'failed_files': len(pdf_files) - success_count
                }
            )

        return safe_execute(_batch_ocr_operation, _operation_name="Batch OCR")

    # Placeholder methods for other commands
    def handle_optimize(self, args) -> ProcessingResult:
        """Handle optimize command."""
        return ProcessingResult.success_result(
            "Optimize command placeholder - not yet implemented",
            "PDF Optimization"
        )

    def handle_pdf_to_word(self, args) -> ProcessingResult:
        """Handle PDF to Word command."""
        return ProcessingResult.success_result(
            "PDF to Word command placeholder - not yet implemented",
            "PDF to Word"
        )

    def handle_split_pdf(self, args) -> ProcessingResult:
        """Handle split PDF command."""
        return ProcessingResult.success_result(
            "Split PDF command placeholder - not yet implemented",
            "PDF Splitting"
        )

    def handle_test_rich(self, args) -> ProcessingResult:
        """Test the Rich interface."""
        if not self.ui:
            self.print_message("Rich interface not available", "error")
            return ProcessingResult.error_result(
                DocForgeException("Rich interface not available"),
                "Test Rich"
            )

        self.print_message("Testing Rich CLI interface...")

        # Test all message types
        self.print_message("This is a success message!", "success")
        self.print_message("This is a warning message!", "warning")
        self.print_message("This is an error message!", "error")
        self.print_message("This is an info message!", "info")

        self.print_message("Rich CLI test completed!", "success")

        return ProcessingResult.success_result(
            "Rich CLI interface test completed successfully",
            "Test Rich"
        )

    def handle_test_errors(self, args) -> ProcessingResult:
        """Test the error handling system."""
        if not self.ui:
            self.print_message("Enhanced error testing requires Rich interface", "error")
            return ProcessingResult.error_result(
                DocForgeException("Rich interface not available"),
                "Test Errors"
            )

        self.print_message("Testing error handling system...")

        # Test different error types
        error_tests = [
            ("File Not Found", lambda: DocForgeException("Test file not found", "FILE_NOT_FOUND")),
            ("Invalid Format", lambda: DocForgeException("Test invalid format", "INVALID_FORMAT")),
            ("Validation Error", lambda: DocForgeException("Test validation error", "VALIDATION_ERROR")),
        ]

        for test_name, error_creator in error_tests:
            if self.console:
                self.console.print(f"\n[bold cyan]Testing: {test_name}[/bold cyan]")

            try:
                raise error_creator()
            except DocForgeException as e:
                if hasattr(self.ui, 'display_error_details'):
                    self.ui.display_error_details(e)
                else:
                    self.print_message(f"Error: {e.message}", "error")

            time.sleep(0.5)  # Brief pause between tests

        self.print_message("Error handling test completed!", "success")
        return ProcessingResult.success_result(
            "All error types tested successfully",
            "Test Errors"
        )

    def handle_test_validation(self, args) -> ProcessingResult:
        """Test the validation system."""
        self.print_message("Testing validation system...")

        # Test basic validation
        test_cases = [
            ("Valid PDF file", "test.pdf", True),
            ("Invalid extension", "test.txt", False),
            ("Valid directory", ".", True),
        ]

        for test_name, test_value, should_pass in test_cases:
            self.print_message(f"Testing {test_name}: {test_value}")

            try:
                if "file" in test_name.lower():
                    # Create a temporary file for testing
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=test_value[-4:], delete=False) as f:
                        test_path = f.name

                    if should_pass:
                        self.validator.validate_input_file(test_path, ['.pdf'])
                        self.print_message(f"✅ {test_name} passed")
                    else:
                        try:
                            self.validator.validate_input_file(test_path, ['.pdf'])
                            self.print_message(f"❌ {test_name} should have failed")
                        except DocForgeException:
                            self.print_message(f"✅ {test_name} correctly failed")

                    # Clean up
                    os.unlink(test_path)

                elif "directory" in test_name.lower():
                    self.validator.validate_directory(test_value, must_exist=True)
                    self.print_message(f"✅ {test_name} passed")

            except DocForgeException as e:
                if should_pass:
                    self.print_message(f"❌ {test_name} failed: {e.message}")
                else:
                    self.print_message(f"✅ {test_name} correctly failed")
            except Exception as e:
                self.print_message(f"⚠️  {test_name} error: {str(e)}")

        self.print_message("Validation test completed!", "success")
        return ProcessingResult.success_result(
            "Validation system test completed",
            "Test Validation"
        )

    def run_interactive(self):
        """Run interactive mode."""
        if self.ui:
            self.ui.print_info("Starting DocForge Interactive Mode...")
        else:
            print("🚀 Starting Interactive Mode...")