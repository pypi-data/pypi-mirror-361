"""
PDF OCR functionality using proven implementation.
Complete OCR processor with all features integrated.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import tempfile
import shutil
import gc
import time
import subprocess

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from PyPDF2 import PdfReader, PdfWriter

    HAS_OCR_DEPS = True
except ImportError as e:
    HAS_OCR_DEPS = False
    print(f"OCR dependencies not available: {e}")
    print("Install with: pip install pytesseract Pillow pdf2image reportlab PyPDF2")
    print("Also install poppler-utils (Linux/Mac) or poppler for Windows")
    print("And install Tesseract OCR from: https://github.com/tesseract-ocr/tesseract")

from ..core.base import BaseProcessor
from ..core.exceptions import OCRError


def get_file_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)


class PDFOCRProcessor(BaseProcessor):
    """Handles PDF OCR operations using proven implementation."""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.has_dependencies = HAS_OCR_DEPS

        if not self.has_dependencies:
            if hasattr(self, 'logger'):
                self.logger.warning("OCR dependencies not available. Install with: pip install pytesseract pdf2image")
            else:
                print("OCR dependencies not available. Install with: pip install pytesseract pdf2image")

    def process(self, input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Process PDF OCR."""
        return self.ocr_pdf(input_path, output_path, **kwargs)

    def check_tesseract(self) -> bool:
        """Check if Tesseract is installed and accessible."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            # Try common Windows installation paths
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
            ]

            for path in common_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    try:
                        pytesseract.get_tesseract_version()
                        if self.verbose:
                            print(f"Found Tesseract at: {path}")
                        return True
                    except Exception:
                        continue

            return False

    def move_with_retry(self, src, dst, max_retries=5):
        """Move file with retry logic for Windows file locking issues."""
        for attempt in range(max_retries):
            try:
                shutil.move(src, dst)
                return
            except PermissionError as e:
                if attempt < max_retries - 1:
                    if self.verbose:
                        print(f"File move attempt {attempt + 1} failed, retrying...")
                    if os.name == 'nt':
                        gc.collect()
                        time.sleep(0.2 * (attempt + 1))  # Increasing delay
                else:
                    raise e

    def process_images_batch(self, images, batch_start, language, layout_mode, progress_callback, total_pages):
        """Process a batch of images with OCR."""
        processed_pages = []

        for i, image in enumerate(images):
            page_num = batch_start + i + 1

            if progress_callback:
                progress_callback(page_num, total_pages)
            elif self.verbose:
                print(f"Processing page {page_num}/{total_pages}...")

            # Perform OCR directly on PIL Image object
            try:
                if layout_mode == 'precise':
                    # Use more detailed OCR configuration for better layout preservation
                    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
                    ocr_data = pytesseract.image_to_data(
                        image,
                        lang=language,
                        output_type=pytesseract.Output.DICT,
                        config=custom_config
                    )
                    text = pytesseract.image_to_string(image, lang=language, config=custom_config)
                else:
                    # Standard OCR
                    ocr_data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
                    text = pytesseract.image_to_string(image, lang=language)

                processed_pages.append({
                    'image': image,
                    'text': text,
                    'ocr_data': ocr_data,
                    'page_num': page_num
                })

                # Force garbage collection after each page on Windows
                if os.name == 'nt':
                    gc.collect()

            except Exception as e:
                if self.verbose:
                    print(f"Warning: OCR failed for page {page_num}: {e}")
                processed_pages.append({
                    'image': image,
                    'text': '',
                    'ocr_data': None,
                    'page_num': page_num
                })

        return processed_pages

    def add_invisible_text_overlay(self, canvas_obj, ocr_data, page_width, page_height, img_width, img_height):
        """Add invisible text overlay based on OCR bounding box data with precise positioning."""

        # Scale factors to convert image coordinates to PDF coordinates
        x_scale = page_width / img_width
        y_scale = page_height / img_height

        # Group text by confidence and word-level processing
        n_boxes = len(ocr_data['text'])

        # Process word-level OCR data for better layout preservation
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i]) if ocr_data['conf'][i] != '-1' else 0

            # Only process text with reasonable confidence
            if text and conf > 30:  # Confidence threshold
                # Get precise bounding box coordinates
                left = ocr_data['left'][i] * x_scale
                top = ocr_data['top'][i] * y_scale
                width = ocr_data['width'][i] * x_scale
                height = ocr_data['height'][i] * y_scale

                # Convert to PDF coordinate system (origin at bottom-left)
                x = left
                y = page_height - top - height

                # Calculate optimal font size to fit the bounding box
                # Use character width estimation for better fit
                char_width = width / len(text) if text else width
                font_size_by_height = height * 0.75  # 75% of box height
                font_size_by_width = char_width * 1.2  # Approximate character width
                font_size = min(font_size_by_height, font_size_by_width)
                font_size = max(font_size, 4)  # Minimum readable size
                font_size = min(font_size, 72)  # Maximum reasonable size

                # Set font and make text invisible by setting fill color to white with 0 alpha
                canvas_obj.setFont("Helvetica", font_size)
                canvas_obj.setFillColorRGB(1, 1, 1, alpha=0)  # Invisible white text

                # Position text precisely within the bounding box
                canvas_obj.drawString(x, y, text)

        # Reset fill color to black for any subsequent operations
        canvas_obj.setFillColorRGB(0, 0, 0, alpha=1)

    def add_precise_text_overlay(self, canvas_obj, ocr_data, page_width, page_height, img_width, img_height):
        """Add invisible text overlay with precise positioning for maximum layout accuracy."""

        # High precision scale factors
        x_scale = page_width / img_width
        y_scale = page_height / img_height

        # Group text by level (word, line, paragraph) for better structure
        n_boxes = len(ocr_data['text'])

        # Process each text element with precise positioning
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            level = ocr_data['level'][i]
            conf = int(ocr_data['conf'][i]) if ocr_data['conf'][i] != '-1' else 0

            # Only process word-level text with good confidence
            if text and level == 5 and conf > 40:  # Level 5 = word level
                # Get exact bounding box
                left = ocr_data['left'][i]
                top = ocr_data['top'][i]
                width = ocr_data['width'][i]
                height = ocr_data['height'][i]

                # Convert to PDF coordinates with high precision
                x = left * x_scale
                y = page_height - (top + height) * y_scale
                box_width = width * x_scale
                box_height = height * y_scale

                # Calculate optimal font size for perfect fit
                # Average character width estimation
                avg_char_width = box_width / len(text) if text else box_width

                # Font size based on both dimensions
                font_size_height = box_height * 0.8  # 80% of height
                font_size_width = avg_char_width * 1.5  # Character width factor

                # Use the smaller of the two to ensure text fits
                font_size = min(font_size_height, font_size_width)
                font_size = max(font_size, 2)  # Minimum size
                font_size = min(font_size, 100)  # Maximum size

                # Set font with calculated size and make text invisible
                canvas_obj.setFont("Helvetica", font_size)
                canvas_obj.setFillColorRGB(1, 1, 1, alpha=0)  # Invisible white text

                # Fine-tune position for better alignment
                # Adjust Y position to center text vertically in box
                y_offset = (box_height - font_size) / 2
                final_y = y + y_offset

                # Draw invisible text at precise location
                canvas_obj.drawString(x, final_y, text)

        # Reset fill color
        canvas_obj.setFillColorRGB(0, 0, 0, alpha=1)

    def create_searchable_pdf_with_images(self, processed_pages: List[dict], output_path: Path):
        """Create a PDF with original images as background and invisible text overlay."""

        temp_pdf_path = output_path.with_suffix('.temp.pdf')

        try:
            c = canvas.Canvas(str(temp_pdf_path))

            for page_data in processed_pages:
                image = page_data['image']
                text = page_data['text']
                ocr_data = page_data['ocr_data']

                # Set page size based on image dimensions
                img_width, img_height = image.size
                # Convert pixels to points (assuming 72 DPI for PDF)
                page_width = img_width * 72 / 300  # Adjust based on your DPI
                page_height = img_height * 72 / 300

                c.setPageSize((page_width, page_height))

                # Save image to temporary file with proper cleanup
                try:
                    # Create a temporary file in a controlled way
                    temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg', prefix='pdf_page_')

                    try:
                        # Convert to RGB if needed and save
                        if image.mode in ('RGBA', 'LA', 'P'):
                            # Convert transparent images to RGB with white background
                            background = Image.new('RGB', image.size, (255, 255, 255))
                            if image.mode == 'P':
                                image = image.convert('RGBA')
                            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                            save_image = background
                        else:
                            save_image = image

                        # Close the file descriptor first
                        os.close(temp_fd)

                        # Save the image
                        save_image.save(temp_path, format='JPEG', quality=95, optimize=True)

                        # Draw image from temp file
                        c.drawImage(temp_path, 0, 0, width=page_width, height=page_height)

                    finally:
                        # Clean up temp file
                        try:
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                        except:
                            pass  # Ignore cleanup errors

                except Exception as e:
                    if self.verbose:
                        print(f"Warning: Failed to add image for page {page_data['page_num']}: {e}")
                    # Continue without image if there's an issue

                # Add invisible text overlay if OCR data is available
                if ocr_data and text.strip():
                    self.add_invisible_text_overlay(c, ocr_data, page_width, page_height, img_width, img_height)

                c.showPage()

                # Force garbage collection to help with memory
                if os.name == 'nt':  # Windows
                    gc.collect()

            c.save()

            # Force garbage collection before moving file
            if os.name == 'nt':
                gc.collect()
                time.sleep(0.1)

            # Move temp file to final location with retry on Windows
            self.move_with_retry(str(temp_pdf_path), str(output_path))

        except Exception as e:
            if temp_pdf_path.exists():
                try:
                    temp_pdf_path.unlink()
                except:
                    pass  # Ignore cleanup errors
            raise e

    def create_precision_layout_pdf(self, processed_pages: List[dict], output_path: Path):
        """Create a PDF with precise layout preservation using advanced text positioning."""

        temp_pdf_path = output_path.with_suffix('.temp.pdf')

        try:
            c = canvas.Canvas(str(temp_pdf_path))

            for page_data in processed_pages:
                image = page_data['image']
                text = page_data['text']
                ocr_data = page_data['ocr_data']

                # Set page size based on image dimensions with proper scaling
                img_width, img_height = image.size
                # Use a more precise conversion factor
                conversion_factor = 72.0 / 300.0  # 72 points per inch, 300 DPI
                page_width = img_width * conversion_factor
                page_height = img_height * conversion_factor

                c.setPageSize((page_width, page_height))

                # Save image to temporary file with proper cleanup
                try:
                    # Create a temporary file in a controlled way
                    temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg', prefix='pdf_page_')

                    try:
                        # Convert to RGB if needed and save
                        if image.mode in ('RGBA', 'LA', 'P'):
                            # Convert transparent images to RGB with white background
                            background = Image.new('RGB', image.size, (255, 255, 255))
                            if image.mode == 'P':
                                image = image.convert('RGBA')
                            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                            save_image = background
                        else:
                            save_image = image

                        # Close the file descriptor first
                        os.close(temp_fd)

                        # Save the image
                        save_image.save(temp_path, format='JPEG', quality=95, optimize=True)

                        # Draw image from temp file with precise positioning
                        c.drawImage(temp_path, 0, 0, width=page_width, height=page_height)

                    finally:
                        # Clean up temp file
                        try:
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                        except:
                            pass  # Ignore cleanup errors

                except Exception as e:
                    if self.verbose:
                        print(f"Warning: Failed to add image for page {page_data['page_num']}: {e}")

                # Add precise text overlay if OCR data is available
                if ocr_data and text.strip():
                    self.add_precise_text_overlay(c, ocr_data, page_width, page_height, img_width, img_height)

                c.showPage()

            c.save()

            # Move temp file to final location with retry
            self.move_with_retry(str(temp_pdf_path), str(output_path))

        except Exception as e:
            if temp_pdf_path.exists():
                try:
                    temp_pdf_path.unlink()
                except:
                    pass
            raise e

    def create_text_only_pdf(self, processed_pages: List[dict], output_path: Path):
        """Create a text-only PDF without images."""

        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        for page_data in processed_pages:
            text = page_data['text']
            page_num = page_data['page_num']

            # Add page header
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 50, f"Page {page_num}")

            # Add text content
            c.setFont("Helvetica", 10)

            # Simple text wrapping
            lines = text.split('\n')
            y_position = height - 80

            for line in lines:
                if y_position < 50:  # Start new page if needed
                    c.showPage()
                    y_position = height - 50

                # Simple line wrapping
                words = line.split()
                current_line = ""

                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if len(test_line) > 80:  # Approximate character limit
                        if current_line:
                            c.drawString(50, y_position, current_line)
                            y_position -= 15
                        current_line = word
                    else:
                        current_line = test_line

                if current_line:
                    c.drawString(50, y_position, current_line)
                    y_position -= 15

            c.showPage()

        c.save()

    def ocr_pdf(self, input_path: str, output_path: str,
                language: str = 'eng', dpi: int = 300,
                preserve_images: bool = True,
                layout_mode: str = 'standard',
                progress_callback: Optional[Callable] = None,
                **kwargs) -> Dict[str, Any]:
        """
        Convert a scanned PDF to searchable PDF using OCR.

        Args:
            input_path (str): Path to the input scanned PDF
            output_path (str): Path for the output searchable PDF
            language (str): Tesseract language code (default: 'eng')
            dpi (int): DPI for image conversion (higher = better quality, slower)
            preserve_images (bool): Whether to preserve original images in output
            layout_mode (str): Layout preservation mode ('precise', 'standard', 'text_only')
            progress_callback (callable): Optional callback function for progress updates

        Returns:
            Dict[str, Any]: Processing results
        """

        if not self.has_dependencies:
            raise OCRError(
                "OCR dependencies not installed. Run: pip install pytesseract pdf2image reportlab PyPDF2")

        if not self.check_tesseract():
            raise OCRError(
                "Tesseract OCR is not installed or not in PATH. Install from: https://github.com/tesseract-ocr/tesseract")

        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise OCRError(f"Input file not found: {input_path}")

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if self.verbose:
                print(f"🔍 Converting scanned PDF to searchable PDF...")
                print(f"📂 Input: {input_path}")
                print(f"📁 Output: {output_path}")
                print(f"🌐 Language: {language}, 📐 DPI: {dpi}, 📋 Layout mode: {layout_mode}")

            original_size = get_file_size_mb(input_path)

            # Convert PDF pages to images and process one by one to avoid temp file buildup
            if self.verbose:
                print("🖼️ Converting PDF pages to images...")

            # Process pages in smaller batches to avoid temp file accumulation
            batch_size = 3  # Process 3 pages at a time
            all_processed_pages = []

            # Get total page count first
            try:
                # Quick check for total pages without loading all images
                result = subprocess.run(['pdfinfo', str(input_path)], capture_output=True, text=True, timeout=30)
                total_pages = 0
                for line in result.stdout.split('\n'):
                    if line.startswith('Pages:'):
                        total_pages = int(line.split(':')[1].strip())
                        break
                if total_pages == 0:
                    raise Exception("Could not determine page count")
            except:
                # Fallback: convert all at once if pdfinfo fails
                if self.verbose:
                    print("📊 Using fallback method for page counting...")
                images = convert_from_path(str(input_path), dpi=dpi)
                total_pages = len(images)
                # Process these images immediately
                all_processed_pages.extend(
                    self.process_images_batch(images, 0, language, layout_mode, progress_callback, total_pages))
                del images
                gc.collect()
            else:
                # Process in batches
                if self.verbose:
                    print(f"📄 Found {total_pages} pages - processing in batches of {batch_size}")

                for batch_start in range(0, total_pages, batch_size):
                    batch_end = min(batch_start + batch_size, total_pages)
                    if self.verbose:
                        print(f"🔄 Processing pages {batch_start + 1}-{batch_end}...")

                    # Convert only this batch of pages
                    images = convert_from_path(
                        str(input_path),
                        dpi=dpi,
                        first_page=batch_start + 1,
                        last_page=batch_end
                    )

                    # Process this batch
                    batch_processed = self.process_images_batch(
                        images, batch_start, language, layout_mode, progress_callback, total_pages
                    )
                    all_processed_pages.extend(batch_processed)

                    # Cleanup this batch
                    del images
                    del batch_processed

                    # Force cleanup and wait for Windows
                    if os.name == 'nt':
                        gc.collect()
                        time.sleep(0.5)

            # Final cleanup before PDF creation
            if os.name == 'nt':
                gc.collect()
                time.sleep(1.0)

            # Create searchable PDF
            if self.verbose:
                print("📝 Creating searchable PDF...")

            if preserve_images:
                if layout_mode == 'precise':
                    self.create_precision_layout_pdf(all_processed_pages, output_path)
                else:
                    self.create_searchable_pdf_with_images(all_processed_pages, output_path)
            else:
                self.create_text_only_pdf(all_processed_pages, output_path)

            final_size = get_file_size_mb(output_path)

            if self.verbose:
                print(f"✅ Successfully created searchable PDF: {output_path}")
                print(f"📏 Original: {original_size:.2f} MB → Final: {final_size:.2f} MB")

            return {
                'success': True,
                'method': 'proven_implementation',
                'language': language,
                'dpi': dpi,
                'layout_mode': layout_mode,
                'preserve_images': preserve_images,
                'pages_processed': total_pages,
                'original_size_mb': original_size,
                'final_size_mb': final_size,
                'input_path': str(input_path),
                'output_path': str(output_path)
            }

        except Exception as e:
            raise OCRError(f"Failed to process PDF OCR: {str(e)}")

    def batch_ocr_pdfs(self, input_folder: str, output_folder: str, **kwargs) -> Dict[str, Any]:
        """Batch OCR processing with comprehensive options."""
        input_dir = Path(input_folder)
        output_dir = Path(output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_files = list(input_dir.glob("*.pdf"))

        if not pdf_files:
            if self.verbose:
                print(f"❌ No PDF files found in {input_folder}")
            return {'processed': 0, 'failed': 0, 'files': []}

        if self.verbose:
            print(f"📁 Found {len(pdf_files)} PDF files to process")
            print(f"📂 Output folder: {output_folder}")

        results = {
            'processed': 0,
            'failed': 0,
            'total_original_size': 0,
            'total_final_size': 0,
            'files': []
        }

        for i, pdf_file in enumerate(pdf_files, 1):
            output_file = output_dir / f"{pdf_file.stem}_searchable.pdf"

            if self.verbose:
                print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_file.name}")

            try:
                result = self.ocr_pdf(str(pdf_file), str(output_file), **kwargs)
                results['processed'] += 1
                results['total_original_size'] += result.get('original_size_mb', 0)
                results['total_final_size'] += result.get('final_size_mb', 0)
                results['files'].append({'file': pdf_file.name, 'result': result})

                if self.verbose:
                    print(f"✅ Success: {result.get('pages_processed', 0)} pages processed")

            except Exception as e:
                results['failed'] += 1
                results['files'].append({'file': pdf_file.name, 'error': str(e)})

                if self.verbose:
                    print(f"❌ Error: {str(e)}")

        if self.verbose:
            print(f"\n🎉 Batch processing complete:")
            print(f"✅ Successful: {results['processed']}")
            print(f"❌ Failed: {results['failed']}")
            if results['processed'] > 0:
                print(f"📏 Total size: {results['total_original_size']:.2f} MB → {results['total_final_size']:.2f} MB")

        return results

    def choose_ocr_method(self):
        """Interactive method selection for users."""
        print("🔍 PDF OCR Methods")
        print("=" * 50)
        print("Choose your OCR processing method:")
        print()
        print("1. Standard OCR")
        print("   - Good quality text recognition")
        print("   - Preserves original images")
        print("   - Best for: Most documents")
        print()
        print("2. Precise Layout OCR")
        print("   - Maximum layout preservation")
        print("   - Best text positioning")
        print("   - Best for: Complex layouts, forms")
        print()
        print("3. Text-Only OCR")
        print("   - Extract text without images")
        print("   - Smaller file size")
        print("   - Best for: Text documents only")
        print()
        print("4. Batch OCR Processing")
        print("   - Process multiple PDFs")
        print("   - Various options available")
        print()

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            return self._run_standard_ocr()
        elif choice == "2":
            return self._run_precise_ocr()
        elif choice == "3":
            return self._run_text_only_ocr()
        elif choice == "4":
            return self._choose_batch_ocr_method()
        else:
            print("❌ Invalid choice. Using standard OCR.")
            return self._run_standard_ocr()

    def _run_standard_ocr(self):
        """Run standard OCR with user input."""
        input_path = input("📁 Enter input PDF path: ").strip()
        output_path = input("📁 Enter output PDF path: ").strip()

        language = input("🌐 Language code (default 'eng'): ").strip() or 'eng'

        try:
            dpi = int(input("📐 DPI (default 300): ") or "300")
        except ValueError:
            dpi = 300

        return self.ocr_pdf(input_path, output_path, language=language, dpi=dpi, layout_mode='standard')

    def _run_precise_ocr(self):
        """Run precise layout OCR with user input."""
        input_path = input("📁 Enter input PDF path: ").strip()
        output_path = input("📁 Enter output PDF path: ").strip()

        language = input("🌐 Language code (default 'eng'): ").strip() or 'eng'

        try:
            dpi = int(input("📐 DPI (default 300): ") or "300")
        except ValueError:
            dpi = 300

        return self.ocr_pdf(input_path, output_path, language=language, dpi=dpi, layout_mode='precise')

    def _run_text_only_ocr(self):
        """Run text-only OCR with user input."""
        input_path = input("📁 Enter input PDF path: ").strip()
        output_path = input("📁 Enter output PDF path: ").strip()

        language = input("🌐 Language code (default 'eng'): ").strip() or 'eng'

        try:
            dpi = int(input("📐 DPI (default 300): ") or "300")
        except ValueError:
            dpi = 300

        return self.ocr_pdf(input_path, output_path, language=language, dpi=dpi,
                            preserve_images=False, layout_mode='text_only')

    def _choose_batch_ocr_method(self):
        """Choose between different batch OCR methods."""
        print("\n🔍 Batch OCR Options")
        print("=" * 40)
        print("1. Standard Batch OCR")
        print("2. Precise Layout Batch OCR")
        print("3. Text-Only Batch OCR")
        print("4. Custom Batch Settings")
        print()

        choice = input("Choose batch method (1-4): ").strip()

        if choice == "1":
            return self._run_standard_batch_ocr()
        elif choice == "2":
            return self._run_precise_batch_ocr()
        elif choice == "3":
            return self._run_text_only_batch_ocr()
        elif choice == "4":
            return self._run_custom_batch_ocr()
        else:
            print("❌ Invalid choice. Using standard batch OCR.")
            return self._run_standard_batch_ocr()

    def _run_standard_batch_ocr(self):
        """Run standard batch OCR."""
        input_folder = input("📁 Enter input folder path: ").strip()
        output_folder = input("📁 Enter output folder path: ").strip()

        language = input("🌐 Language code (default 'eng'): ").strip() or 'eng'

        return self.batch_ocr_pdfs(input_folder, output_folder, language=language, layout_mode='standard')

    def _run_precise_batch_ocr(self):
        """Run precise layout batch OCR."""
        input_folder = input("📁 Enter input folder path: ").strip()
        output_folder = input("📁 Enter output folder path: ").strip()

        language = input("🌐 Language code (default 'eng'): ").strip() or 'eng'

        return self.batch_ocr_pdfs(input_folder, output_folder, language=language, layout_mode='precise')

    def _run_text_only_batch_ocr(self):
        """Run text-only batch OCR."""
        input_folder = input("📁 Enter input folder path: ").strip()
        output_folder = input("📁 Enter output folder path: ").strip()

        language = input("🌐 Language code (default 'eng'): ").strip() or 'eng'

        return self.batch_ocr_pdfs(input_folder, output_folder, language=language,
                                   preserve_images=False, layout_mode='text_only')

    def _run_custom_batch_ocr(self):
        """Run custom batch OCR with full customization."""
        print("🔍 Custom Batch OCR Settings")
        print("=" * 40)

        input_folder = input("📁 Enter input folder path: ").strip()
        output_folder = input("📁 Enter output folder path: ").strip()

        language = input("🌐 Language code (default 'eng'): ").strip() or 'eng'

        print("\n📋 Choose layout mode:")
        print("1. Standard (good balance)")
        print("2. Precise (best layout preservation)")
        print("3. Text only (no images)")

        mode_choice = input("Choose mode (1-3): ").strip()
        mode_map = {"1": "standard", "2": "precise", "3": "text_only"}
        layout_mode = mode_map.get(mode_choice, "standard")

        preserve_images = layout_mode != "text_only"

        try:
            dpi = int(input("📐 DPI (default 300): ") or "300")
        except ValueError:
            dpi = 300

        return self.batch_ocr_pdfs(
            input_folder, output_folder,
            language=language,
            dpi=dpi,
            layout_mode=layout_mode,
            preserve_images=preserve_images
        )

    def analyze_pdf_for_ocr(self, input_path: str):
        """Analyze PDF to help determine best OCR strategy."""
        if not self.has_dependencies:
            print("❌ OCR dependencies not available")
            return

        input_path = Path(input_path)
        if not input_path.exists():
            print(f"❌ File not found: {input_path}")
            return

        try:
            print(f"📊 PDF OCR Analysis: {input_path.name}")
            print(f"📏 File size: {get_file_size_mb(input_path):.2f} MB")

            # Quick conversion of first page to analyze
            print("🔍 Analyzing first page...")
            images = convert_from_path(str(input_path), dpi=150, first_page=1, last_page=1)

            if images:
                first_image = images[0]
                img_width, img_height = first_image.size

                print(f"📐 Page dimensions: {img_width} x {img_height} pixels")
                print(f"📏 Aspect ratio: {img_width / img_height:.2f}")

                # Try quick OCR to see if text is detected
                try:
                    sample_text = pytesseract.image_to_string(first_image, lang='eng')
                    text_length = len(sample_text.strip())

                    print(f"📝 Text detected: {text_length} characters")

                    if text_length > 50:
                        print("✅ Good text content detected - OCR recommended")
                        print("💡 Suggested: Standard or Precise layout mode")
                    elif text_length > 10:
                        print("⚠️ Some text detected - may need higher DPI")
                        print("💡 Suggested: Try DPI 400-600")
                    else:
                        print("❌ Little or no text detected")
                        print("💡 Check if this is a text document or try different language")

                    # Show sample of detected text
                    if text_length > 0:
                        sample = sample_text.strip()[:100]
                        print(f"📄 Sample text: '{sample}{'...' if len(sample) == 100 else ''}'")

                except Exception as e:
                    print(f"⚠️ OCR test failed: {e}")

                del images
                gc.collect()

        except Exception as e:
            print(f"❌ Analysis failed: {e}")


# Convenience functions for easy usage
def create_ocr_processor(verbose=True):
    """Factory function to create OCR processor instance."""
    return PDFOCRProcessor(verbose=verbose)


def run_interactive_ocr():
    """Run the interactive OCR processor."""
    processor = create_ocr_processor(verbose=True)

    if not processor.has_dependencies:
        print("❌ OCR dependencies not installed.")
        print("Install with: pip install pytesseract Pillow pdf2image reportlab PyPDF2")
        return

    try:
        return processor.choose_ocr_method()
    except KeyboardInterrupt:
        print("\n\n👋 OCR processing cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")


# Example usage
if __name__ == "__main__":
    run_interactive_ocr()