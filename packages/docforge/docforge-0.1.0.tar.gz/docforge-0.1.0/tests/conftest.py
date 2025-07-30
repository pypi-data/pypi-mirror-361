# tests/conftest.py - pytest configuration and fixtures
"""
Pytest configuration and shared fixtures for DocForge testing
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add docforge to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from docforge.core.exceptions import DocForgeException, ProcessingResult
from docforge.cli.rich_interface import DocForgeUI
from docforge.cli.interface import CLIInterface


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Create a mock PDF file path."""
    pdf_path = temp_dir / "sample.pdf"
    # Create a dummy file
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n%%EOF")
    return pdf_path


@pytest.fixture
def nonexistent_pdf_path(temp_dir):
    """Return path to a nonexistent PDF file."""
    return temp_dir / "nonexistent.pdf"


@pytest.fixture
def cli_interface():
    """Create CLI interface for testing."""
    return CLIInterface(use_rich=False)  # Disable Rich for easier testing


@pytest.fixture
def rich_ui():
    """Create Rich UI for testing."""
    return DocForgeUI()


@pytest.fixture
def mock_processor():
    """Mock DocumentProcessor for testing."""
    mock = Mock()
    mock.ocr_pdf.return_value = {'success': True, 'message': 'OCR completed'}
    mock.pdf_to_word.return_value = {'success': True, 'message': 'Conversion completed'}
    mock.optimize_pdf.return_value = {'success': True, 'message': 'Optimization completed'}
    return mock

