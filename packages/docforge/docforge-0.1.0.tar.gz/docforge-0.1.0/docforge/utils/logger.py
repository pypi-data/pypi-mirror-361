"""Logging utilities for DocForge."""

import logging
import sys


def setup_logger(name: str, verbose: bool = False) -> logging.Logger:
    """Setup logger with appropriate level."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger
