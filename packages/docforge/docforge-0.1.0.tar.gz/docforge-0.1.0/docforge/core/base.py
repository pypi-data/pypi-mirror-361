"""Base classes and interfaces for DocForge operations."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging


class BaseProcessor(ABC):
    """Base class for all DocForge processors."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = logging.getLogger(self.__class__.__name__)
        if verbose:
            self.logger.setLevel(logging.DEBUG)

    @abstractmethod
    def process(self, *args, **kwargs) -> Dict[str, Any]:
        """Process the operation."""
        pass

    def validate_input(self, input_path: str) -> bool:
        """Validate input file exists and is correct format."""
        from pathlib import Path

        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        return True
