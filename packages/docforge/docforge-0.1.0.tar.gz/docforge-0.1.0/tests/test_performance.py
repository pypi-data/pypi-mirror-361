# tests/test_performance.py - Basic performance tests
"""
Basic performance tests for DocForge
"""

import pytest
import time
from docforge.core.validators import ParameterValidator, SmartParameterValidator
from docforge.cli.rich_interface import DocForgeUI


class TestPerformance:
    """Basic performance tests."""

    def test_parameter_validation_performance(self):
        """Test parameter validation performance."""
        start_time = time.time()

        # Run validation many times
        for _ in range(1000):
            ParameterValidator.validate_language_code('eng')
            ParameterValidator.validate_quality(85)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in reasonable time (adjust threshold as needed)
        assert duration < 1.0, f"Parameter validation too slow: {duration}s"

    def test_smart_validation_performance(self):
        """Test smart validation performance."""
        start_time = time.time()

        # Run smart validation many times
        for _ in range(100):
            result, _ = SmartParameterValidator.validate_and_suggest_language("eng")
            assert result == "eng"

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in reasonable time
        assert duration < 1.0, f"Smart validation too slow: {duration}s"

    def test_ui_creation_performance(self):
        """Test UI creation performance."""
        start_time = time.time()

        # Create UI multiple times
        for _ in range(10):
            ui = DocForgeUI()
            assert ui.console is not None

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly
        assert duration < 0.5, f"UI creation too slow: {duration}s"