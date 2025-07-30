"""
🔨 DocForge - Document Processing Toolkit
Forge perfect documents from any format with precision, power, and simplicity.
"""

__version__ = "1.0.0"
__author__ = "Oscar Song"
__description__ = "Document processing toolkit with proven implementations"

from .core.processor import DocumentProcessor
from .core.exceptions import DocForgeException

__all__ = ["DocumentProcessor", "DocForgeException"]