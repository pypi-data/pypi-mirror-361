"""
PDF merger functionality using proven implementation.
Merge multiple PDFs with optional page numbering while preserving signatures.
"""

import os
import glob
from pathlib import Path
from typing import Dict, Any, List, Union

try:
    import fitz  # PyMuPDF

    HAS_PDF_DEPS = True
except ImportError:
    HAS_PDF_DEPS = False
    print("PDF dependencies not available. Install with: pip install PyMuPDF")

from ..core.base import BaseProcessor
from ..core.exceptions import DocForgeException


def get_file_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)


class PDFMerger(BaseProcessor):
    """Handles PDF merging operations using proven implementation."""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.has_dependencies = HAS_PDF_DEPS

    def process(self, input_path: Union[str, List[str]], output_path: str, **kwargs) -> Dict[str, Any]:
        """Process PDF merging."""
        return self.merge_pdfs(input_path, output_path, **kwargs)

    def merge_pdfs(self, input_folder_or_files: Union[str, List[str]], output_path: str,
                   add_page_numbers: bool = True,
                   font_size: int = 12,
                   right_margin: int = 72,
                   bottom_margin: int = 54,
                   preserve_signatures: bool = True,
                   **kwargs) -> Dict[str, Any]:
        """
        Merge multiple PDF files with optional page numbering while preserving signatures.

        Args:
            input_folder_or_files: Either a folder path containing PDFs or a list of PDF file paths
            output_path: Path for the merged output PDF
            add_page_numbers: Boolean flag - True to add page numbers, False to merge only
            font_size: Font size for page numbers (default: 12)
            right_margin: Distance from right edge in points (default: 72 = 1 inch)
            bottom_margin: Distance from bottom edge in points (default: 54 = 0.75 inch)
            preserve_signatures: Use signature-preserving merge method

        Returns:
            Dict[str, Any]: Processing results
        """

        if not self.has_dependencies:
            raise DocForgeException("PDF dependencies not installed. Run: pip install PyMuPDF")

        try:
            # Get list of PDF files
            if isinstance(input_folder_or_files, str) and os.path.isdir(input_folder_or_files):
                # If it's a folder, get all PDF files
                pdf_files = glob.glob(os.path.join(input_folder_or_files, "*.pdf"))
                pdf_files.sort()  # Sort alphabetically
            elif isinstance(input_folder_or_files, list):
                # If it's a list of files
                pdf_files = input_folder_or_files
            else:
                raise ValueError("input_folder_or_files must be a folder path or list of file paths")

            if not pdf_files:
                raise ValueError("No PDF files found")

            if self.verbose:
                print(f"📄 Found {len(pdf_files)} PDF files to merge:")
                for i, file in enumerate(pdf_files, 1):
                    print(f"  {i}. {os.path.basename(file)}")

                if add_page_numbers:
                    print("📄 Page numbers will be added")
                else:
                    print("📄 Merge only - no page numbers will be added")

            # Calculate total original size
            total_original_size = sum(get_file_size_mb(f) for f in pdf_files if os.path.exists(f))

            if preserve_signatures:
                self._merge_preserve_signatures(pdf_files, output_path, add_page_numbers,
                                                font_size, right_margin, bottom_margin)
            else:
                self._merge_standard(pdf_files, output_path, add_page_numbers,
                                     font_size, right_margin, bottom_margin)

            # Calculate final size
            final_size = get_file_size_mb(output_path)

            if self.verbose:
                action = "merged with page numbers" if add_page_numbers else "merged without page numbers"
                method = "signature-preserving" if preserve_signatures else "standard"
                print(f"✅ Successfully {action} {len(pdf_files)} PDFs using {method} method")
                print(f"📏 Total size: {total_original_size:.2f} MB → {final_size:.2f} MB")

            return {
                'success': True,
                'files_merged': len(pdf_files),
                'add_page_numbers': add_page_numbers,
                'preserve_signatures': preserve_signatures,
                'total_original_size_mb': total_original_size,
                'final_size_mb': final_size,
                'output_path': output_path
            }

        except Exception as e:
            raise DocForgeException(f"Failed to merge PDFs: {str(e)}")

    def _merge_standard(self, pdf_files: List[str], output_path: str, add_page_numbers: bool,
                        font_size: int, right_margin: int, bottom_margin: int):
        """Standard merge method."""
        merged_doc = fitz.open()
        page_counter = 1

        for pdf_file in pdf_files:
            if self.verbose:
                print(f"🔄 Processing: {os.path.basename(pdf_file)}")

            current_doc = fitz.open(pdf_file)
            pages_in_current = len(current_doc)

            # Insert entire document at once to better preserve structure
            merged_doc.insert_pdf(current_doc)

            # Add page numbers only if flag is True
            if add_page_numbers:
                for i in range(pages_in_current):
                    page_index = len(merged_doc) - pages_in_current + i
                    merged_page = merged_doc.load_page(page_index)
                    rect = merged_page.rect

                    text = str(page_counter)
                    point = fitz.Point(rect.width - right_margin, rect.height - bottom_margin)

                    merged_page.insert_text(
                        point,
                        text,
                        fontsize=font_size,
                        color=(0, 0, 0),
                        fontname="helv"
                    )
                    page_counter += 1
            else:
                page_counter += pages_in_current

            if self.verbose:
                print(f"  ✅ Added {pages_in_current} pages")
            current_doc.close()

        # Save with standard settings
        if self.verbose:
            print(f"💾 Saving merged PDF to: {output_path}")

        merged_doc.save(
            output_path,
            garbage=0,
            clean=False,
            deflate=False,
            deflate_images=False,
            deflate_fonts=False,
            incremental=False,
            ascii=False,
            expand=0,
            linear=False
        )
        merged_doc.close()

    def _merge_preserve_signatures(self, pdf_files: List[str], output_path: str, add_page_numbers: bool,
                                   font_size: int, right_margin: int, bottom_margin: int):
        """Signature-preserving merge method."""
        # Start with first document as base
        merged_doc = fitz.open(pdf_files[0])
        page_counter = 1

        # Add page numbers to first document only if flag is True
        if add_page_numbers:
            for page_num in range(len(merged_doc)):
                page = merged_doc.load_page(page_num)
                rect = page.rect

                text = str(page_counter)
                point = fitz.Point(rect.width - right_margin, rect.height - bottom_margin)

                page.insert_text(point, text, fontsize=font_size, color=(0, 0, 0), fontname="helv")
                page_counter += 1
        else:
            page_counter += len(merged_doc)

        if self.verbose:
            print(f"📄 Base document: {os.path.basename(pdf_files[0])} - {len(merged_doc)} pages")

        # Append remaining documents
        for pdf_file in pdf_files[1:]:
            if self.verbose:
                print(f"🔄 Processing: {os.path.basename(pdf_file)}")

            current_doc = fitz.open(pdf_file)
            pages_in_current = len(current_doc)

            # Insert entire document to preserve structure
            merged_doc.insert_pdf(current_doc)

            # Add page numbers to newly added pages only if flag is True
            if add_page_numbers:
                start_page = len(merged_doc) - pages_in_current
                for i in range(pages_in_current):
                    page = merged_doc.load_page(start_page + i)
                    rect = page.rect

                    text = str(page_counter)
                    point = fitz.Point(rect.width - right_margin, rect.height - bottom_margin)

                    page.insert_text(point, text, fontsize=font_size, color=(0, 0, 0), fontname="helv")
                    page_counter += 1
            else:
                page_counter += pages_in_current

            current_doc.close()
            if self.verbose:
                print(f"  ✅ Added {pages_in_current} pages")

        # Save with minimal processing for signature preservation
        if self.verbose:
            print(f"💾 Saving signature-preserved PDF to: {output_path}")

        merged_doc.save(output_path, garbage=0, clean=False, deflate=False)
        merged_doc.close()

    def merge_specific_files(self, file_list: List[str], output_path: str,
                             add_page_numbers: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Merge specific PDF files in the exact order provided.

        Args:
            file_list: List of PDF file paths in desired order
            output_path: Path for merged output PDF
            add_page_numbers: Boolean flag - True to add page numbers, False to merge only

        Returns:
            Dict[str, Any]: Processing results
        """
        return self.merge_pdfs(file_list, output_path, add_page_numbers, **kwargs)

    def merge_folder(self, folder_path: str, output_path: str,
                     add_page_numbers: bool = True, pattern: str = "*.pdf", **kwargs) -> Dict[str, Any]:
        """
        Merge all PDFs in a folder (sorted alphabetically).

        Args:
            folder_path: Folder containing PDF files
            output_path: Path for merged output PDF
            add_page_numbers: Boolean flag - True to add page numbers, False to merge only
            pattern: File pattern to match (default: "*.pdf")

        Returns:
            Dict[str, Any]: Processing results
        """
        pdf_files = glob.glob(os.path.join(folder_path, pattern))

        if not pdf_files:
            raise DocForgeException(f"No PDF files found in {folder_path}")

        pdf_files.sort()  # Sort alphabetically
        return self.merge_pdfs(pdf_files, output_path, add_page_numbers, **kwargs)

    def choose_merge_method(self):
        """Interactive method selection for users."""
        print("📄 PDF Merge Methods")
        print("=" * 50)
        print("Choose your merge method:")
        print()
        print("1. Merge Folder (alphabetical order)")
        print("   - Merge all PDFs in a folder")
        print("   - Files sorted alphabetically")
        print("   - Best for: Multiple files in one location")
        print()
        print("2. Merge Specific Files (custom order)")
        print("   - Choose exact files and order")
        print("   - Full control over sequence")
        print("   - Best for: Specific document assembly")
        print()
        print("3. Standard Merge")
        print("   - Fast merging with standard preservation")
        print("   - Good for most documents")
        print()
        print("4. Signature-Preserving Merge")
        print("   - Maximum preservation of signatures/forms")
        print("   - Best for: Legal documents, signed PDFs")
        print()

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            return self._run_folder_merge()
        elif choice == "2":
            return self._run_specific_files_merge()
        elif choice == "3":
            return self._run_standard_merge()
        elif choice == "4":
            return self._run_signature_preserving_merge()
        else:
            print("❌ Invalid choice. Using folder merge.")
            return self._run_folder_merge()

    def _run_folder_merge(self):
        """Run folder merge with user input."""
        print("\n--- Merge Folder ---")
        folder_path = input("📁 Input folder path: ").strip()
        output_path = input("📁 Output PDF file: ").strip()

        add_numbers = input("Add page numbers? (y/n) [y]: ").strip().lower()
        add_page_numbers = add_numbers != 'n'

        preserve_sigs = input("Preserve signatures? (y/n) [y]: ").strip().lower()
        preserve_signatures = preserve_sigs != 'n'

        return self.merge_folder(folder_path, output_path,
                                 add_page_numbers=add_page_numbers,
                                 preserve_signatures=preserve_signatures)

    def _run_specific_files_merge(self):
        """Run specific files merge with user input."""
        print("\n--- Merge Specific Files ---")
        print("Enter file paths (one per line, empty line to finish):")

        file_list = []
        while True:
            file_path = input(f"File {len(file_list) + 1}: ").strip()
            if not file_path:
                break
            if not os.path.exists(file_path):
                print(f"⚠️ Warning: File not found: {file_path}")
            file_list.append(file_path)

        if not file_list:
            print("❌ No files specified")
            return

        output_path = input("📁 Output PDF file: ").strip()

        add_numbers = input("Add page numbers? (y/n) [y]: ").strip().lower()
        add_page_numbers = add_numbers != 'n'

        preserve_sigs = input("Preserve signatures? (y/n) [y]: ").strip().lower()
        preserve_signatures = preserve_sigs != 'n'

        return self.merge_specific_files(file_list, output_path,
                                         add_page_numbers=add_page_numbers,
                                         preserve_signatures=preserve_signatures)

    def _run_standard_merge(self):
        """Run standard merge with user input."""
        print("\n--- Standard Merge ---")
        input_source = input("Input (folder path or file1.pdf,file2.pdf): ").strip()
        output_path = input("📁 Output PDF file: ").strip()

        # Determine if it's a folder or file list
        if ',' in input_source:
            file_list = [f.strip() for f in input_source.split(',')]
            input_files = file_list
        else:
            input_files = input_source

        add_numbers = input("Add page numbers? (y/n) [y]: ").strip().lower()
        add_page_numbers = add_numbers != 'n'

        return self.merge_pdfs(input_files, output_path,
                               add_page_numbers=add_page_numbers,
                               preserve_signatures=False)

    def _run_signature_preserving_merge(self):
        """Run signature-preserving merge with user input."""
        print("\n--- Signature-Preserving Merge ---")
        input_source = input("Input (folder path or file1.pdf,file2.pdf): ").strip()
        output_path = input("📁 Output PDF file: ").strip()

        # Determine if it's a folder or file list
        if ',' in input_source:
            file_list = [f.strip() for f in input_source.split(',')]
            input_files = file_list
        else:
            input_files = input_source

        add_numbers = input("Add page numbers? (y/n) [y]: ").strip().lower()
        add_page_numbers = add_numbers != 'n'

        return self.merge_pdfs(input_files, output_path,
                               add_page_numbers=add_page_numbers,
                               preserve_signatures=True)

    def analyze_merge_candidates(self, folder_path: str):
        """Analyze PDFs in a folder for merging."""
        if not os.path.isdir(folder_path):
            print(f"❌ Not a valid folder: {folder_path}")
            return

        pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

        if not pdf_files:
            print(f"❌ No PDF files found in {folder_path}")
            return

        pdf_files.sort()

        print(f"📊 Merge Analysis: {folder_path}")
        print(f"📄 Found {len(pdf_files)} PDF files")
        print()

        total_size = 0
        total_pages = 0

        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                doc = fitz.open(pdf_file)
                pages = len(doc)
                size_mb = get_file_size_mb(pdf_file)
                total_size += size_mb
                total_pages += pages
                doc.close()

                print(f"{i:2d}. {os.path.basename(pdf_file)}")
                print(f"     📄 {pages} pages, 📏 {size_mb:.2f} MB")

            except Exception as e:
                print(f"{i:2d}. {os.path.basename(pdf_file)} - ❌ Error: {e}")

        print()
        print(f"📊 Total: {total_pages} pages, {total_size:.2f} MB")
        print(f"💾 Estimated merged size: {total_size:.2f} MB")

        if total_pages > 100:
            print("💡 Recommendation: Large merge - consider signature preservation")
        elif total_size > 50:
            print("💡 Recommendation: Large files - monitor memory usage")
        else:
            print("💡 Recommendation: Standard merge should work well")


# Convenience functions for easy usage
def create_pdf_merger(verbose=True):
    """Factory function to create PDF merger instance."""
    return PDFMerger(verbose=verbose)


def run_interactive_merger():
    """Run the interactive PDF merger."""
    merger = create_pdf_merger(verbose=True)

    if not merger.has_dependencies:
        print("❌ PDF dependencies not installed. Run: pip install PyMuPDF")
        return

    try:
        return merger.choose_merge_method()
    except KeyboardInterrupt:
        print("\n\n👋 PDF merge cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")


# Example usage
if __name__ == "__main__":
    run_interactive_merger()
