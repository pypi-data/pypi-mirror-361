"""
Main DocForge processor that coordinates all operations.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .exceptions import DocForgeException
from ..pdf.ocr import PDFOCRProcessor
from ..pdf.optimizer import PDFOptimizer
from ..utils.logger import setup_logger
from ..pdf.pdf_merger import PDFMerger
from ..pdf.pdf_to_word import PDFToWordConverter
from ..pdf.pdf_splitter import PDFSplitter


class DocumentProcessor:
    """Main DocForge processor that coordinates all operations."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = setup_logger(__name__, verbose)

        # Initialize operation modules
        self.ocr_processor = PDFOCRProcessor(verbose)
        self.optimizer = PDFOptimizer(verbose)
        self.merger = PDFMerger(verbose)
        self.pdf_to_word_converter = PDFToWordConverter(verbose)
        self.pdf_splitter = PDFSplitter(verbose)

        if verbose:
            print("🔨 DocForge DocumentProcessor initialized")
            print(f"   OCR available: {self.ocr_processor.has_dependencies}")
            print(f"   PDF processing available: {self.optimizer.has_dependencies}")
            print(f"   PDF merging available: {self.merger.has_dependencies}")
            print(f"   PDF to Word conversion available: {self.pdf_to_word_converter.has_dependencies}")
            print(f"   PDF splitting available: {self.pdf_splitter.has_dependencies}")

    # OCR methods
    def ocr_pdf(self, input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Add OCR text layer to PDF using proven implementation."""
        return self.ocr_processor.ocr_pdf(input_path, output_path, **kwargs)

    def batch_ocr_pdfs(self, input_folder: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Batch OCR PDF files."""
        return self.ocr_processor.batch_ocr_pdfs(input_folder, output_folder, **kwargs)

    # Optimization methods
    def optimize_pdf(self, input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Optimize a single PDF file."""
        return self.optimizer.optimize_pdf(input_path, output_path, **kwargs)

    def batch_optimize_pdfs(self, input_folder: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Batch optimize PDF files."""
        return self.optimizer.batch_optimize_pdfs(input_folder, output_folder, **kwargs)

    # Merger methods
    def merge_pdfs(self, *args, **kwargs):
        """Merge multiple PDF files."""
        return self.merger.merge_pdfs(*args, **kwargs)

    def merge_folder(self, *args, **kwargs):
        """Merge all PDFs in a folder."""
        return self.merger.merge_folder(*args, **kwargs)

    def merge_specific_files(self, *args, **kwargs):
        """Merge specific PDF files in custom order."""
        return self.merger.merge_specific_files(*args, **kwargs)

    def choose_merge_method(self, *args, **kwargs):
        """Interactive method selection for merging."""
        return self.merger.choose_merge_method(*args, **kwargs)

    def analyze_merge_candidates(self, *args, **kwargs):
        """Analyze PDFs in a folder for merging."""
        return self.merger.analyze_merge_candidates(*args, **kwargs)

    # PDF to Word conversion methods
    def pdf_to_word(self, input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Convert PDF to Word document."""
        return self.pdf_to_word_converter.convert_pdf_to_word(input_path, output_path, **kwargs)

    def batch_pdf_to_word(self, input_folder: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Batch convert PDF files to Word documents."""
        return self.pdf_to_word_converter.batch_convert_pdfs_to_word(input_folder, output_folder, **kwargs)

    # PDF splitting methods
    def split_pdf(self, input_path: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Split PDF into multiple files."""
        return self.pdf_splitter.split_pdf(input_path, output_folder, **kwargs)

    def split_pdf_by_pages(self, input_path: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Split PDF by specific page ranges."""
        return self.pdf_splitter.split_pdf_by_pages(input_path, output_folder, **kwargs)

    def split_pdf_by_size(self, input_path: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Split PDF by file size."""
        return self.pdf_splitter.split_pdf_by_size(input_path, output_folder, **kwargs)

    def split_pdf_by_bookmarks(self, input_path: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Split PDF by bookmarks."""
        return self.pdf_splitter.split_pdf_by_bookmarks(input_path, output_folder, **kwargs)

    def batch_split_pdfs(self, input_folder: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Batch split PDF files."""
        return self.pdf_splitter.batch_split_pdfs(input_folder, output_folder, **kwargs)