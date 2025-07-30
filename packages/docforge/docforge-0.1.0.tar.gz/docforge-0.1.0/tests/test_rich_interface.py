# tests/test_rich_interface.py - Test Rich UI components
"""
Test Rich UI interface components
"""

import pytest
from unittest.mock import patch, Mock
from docforge.cli.rich_interface import DocForgeUI, BatchProgressTracker
from docforge.core.exceptions import DocForgeException, ValidationError


class TestDocForgeUI:
    """Test DocForge Rich UI components."""

    def test_ui_initialization(self, rich_ui):
        """Test UI initialization."""
        assert hasattr(rich_ui, 'console')
        assert rich_ui.console is not None

    def test_error_display(self, rich_ui):
        """Test error display functionality."""
        error = DocForgeException(
            "Test error",
            error_code="TEST_ERROR",
            context={"file_path": "test.pdf"},
            suggestions=["Try again", "Check file"]
        )

        # Should not raise exception
        try:
            rich_ui.display_error_details(error)
        except Exception as e:
            pytest.fail(f"Error display failed: {e}")

    def test_validation_error_display(self, rich_ui):
        """Test validation error display."""
        error = ValidationError("quality", 150, "1-100", ["Use value between 1-100"])

        # Should not raise exception
        try:
            rich_ui.display_error_details(error)
        except Exception as e:
            pytest.fail(f"Validation error display failed: {e}")

    def test_results_table_display(self, rich_ui):
        """Test results table display."""
        results = [
            {
                'input_file': 'test1.pdf',
                'success': True,
                'file_size': 1024,
                'processing_time': 1.5,
                'output_file': 'output1.pdf'
            },
            {
                'input_file': 'test2.pdf',
                'success': False,
                'file_size': 2048,
                'processing_time': 0.5,
                'output_file': None
            }
        ]

        # Should not raise exception
        try:
            rich_ui.display_results_table(results, "Test Results")
        except Exception as e:
            pytest.fail(f"Results table display failed: {e}")


class TestBatchProgressTracker:
    """Test batch progress tracking."""

    def test_batch_tracker_initialization(self, rich_ui):
        """Test batch tracker initialization."""
        tracker = BatchProgressTracker(rich_ui)
        assert tracker.ui == rich_ui
        assert tracker.results == []
        assert tracker.errors == []

    def test_batch_tracking_workflow(self, rich_ui):
        """Test complete batch tracking workflow."""
        tracker = BatchProgressTracker(rich_ui)

        # Start batch
        tracker.start_batch(3, "Test Operation")
        assert tracker.results == []

        # Add results
        from docforge.core.exceptions import ProcessingResult

        result1 = ProcessingResult.success_result(
            "File 1 processed", "test",
            input_file="file1.pdf", processing_time=1.0
        )
        tracker.update_progress(result1)

        result2 = ProcessingResult.error_result(
            DocForgeException("Test error"), "test",
            input_file="file2.pdf", processing_time=0.5
        )
        tracker.update_progress(result2)

        assert len(tracker.results) == 2
        assert len(tracker.errors) == 1

        # Finish batch
        try:
            tracker.finish_batch("Test Operation")
        except Exception as e:
            pytest.fail(f"Batch finish failed: {e}")

