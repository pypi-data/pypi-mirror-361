#!/usr/bin/env python3
"""
🔨 DocForge - Basic Usage Examples
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docforge.core.processor import DocumentProcessor


def main():
    """Basic DocForge usage examples."""
    print("🔨 DocForge - Basic Usage Examples")
    print("=" * 40)

    # Initialize the processor
    processor = DocumentProcessor(verbose=True)

    print("\n📖 Example 1: OCR Processing")
    print("-" * 30)
    print("# Convert scanned PDF to searchable")
    print("processor.ocr_pdf('scanned.pdf', 'searchable.pdf', language='eng')")

    print("\n📖 Example 2: PDF Optimization")
    print("-" * 30)
    print("# Optimize PDF for smaller size")
    print("processor.optimize_pdf('large.pdf', 'optimized.pdf', optimization_type='aggressive')")

    print("\n📖 Example 3: Batch Processing")
    print("-" * 30)
    print("# Process multiple files at once")
    print("processor.batch_ocr_pdfs('scanned_folder/', 'searchable_folder/')")

    print("\n🚀 To run actual processing:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Install system dependencies (Tesseract, Poppler)")
    print("3. Replace these examples with your actual file paths")
    print("4. Run: python examples/basic_usage.py")

    print("\n🔨 DocForge: Forge perfect documents with precision!")


if __name__ == "__main__":
    main()
