# tests/test_cli_interface.py - Test CLI interface
"""
Test the enhanced CLI interface
"""

import pytest
from unittest.mock import patch, Mock
import argparse
from docforge.cli.interface import CLIInterface
from docforge.core.exceptions import ProcessingResult


class TestCLIInterface:
    """Test CLI interface functionality."""

    def test_cli_initialization(self):
        """Test CLI interface initialization."""
        cli = CLIInterface(use_rich=False)
        assert cli.use_rich is False
        assert cli.ui is None

    def test_cli_initialization_with_rich(self):
        """Test CLI interface with Rich enabled."""
        cli = CLIInterface(use_rich=True)
        # Rich might not be available in test environment
        assert hasattr(cli, 'ui')

    def test_print_message_basic(self, cli_interface, capsys):
        """Test basic message printing."""
        cli_interface.print_message("Test message", "info")
        captured = capsys.readouterr()
        assert "Test message" in captured.out

    @patch('docforge.cli.interface.DocumentProcessor')
    def test_handle_test_validation(self, mock_processor, cli_interface):
        """Test validation testing command."""
        # Create mock args
        args = Mock()

        # Test without Rich UI
        cli_interface.ui = None
        result = cli_interface.handle_test_validation(args)

        # Should handle gracefully when Rich is not available
        assert result is None or isinstance(result, ProcessingResult)
