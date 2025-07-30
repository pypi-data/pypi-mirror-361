"""
PDF splitter functionality using proven implementation.
Split PDFs by pages, bookmarks, or file size while preserving document integrity.
"""

import os
import glob
from pathlib import Path
from typing import Dict, Any, List, Union, Tuple

try:
    from PyPDF2 import PdfReader, PdfWriter
    HAS_PDF_DEPS = True
except ImportError:
    HAS_PDF_DEPS = False
    print("PDF dependencies not available. Install with: pip install PyPDF2")

from ..core.base import BaseProcessor
from ..core.exceptions import DocForgeException


def get_file_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)


class PDFSplitter(BaseProcessor):
    """Handles PDF splitting operations using proven implementation."""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.has_dependencies = HAS_PDF_DEPS

    def process(self, input_path: Union[str, List[str]], output_path: str, **kwargs) -> Dict[str, Any]:
        """Process PDF splitting."""
        return self.split_pdf(input_path, output_path, **kwargs)

    def split_pdf(self, input_path: str, output_dir: str,
                  split_type: str = "pages",
                  pages_per_file: int = 1,
                  page_ranges: str = None,
                  max_size_mb: float = 10.0,
                  **kwargs) -> Dict[str, Any]:
        """
        Split PDF into multiple files using various methods.

        Args:
            input_path: Path to input PDF file
            output_dir: Directory for output files
            split_type: Type of split ('pages', 'size', 'bookmarks')
            pages_per_file: Pages per file for 'pages' split type
            page_ranges: Page ranges for extraction (e.g., "1-5,10-15")
            max_size_mb: Maximum file size in MB for 'size' split type

        Returns:
            Dict[str, Any]: Processing results
        """

        if not self.has_dependencies:
            raise DocForgeException("PDF dependencies not installed. Run: pip install PyPDF2")

        try:
            # Validate input
            if not os.path.exists(input_path):
                raise DocForgeException(f"Input file not found: {input_path}")

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            if self.verbose:
                print(f"🔪 Starting PDF splitting: {os.path.basename(input_path)}")
                print(f"📁 Output directory: {output_dir}")
                print(f"🔧 Split type: {split_type}")

            # Calculate original size
            original_size = get_file_size_mb(input_path)

            # Choose splitting method
            if split_type == "pages" and page_ranges:
                output_files = self._split_by_page_ranges(input_path, output_dir, page_ranges)
            elif split_type == "pages":
                output_files = self._split_by_fixed_pages(input_path, output_dir, pages_per_file)
            elif split_type == "size":
                output_files = self._split_by_size(input_path, output_dir, max_size_mb)
            elif split_type == "bookmarks":
                output_files = self._split_by_bookmarks(input_path, output_dir)
            else:
                raise DocForgeException(f"Unknown split type: {split_type}")

            # Calculate total output size
            total_output_size = sum(get_file_size_mb(f) for f in output_files if os.path.exists(f))

            if self.verbose:
                print(f"✅ Successfully split PDF into {len(output_files)} files")
                print(f"📏 Original size: {original_size:.2f} MB → Total output: {total_output_size:.2f} MB")

            return {
                'success': True,
                'split_type': split_type,
                'files_created': len(output_files),
                'output_files': output_files,
                'original_size_mb': original_size,
                'total_output_size_mb': total_output_size,
                'output_dir': output_dir
            }

        except Exception as e:
            raise DocForgeException(f"Failed to split PDF: {str(e)}")

    def split_pdf_by_pages(self, input_path: str, output_dir: str, page_ranges: str, **kwargs) -> Dict[str, Any]:
        """
        Split PDF by specific page ranges.

        Args:
            input_path: Path to input PDF file
            output_dir: Directory for output files
            page_ranges: Page ranges (e.g., "1-5,10-15")

        Returns:
            Dict[str, Any]: Processing results
        """
        return self.split_pdf(input_path, output_dir, split_type="pages", page_ranges=page_ranges, **kwargs)

    def split_pdf_by_size(self, input_path: str, output_dir: str, max_size_mb: float = 10.0, **kwargs) -> Dict[str, Any]:
        """
        Split PDF by file size.

        Args:
            input_path: Path to input PDF file
            output_dir: Directory for output files
            max_size_mb: Maximum file size in MB

        Returns:
            Dict[str, Any]: Processing results
        """
        return self.split_pdf(input_path, output_dir, split_type="size", max_size_mb=max_size_mb, **kwargs)

    def split_pdf_by_bookmarks(self, input_path: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """
        Split PDF by bookmarks.

        Args:
            input_path: Path to input PDF file
            output_dir: Directory for output files

        Returns:
            Dict[str, Any]: Processing results
        """
        return self.split_pdf(input_path, output_dir, split_type="bookmarks", **kwargs)

    def batch_split_pdfs(self, input_folder: str, output_folder: str, split_type: str = "pages",
                         **kwargs) -> Dict[str, Any]:
        """
        Batch split multiple PDF files.

        Args:
            input_folder: Directory containing input PDF files
            output_folder: Directory for output files
            split_type: Type of split ('pages', 'size', 'bookmarks')

        Returns:
            Dict[str, Any]: Batch processing results
        """
        if not self.has_dependencies:
            raise DocForgeException("PDF dependencies not installed. Run: pip install PyPDF2")

        try:
            # Find PDF files
            pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))
            if not pdf_files:
                raise DocForgeException(f"No PDF files found in {input_folder}")

            # Ensure output directory exists
            os.makedirs(output_folder, exist_ok=True)

            if self.verbose:
                print(f"🔪 Starting batch PDF splitting: {len(pdf_files)} files")
                print(f"📁 Input folder: {input_folder}")
                print(f"📁 Output folder: {output_folder}")
                print(f"🔧 Split type: {split_type}")

            results = []
            successful = 0
            failed = 0
            total_files_created = 0

            for pdf_file in pdf_files:
                try:
                    filename = os.path.basename(pdf_file)
                    file_output_dir = os.path.join(output_folder, os.path.splitext(filename)[0])

                    if self.verbose:
                        print(f"🔄 Processing: {filename}")

                    result = self.split_pdf(pdf_file, file_output_dir, split_type=split_type, **kwargs)
                    results.append(result)

                    if result['success']:
                        successful += 1
                        total_files_created += result['files_created']
                        if self.verbose:
                            print(f"  ✅ Created {result['files_created']} files")
                    else:
                        failed += 1

                except Exception as e:
                    failed += 1
                    if self.verbose:
                        print(f"  ❌ Failed: {str(e)}")
                    results.append({
                        'success': False,
                        'error': str(e),
                        'input_file': pdf_file
                    })

            if self.verbose:
                print(f"✅ Batch splitting completed: {successful}/{len(pdf_files)} successful")
                print(f"📄 Total files created: {total_files_created}")

            return {
                'success': True,
                'split_type': split_type,
                'total_input_files': len(pdf_files),
                'successful': successful,
                'failed': failed,
                'total_files_created': total_files_created,
                'results': results,
                'input_folder': input_folder,
                'output_folder': output_folder
            }

        except Exception as e:
            raise DocForgeException(f"Failed to batch split PDFs: {str(e)}")

    def _split_by_page_ranges(self, input_path: str, output_dir: str, page_ranges: str) -> List[str]:
        """Split PDF by specific page ranges."""
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        base_name = os.path.splitext(os.path.basename(input_path))[0]

        if self.verbose:
            print(f"📄 Total pages: {total_pages}")
            print(f"📋 Page ranges: {page_ranges}")

        # Parse page ranges
        ranges = self._parse_page_ranges(page_ranges)
        output_files = []

        for i, (start, end) in enumerate(ranges):
            if start < 1 or end > total_pages:
                raise DocForgeException(f"Page range {start}-{end} is invalid for {total_pages} pages")

            output_filename = f"{base_name}_pages_{start}-{end}.pdf"
            output_path = os.path.join(output_dir, output_filename)

            writer = PdfWriter()
            for page_num in range(start - 1, end):  # Convert to 0-indexed
                writer.add_page(reader.pages[page_num])

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            output_files.append(output_path)

            if self.verbose:
                print(f"  ✅ Created: {output_filename} (pages {start}-{end})")

        return output_files

    def _split_by_fixed_pages(self, input_path: str, output_dir: str, pages_per_file: int) -> List[str]:
        """Split PDF into files with fixed number of pages."""
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        base_name = os.path.splitext(os.path.basename(input_path))[0]

        if self.verbose:
            print(f"📄 Total pages: {total_pages}")
            print(f"📋 Pages per file: {pages_per_file}")

        output_files = []
        file_count = 1

        for start_page in range(0, total_pages, pages_per_file):
            end_page = min(start_page + pages_per_file, total_pages)

            output_filename = f"{base_name}_part_{file_count}.pdf"
            output_path = os.path.join(output_dir, output_filename)

            writer = PdfWriter()
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            output_files.append(output_path)
            file_count += 1

            if self.verbose:
                print(f"  ✅ Created: {output_filename} (pages {start_page + 1}-{end_page})")

        return output_files

    def _split_by_size(self, input_path: str, output_dir: str, max_size_mb: float) -> List[str]:
        """Split PDF by approximate file size."""
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        original_size = get_file_size_mb(input_path)

        if self.verbose:
            print(f"📄 Total pages: {total_pages}")
            print(f"📏 Original size: {original_size:.2f} MB")
            print(f"🎯 Target max size: {max_size_mb} MB")

        # Estimate pages per file based on size
        avg_mb_per_page = original_size / total_pages
        estimated_pages_per_file = max(1, int(max_size_mb / avg_mb_per_page))

        if self.verbose:
            print(f"📊 Estimated pages per file: {estimated_pages_per_file}")

        return self._split_by_fixed_pages(input_path, output_dir, estimated_pages_per_file)

    def _split_by_bookmarks(self, input_path: str, output_dir: str) -> List[str]:
        """Split PDF by bookmarks."""
        reader = PdfReader(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]

        if not reader.outline:
            raise DocForgeException("PDF has no bookmarks to split by")

        # Extract bookmark page numbers
        bookmarks = self._extract_bookmark_pages(reader)

        if not bookmarks:
            raise DocForgeException("Could not extract valid bookmark page numbers")

        if self.verbose:
            print(f"📑 Found {len(bookmarks)} bookmarks:")
            for title, page_num in bookmarks[:5]:  # Show first 5
                print(f"  '{title}' at page {page_num}")
            if len(bookmarks) > 5:
                print(f"  ... and {len(bookmarks) - 5} more")

        output_files = []
        total_pages = len(reader.pages)

        for i, (title, start_page) in enumerate(bookmarks):
            # Determine end page
            if i < len(bookmarks) - 1:
                end_page = bookmarks[i + 1][1] - 1
            else:
                end_page = total_pages

            # Sanitize bookmark title for filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            output_filename = f"{base_name}_{i + 1:02d}_{safe_title}.pdf"
            output_path = os.path.join(output_dir, output_filename)

            writer = PdfWriter()
            for page_num in range(start_page - 1, end_page):  # Convert to 0-indexed
                writer.add_page(reader.pages[page_num])

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            output_files.append(output_path)

            if self.verbose:
                print(f"  ✅ Created: {output_filename} (pages {start_page}-{end_page})")

        return output_files

    def _parse_page_ranges(self, page_ranges: str) -> List[Tuple[int, int]]:
        """Parse page ranges like '1-5,10-15,20'."""
        ranges = []
        for part in page_ranges.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                ranges.append((start, end))
            else:
                page = int(part)
                ranges.append((page, page))
        return ranges

    def _extract_bookmark_pages(self, reader: PdfReader) -> List[Tuple[str, int]]:
        """Extract bookmark titles and page numbers."""
        bookmarks = []

        def extract_from_outline(outline, level=0):
            for item in outline:
                if isinstance(item, list):
                    extract_from_outline(item, level + 1)
                else:
                    try:
                        title = item.title if hasattr(item, 'title') else str(item)
                        page = reader.get_destination_page_number(item) + 1
                        bookmarks.append((title, page))
                    except:
                        continue

        extract_from_outline(reader.outline)

        # Remove duplicates and sort by page number
        seen_pages = set()
        unique_bookmarks = []

        for title, page in sorted(bookmarks, key=lambda x: x[1]):
            if page not in seen_pages:
                unique_bookmarks.append((title, page))
                seen_pages.add(page)

        return unique_bookmarks

    def choose_split_method(self):
        """Interactive method selection for users."""
        print("✂️ PDF Split Methods")
        print("=" * 50)
        print("Choose your split method:")
        print()
        print("1. Split by Page Ranges")
        print("   - Extract specific page ranges")
        print("   - Best for: Extracting chapters, sections")
        print()
        print("2. Split by Fixed Page Count")
        print("   - Split into files with N pages each")
        print("   - Best for: Even distribution")
        print()
        print("3. Split by File Size")
        print("   - Split to keep files under size limit")
        print("   - Best for: Size-constrained sharing")
        print()
        print("4. Split by Bookmarks")
        print("   - Split at bookmark boundaries")
        print("   - Best for: Documents with proper bookmarks")
        print()

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            return self._run_page_ranges_split()
        elif choice == "2":
            return self._run_fixed_pages_split()
        elif choice == "3":
            return self._run_size_split()
        elif choice == "4":
            return self._run_bookmarks_split()
        else:
            print("❌ Invalid choice. Using page ranges split.")
            return self._run_page_ranges_split()

    def _run_page_ranges_split(self):
        """Run page ranges split with user input."""
        print("\n--- Split by Page Ranges ---")
        input_path = input("📁 Input PDF file: ").strip()
        output_dir = input("📁 Output directory: ").strip()
        print("📋 Example page ranges: '1-5,10-15' or '1-3,7,12-20'")
        page_ranges = input("📋 Page ranges: ").strip()

        return self.split_pdf_by_pages(input_path, output_dir, page_ranges)

    def _run_fixed_pages_split(self):
        """Run fixed pages split with user input."""
        print("\n--- Split by Fixed Page Count ---")
        input_path = input("📁 Input PDF file: ").strip()
        output_dir = input("📁 Output directory: ").strip()
        pages_per_file = int(input("📋 Pages per file: ").strip())

        return self.split_pdf(input_path, output_dir, split_type="pages", pages_per_file=pages_per_file)

    def _run_size_split(self):
        """Run size split with user input."""
        print("\n--- Split by File Size ---")
        input_path = input("📁 Input PDF file: ").strip()
        output_dir = input("📁 Output directory: ").strip()
        max_size_mb = float(input("📏 Maximum file size (MB): ").strip())

        return self.split_pdf_by_size(input_path, output_dir, max_size_mb)

    def _run_bookmarks_split(self):
        """Run bookmarks split with user input."""
        print("\n--- Split by Bookmarks ---")
        input_path = input("📁 Input PDF file: ").strip()
        output_dir = input("📁 Output directory: ").strip()

        return self.split_pdf_by_bookmarks(input_path, output_dir)

    def analyze_split_candidates(self, input_path: str):
        """Analyze PDF for splitting recommendations."""
        if not os.path.exists(input_path):
            print(f"❌ File not found: {input_path}")
            return

        try:
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            file_size = get_file_size_mb(input_path)

            print(f"📊 Split Analysis: {os.path.basename(input_path)}")
            print(f"📄 Total pages: {total_pages}")
            print(f"📏 File size: {file_size:.2f} MB")
            print(f"📊 Average MB per page: {file_size / total_pages:.3f}")

            # Check for bookmarks
            if reader.outline:
                bookmarks = self._extract_bookmark_pages(reader)
                print(f"📑 Bookmarks found: {len(bookmarks)}")
                print("💡 Recommendation: Split by bookmarks for logical sections")
            else:
                print("📑 No bookmarks found")

            # Size recommendations
            if file_size > 50:
                print("💡 Recommendation: Large file - consider splitting by size (10-20 MB chunks)")
            elif total_pages > 100:
                print("💡 Recommendation: Many pages - consider splitting by page count (20-50 pages)")
            else:
                print("💡 Recommendation: Moderate size - page ranges might be most appropriate")

        except Exception as e:
            print(f"❌ Error analyzing PDF: {str(e)}")


# Convenience functions for easy usage
def create_pdf_splitter(verbose=True):
    """Factory function to create PDF splitter instance."""
    return PDFSplitter(verbose=verbose)


def run_interactive_splitter():
    """Run the interactive PDF splitter."""
    splitter = create_pdf_splitter(verbose=True)

    if not splitter.has_dependencies:
        print("❌ PDF dependencies not installed. Run: pip install PyPDF2")
        return

    try:
        return splitter.choose_split_method()
    except KeyboardInterrupt:
        print("\n\n👋 PDF split cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")


# Example usage
if __name__ == "__main__":
    run_interactive_splitter()
