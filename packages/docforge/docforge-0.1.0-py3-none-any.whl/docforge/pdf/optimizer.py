"""
PDF optimization functionality using proven implementation.
This is where your proven optimization code will be integrated.
"""

import os
from pathlib import Path
from typing import Dict, Any

try:
    import fitz  # PyMuPDF

    HAS_PDF_DEPS = True
except ImportError:
    HAS_PDF_DEPS = False
    print("PDF dependencies not available. Install with: pip install PyMuPDF")

from ..core.base import BaseProcessor
from ..core.exceptions import OptimizationError


def get_file_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)


class PDFOptimizer(BaseProcessor):
    """Handles PDF optimization operations using proven implementation."""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.has_dependencies = HAS_PDF_DEPS

    def process(self, input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """Process PDF optimization."""
        return self.optimize_pdf(input_path, output_path, **kwargs)

    def optimize_pdf(self, input_path: str, output_path: str,
                     target_dpi: int = 150, jpeg_quality: int = 70,
                     optimization_type: str = 'standard', **kwargs) -> Dict[str, Any]:
        """Optimize a single PDF file with complete implementation."""

        if not self.has_dependencies:
            raise OptimizationError("PDF dependencies not installed. Run: pip install PyMuPDF")

        try:
            self.validate_input(input_path)

            original_size = get_file_size_mb(input_path)

            if self.verbose:
                print(f"🗜️ Optimizing: {input_path} -> {output_path}")
                print(f"   Type: {optimization_type}, DPI: {target_dpi}, Quality: {jpeg_quality}%")

            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Actual optimization implementation based on type
            if optimization_type == 'aggressive':
                self._optimize_aggressive(input_path, output_path, target_dpi, jpeg_quality)
            elif optimization_type == 'scanned':
                self._optimize_scanned_pdf(input_path, output_path, target_dpi, jpeg_quality)
            elif optimization_type == 'scale_only':
                self._scale_pdf_pages(input_path, output_path, target_dpi, jpeg_quality)
            elif optimization_type == 'high_quality':
                self._optimize_high_quality(input_path, output_path, target_dpi, jpeg_quality)
            else:  # standard
                self._optimize_standard(input_path, output_path, target_dpi, jpeg_quality)

            final_size = get_file_size_mb(output_path)
            compression_ratio = (original_size - final_size) / original_size * 100 if original_size > 0 else 0

            if self.verbose:
                print(f"✅ Optimization completed!")
                print(f"📏 {original_size:.2f} MB → {final_size:.2f} MB")
                print(f"💾 Size reduction: {compression_ratio:.1f}%")

            return {
                'success': True,
                'original_size_mb': original_size,
                'final_size_mb': final_size,
                'compression_ratio': compression_ratio,
                'optimization_type': optimization_type
            }

        except Exception as e:
            raise OptimizationError(f"Failed to optimize PDF: {str(e)}")

    def _optimize_standard(self, input_path: str, output_path: str, target_dpi: int, jpeg_quality: int):
        """Standard optimization with moderate compression."""
        doc = fitz.open(input_path)

        # Apply standard optimizations
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Compress images if they exist
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                try:
                    # Extract and recompress image
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    if image_ext.lower() in ['jpg', 'jpeg', 'png']:
                        # Create new compressed version
                        pix = fitz.Pixmap(image_bytes)
                        if pix.n - pix.alpha < 4:  # Not CMYK
                            compressed_bytes = pix.tobytes("jpeg", jpeg_quality)
                            # Replace image in document
                            doc._replace_image(xref, compressed_bytes)
                        pix = None
                except:
                    continue

        # Save with compression options
        doc.save(output_path, garbage=4, clean=True, deflate=True,
                 deflate_images=True, deflate_fonts=True)
        doc.close()

    def _optimize_aggressive(self, input_path: str, output_path: str, target_dpi: int, jpeg_quality: int):
        """Aggressive optimization with maximum compression."""
        self.optimize_scanned_pdf_aggressive(input_path, output_path, target_dpi, jpeg_quality)

    def _optimize_scanned_pdf(self, input_path: str, output_path: str, target_dpi: int, jpeg_quality: int):
        """Optimize scanned PDFs."""
        self.optimize_scanned_pdf(input_path, output_path, target_dpi, jpeg_quality)

    def _scale_pdf_pages(self, input_path: str, output_path: str, target_dpi: int, jpeg_quality: int):
        """Scale PDF pages only."""
        self.scale_pdf_pages(input_path, output_path, compression_quality=jpeg_quality, image_dpi=target_dpi)

    def _optimize_high_quality(self, input_path: str, output_path: str, target_dpi: int, jpeg_quality: int):
        """High quality optimization."""
        self.scale_pdf_to_letter_high_quality(input_path, output_path, quality_mode="high", jpeg_quality=jpeg_quality)

    def choose_optimization_method(self):
        """Interactive method selection for users."""
        print("🔧 PDF Optimization Methods")
        print("=" * 50)
        print("Choose your optimization method:")
        print()
        print("1. Standard Optimization")
        print("   - Moderate compression")
        print("   - Good balance of size/quality")
        print("   - Best for: Mixed content PDFs")
        print()
        print("2. Aggressive Optimization")
        print("   - Maximum compression")
        print("   - Smaller file size")
        print("   - Best for: File size is priority")
        print()
        print("3. Scanned PDF Optimization")
        print("   - Optimized for scanned documents")
        print("   - Image-focused compression")
        print("   - Best for: Scanned papers/books")
        print()
        print("4. Page Scaling Only")
        print("   - Scale oversized pages to standard")
        print("   - Minimal quality loss")
        print("   - Best for: Oversized pages")
        print()
        print("5. High Quality Optimization")
        print("   - Preserve maximum quality")
        print("   - Larger file size")
        print("   - Best for: Important documents")
        print()
        print("6. Batch Processing Options")
        print("   - Multiple batch processing methods")
        print()

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            return self._run_standard_optimization()
        elif choice == "2":
            return self._run_aggressive_optimization()
        elif choice == "3":
            return self._run_scanned_optimization()
        elif choice == "4":
            return self._run_scaling_optimization()
        elif choice == "5":
            return self._run_high_quality_optimization()
        elif choice == "6":
            return self._choose_batch_method()
        else:
            print("❌ Invalid choice. Using standard optimization.")
            return self._run_standard_optimization()

    def _run_standard_optimization(self):
        """Run standard optimization with user input."""
        input_path = input("📁 Enter input PDF path: ").strip()
        output_path = input("📁 Enter output PDF path: ").strip()

        try:
            dpi = int(input("🎯 Target DPI (default 150): ") or "150")
            quality = int(input("🗜️ JPEG quality % (default 70): ") or "70")
        except ValueError:
            dpi, quality = 150, 70

        return self.optimize_pdf(input_path, output_path, target_dpi=dpi,
                                 jpeg_quality=quality, optimization_type='standard')

    def _run_aggressive_optimization(self):
        """Run aggressive optimization with user input."""
        input_path = input("📁 Enter input PDF path: ").strip()
        output_path = input("📁 Enter output PDF path: ").strip()

        try:
            dpi = int(input("🎯 Target DPI (default 100): ") or "100")
            quality = int(input("🗜️ JPEG quality % (default 60): ") or "60")
        except ValueError:
            dpi, quality = 100, 60

        return self.optimize_pdf(input_path, output_path, target_dpi=dpi,
                                 jpeg_quality=quality, optimization_type='aggressive')

    def _run_scanned_optimization(self):
        """Run scanned PDF optimization with user input."""
        input_path = input("📁 Enter input PDF path: ").strip()
        output_path = input("📁 Enter output PDF path: ").strip()

        try:
            dpi = int(input("🎯 Target DPI (default 150): ") or "150")
            quality = int(input("🗜️ JPEG quality % (default 70): ") or "70")
        except ValueError:
            dpi, quality = 150, 70

        return self.optimize_pdf(input_path, output_path, target_dpi=dpi,
                                 jpeg_quality=quality, optimization_type='scanned')

    def _run_scaling_optimization(self):
        """Run page scaling optimization with user input."""
        input_path = input("📁 Enter input PDF path: ").strip()
        output_path = input("📁 Enter output PDF path: ").strip()

        return self.optimize_pdf(input_path, output_path, optimization_type='scale_only')

    def _run_high_quality_optimization(self):
        """Run high quality optimization with user input."""
        input_path = input("📁 Enter input PDF path: ").strip()
        output_path = input("📁 Enter output PDF path: ").strip()

        try:
            quality = int(input("🗜️ JPEG quality % (default 85): ") or "85")
        except ValueError:
            quality = 85

        return self.optimize_pdf(input_path, output_path, jpeg_quality=quality,
                                 optimization_type='high_quality')

    def _choose_batch_method(self):
        """Choose between different batch processing methods."""
        print("\n🔧 Batch Processing Options")
        print("=" * 40)
        print("1. Standard Batch Optimization")
        print("2. Advanced Batch with Quality Options")
        print("3. Batch Scale PDFs to Standard Size")
        print("4. Interactive Batch with Custom Settings")
        print()

        choice = input("Choose batch method (1-4): ").strip()

        if choice == "1":
            return self._run_standard_batch()
        elif choice == "2":
            return self._run_advanced_batch()
        elif choice == "3":
            return self._run_batch_scaling()
        elif choice == "4":
            return self.batch_optimize_interactive()
        else:
            print("❌ Invalid choice. Using standard batch.")
            return self._run_standard_batch()

    def _run_standard_batch(self):
        """Run standard batch optimization."""
        input_folder = input("📁 Enter input folder path: ").strip()
        output_folder = input("📁 Enter output folder path: ").strip()

        return self.batch_optimize_standard(input_folder, output_folder)

    def _run_advanced_batch(self):
        """Run advanced batch optimization."""
        input_folder = input("📁 Enter input folder path: ").strip()
        output_folder = input("📁 Enter output folder path: ").strip()

        print("\n🎯 Choose optimization level:")
        print("1. Standard (150 DPI, 70% quality)")
        print("2. Aggressive (100 DPI, 60% quality)")
        print("3. High Quality (200 DPI, 85% quality)")

        level_choice = input("Choose level (1-3): ").strip()

        if level_choice == "2":
            return self.batch_optimize_advanced(input_folder, output_folder, "aggressive")
        elif level_choice == "3":
            return self.batch_optimize_advanced(input_folder, output_folder, "high_quality", 200, 85)
        else:
            return self.batch_optimize_advanced(input_folder, output_folder, "standard")

    def _run_batch_scaling(self):
        """Run batch scaling optimization."""
        input_folder = input("📁 Enter input folder path: ").strip()

        print("\n📏 Choose target size:")
        print("1. A4 (595 x 842 points)")
        print("2. Letter (612 x 792 points)")
        print("3. Legal (612 x 1008 points)")

        size_choice = input("Choose size (1-3): ").strip()
        size_map = {"1": "A4", "2": "Letter", "3": "Legal"}
        target_size = size_map.get(size_choice, "A4")

        return self.batch_scale_pdfs(input_folder, target_size)

    def batch_optimize_standard(self, input_folder: str, output_folder: str) -> Dict[str, Any]:
        """Standard batch optimization - renamed from original batch_optimize_pdfs."""
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        pdf_files = list(input_path.glob("*.pdf"))

        results = {
            'processed': 0,
            'failed': 0,
            'total_original_size': 0,
            'total_final_size': 0,
            'files': []
        }

        for pdf_file in pdf_files:
            try:
                output_file = output_path / f"{pdf_file.stem}_optimized.pdf"
                result = self.optimize_pdf(str(pdf_file), str(output_file), optimization_type='standard')

                results['processed'] += 1
                results['total_original_size'] += result['original_size_mb']
                results['total_final_size'] += result['final_size_mb']
                results['files'].append({
                    'file': pdf_file.name,
                    'result': result
                })

            except Exception as e:
                results['failed'] += 1
                results['files'].append({
                    'file': pdf_file.name,
                    'error': str(e)
                })

        return results

    def batch_optimize_advanced(self, input_folder: str, output_folder: str,
                                optimization_type: str = "standard",
                                target_dpi: int = 150, jpeg_quality: int = 70,
                                max_file_size_mb: int = 100) -> Dict[str, Any]:
        """Advanced batch optimize with more options."""
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        pdf_files = list(input_path.glob("*.pdf"))

        if not pdf_files:
            print(f"❌ No PDF files found in {input_folder}")
            return {'processed': 0, 'failed': 0, 'files': []}

        print(f"🔧 Advanced Batch PDF Optimization")
        print(f"📁 Input folder: {input_folder}")
        print(f"📁 Output folder: {output_folder}")
        print(f"📄 Found {len(pdf_files)} PDF files")
        print(f"🎯 Type: {optimization_type}")
        print(f"🗜️ DPI: {target_dpi}, Quality: {jpeg_quality}%")
        print("=" * 80)

        results = {
            'processed': 0,
            'failed': 0,
            'total_original_size': 0,
            'total_final_size': 0,
            'files': []
        }

        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_file.name}")

            file_size = get_file_size_mb(pdf_file)
            print(f"📏 File size: {file_size:.2f} MB")

            if file_size > max_file_size_mb:
                print(f"⏭️ Skipping - too large ({file_size:.2f} MB > {max_file_size_mb} MB)")
                results['failed'] += 1
                continue

            output_filename = f"{pdf_file.stem}_optimized.pdf"
            output_file_path = output_path / output_filename

            try:
                result = self.optimize_pdf(
                    str(pdf_file),
                    str(output_file_path),
                    target_dpi=target_dpi,
                    jpeg_quality=jpeg_quality,
                    optimization_type=optimization_type
                )

                results['processed'] += 1
                results['total_original_size'] += result['original_size_mb']
                results['total_final_size'] += result['final_size_mb']
                results['files'].append({
                    'file': pdf_file.name,
                    'result': result
                })

            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results['failed'] += 1
                results['files'].append({
                    'file': pdf_file.name,
                    'error': str(e)
                })

        # Final report
        if results['processed'] > 0:
            total_reduction = ((results['total_original_size'] - results['total_final_size']) /
                               results['total_original_size']) * 100
            print(f"\n✅ Batch completed!")
            print(f"📊 Processed: {results['processed']}, Failed: {results['failed']}")
            print(f"📏 {results['total_original_size']:.2f} MB → {results['total_final_size']:.2f} MB")
            print(f"💾 Total reduction: {total_reduction:.1f}%")

        return results

    def batch_optimize_interactive(self):
        """Interactive batch optimization with full customization."""
        print("🔧 Interactive Batch PDF Optimizer")
        print("=" * 50)

        input_folder = input("📁 Enter input folder path: ").strip()
        if not Path(input_folder).exists():
            print(f"❌ Input folder not found: {input_folder}")
            return

        output_folder = input("📁 Enter output folder path: ").strip()

        print("\n🎯 Choose optimization type:")
        print("1. Standard (balanced)")
        print("2. Aggressive (maximum compression)")
        print("3. High Quality (preserve quality)")
        print("4. Scanned PDF optimized")
        print("5. Scale pages only")

        opt_choice = input("Enter choice (1-5): ").strip()
        opt_map = {
            "1": "standard",
            "2": "aggressive",
            "3": "high_quality",
            "4": "scanned",
            "5": "scale_only"
        }
        optimization_type = opt_map.get(opt_choice, "standard")

        try:
            dpi = int(input("🎯 Target DPI (default 150): ") or "150")
            quality = int(input("🗜️ JPEG quality % (default 70): ") or "70")
            max_size = int(input("📏 Max file size MB to process (default 100): ") or "100")
        except ValueError:
            dpi, quality, max_size = 150, 70, 100

        return self.batch_optimize_advanced(
            input_folder, output_folder, optimization_type, dpi, quality, max_size
        )

    # Keep all the existing specialized methods with fixed self. references
    def scale_pdf_pages(self, input_pdf_path, output_pdf_path,
                        target_width=595, target_height=842,
                        compression_quality=70, image_dpi=150):
        """Scale down large PDF pages to normal size and optimize file size"""
        print(f"📂 Processing: {input_pdf_path}")
        print(f"🎯 Target size: {target_width} x {target_height} points")
        print(f"🗜️ Compression quality: {compression_quality}%")
        print(f"📐 Image DPI: {image_dpi}")

        input_doc = fitz.open(input_pdf_path)
        output_doc = fitz.open()

        original_size = get_file_size_mb(input_pdf_path)
        total_pages = len(input_doc)

        print(f"📄 Total pages: {total_pages}")
        print(f"📏 Original size: {original_size:.2f} MB")

        pages_scaled = 0

        for page_num in range(total_pages):
            page = input_doc.load_page(page_num)
            original_rect = page.rect

            print(f"📄 Page {page_num + 1}: {original_rect.width:.0f} x {original_rect.height:.0f} points", end="")

            if original_rect.width > target_width or original_rect.height > target_height:
                scale_x = target_width / original_rect.width
                scale_y = target_height / original_rect.height
                scale_factor = min(scale_x, scale_y)

                matrix = fitz.Matrix(scale_factor, scale_factor)
                new_rect = fitz.Rect(0, 0, target_width, target_height)
                new_page = output_doc.new_page(width=target_width, height=target_height)

                pix = page.get_pixmap(matrix=matrix, alpha=False)
                new_page.insert_image(new_rect, pixmap=pix)

                pages_scaled += 1
                print(f" → Scaled to {target_width:.0f} x {target_height:.0f} (factor: {scale_factor:.3f})")
            else:
                output_doc.insert_pdf(input_doc, from_page=page_num, to_page=page_num)
                print(" → No scaling needed")

        print(f"\n💾 Saving optimized PDF...")
        output_doc.save(
            output_pdf_path,
            garbage=4, clean=True, deflate=True,
            deflate_images=True, deflate_fonts=True,
        )

        input_doc.close()
        output_doc.close()

        final_size = get_file_size_mb(output_pdf_path)
        size_reduction = ((original_size - final_size) / original_size) * 100

        print(f"\n✅ Optimization completed!")
        print(f"📄 Pages scaled: {pages_scaled}/{total_pages}")
        print(f"📏 Original size: {original_size:.2f} MB")
        print(f"📉 Final size: {final_size:.2f} MB")
        print(f"💾 Size reduction: {size_reduction:.1f}%")

    def scale_to_standard_sizes(self, input_pdf_path, output_folder=None, page_size="A4"):
        """Scale PDF to standard page sizes"""
        page_sizes = {
            "A4": (595, 842),
            "Letter": (612, 792),
            "Legal": (612, 1008),
            "A3": (842, 1191),
            "Tabloid": (792, 1224),
        }

        if page_size not in page_sizes:
            print(f"❌ Unknown page size: {page_size}")
            print(f"Available sizes: {list(page_sizes.keys())}")
            return

        target_width, target_height = page_sizes[page_size]

        input_path = Path(input_pdf_path)
        if output_folder is None:
            output_folder = input_path.parent
        else:
            output_folder = Path(output_folder)
            output_folder.mkdir(exist_ok=True)

        output_filename = f"{input_path.stem}_scaled_{page_size}.pdf"
        output_path = output_folder / output_filename

        print(f"🎯 Scaling to {page_size} size ({target_width} x {target_height} points)")

        self.scale_pdf_pages(
            input_pdf_path=str(input_path),
            output_pdf_path=str(output_path),
            target_width=target_width,
            target_height=target_height
        )

    def analyze_pdf_pages(self, input_pdf_path):
        """Analyze PDF page sizes to help decide scaling strategy"""
        doc = fitz.open(input_pdf_path)
        total_pages = len(doc)

        print(f"📊 PDF Page Analysis: {Path(input_pdf_path).name}")
        print(f"📄 Total pages: {total_pages}")
        print(f"📏 File size: {get_file_size_mb(input_pdf_path):.2f} MB")
        print("\nPage sizes found:")

        page_sizes = {}
        large_pages = 0

        for page_num in range(min(total_pages, 10)):
            page = doc.load_page(page_num)
            rect = page.rect
            size_key = f"{rect.width:.0f} x {rect.height:.0f}"

            if size_key not in page_sizes:
                page_sizes[size_key] = 0
            page_sizes[size_key] += 1

            if rect.width > 595 or rect.height > 842:
                large_pages += 1

            print(f"  Page {page_num + 1}: {rect.width:.0f} x {rect.height:.0f} points")

        if total_pages > 10:
            print(f"  ... (showing first 10 of {total_pages} pages)")

        print(f"\n📐 Standard page sizes for reference:")
        print(f"  A4: 595 x 842 points")
        print(f"  Letter: 612 x 792 points")
        print(f"  Legal: 612 x 1008 points")

        if large_pages > 0:
            print(f"\n⚠️ Found {large_pages} oversized pages that should be scaled")
        else:
            print(f"\n✅ All pages appear to be standard size")

        doc.close()

    def batch_scale_pdfs(self, input_folder, target_size="A4", max_input_size_mb=50):
        """Batch scale multiple PDFs in a folder"""
        input_path = Path(input_folder)
        pdf_files = list(input_path.glob("*.pdf"))

        if not pdf_files:
            print(f"❌ No PDF files found in {input_folder}")
            return

        output_folder = input_path / "scaled_pdfs"
        output_folder.mkdir(exist_ok=True)

        print(f"📁 Found {len(pdf_files)} PDF files")
        print(f"🎯 Target size: {target_size}")
        print(f"📁 Output folder: {output_folder}")

        processed = 0
        skipped = 0

        for pdf_file in pdf_files:
            file_size = get_file_size_mb(pdf_file)

            print(f"\n{'=' * 60}")
            print(f"Processing: {pdf_file.name} ({file_size:.2f} MB)")

            if file_size > max_input_size_mb:
                print(f"⏭️ File too large ({file_size:.2f} MB > {max_input_size_mb} MB) - skipping")
                skipped += 1
                continue

            try:
                self.scale_to_standard_sizes(
                    str(pdf_file),
                    str(output_folder),
                    target_size
                )
                processed += 1
            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {e}")
                skipped += 1

        print(f"\n🎉 Batch processing completed!")
        print(f"✅ Processed: {processed}")
        print(f"⏭️ Skipped: {skipped}")

    def optimize_scanned_pdf(self, input_pdf_path, output_pdf_path,
                             target_dpi=150, jpeg_quality=70):
        """Optimize scanned PDFs by reducing image resolution and compression"""
        print(f"🔧 Optimizing scanned PDF: {input_pdf_path}")
        print(f"🎯 Target DPI: {target_dpi}")
        print(f"🗜️ JPEG quality: {jpeg_quality}%")

        output_dir = Path(output_pdf_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        input_doc = fitz.open(input_pdf_path)
        output_doc = fitz.open()

        for page_num in range(len(input_doc)):
            page = input_doc.load_page(page_num)
            print(f"📄 Processing page {page_num + 1}/{len(input_doc)}")

            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height

            print(f"   Original page size: {page_width:.0f} x {page_height:.0f} points")

            image_list = page.get_images()
            needs_optimization = False

            if image_list:
                for img in image_list:
                    try:
                        xref = img[0]
                        base_image = input_doc.extract_image(xref)
                        img_width = base_image["width"]
                        img_height = base_image["height"]

                        if img_width > target_dpi * 8.5 or img_height > target_dpi * 11:
                            needs_optimization = True
                            print(f"   Found high-res image: {img_width} x {img_height}")
                            break
                    except:
                        continue

            if needs_optimization:
                print(f"   Rendering page at {target_dpi} DPI...")

                scale_factor = target_dpi / 72.0
                matrix = fitz.Matrix(scale_factor, scale_factor)

                pix = page.get_pixmap(matrix=matrix, alpha=False)
                new_width = page_width * scale_factor
                new_height = page_height * scale_factor

                print(f"   Scaled page size: {new_width:.0f} x {new_height:.0f} points")

                new_page = output_doc.new_page(width=new_width, height=new_height)
                img_data = pix.tobytes("jpeg", jpeg_quality)
                img_rect = fitz.Rect(0, 0, new_width, new_height)
                new_page.insert_image(img_rect, stream=img_data)

                pix = None
                print(f"   ✅ Page optimized and compressed")
            else:
                print(f"   ℹ️ Page doesn't need optimization, copying as-is")
                output_doc.insert_pdf(input_doc, from_page=page_num, to_page=page_num)

        print("💾 Saving optimized PDF...")

        output_doc.save(
            output_pdf_path,
            garbage=4, clean=True, deflate=True,
            deflate_images=True, deflate_fonts=True,
            linear=True, pretty=False
        )

        input_doc.close()
        output_doc.close()

        original_size = get_file_size_mb(input_pdf_path)
        final_size = get_file_size_mb(output_pdf_path)
        reduction = ((original_size - final_size) / original_size) * 100

        print(f"✅ Optimization completed!")
        print(f"📏 Original: {original_size:.2f} MB → Final: {final_size:.2f} MB")
        print(f"💾 Size reduction: {reduction:.1f}%")

    def optimize_scanned_pdf_aggressive(self, input_pdf_path, output_pdf_path,
                                        target_dpi=100, jpeg_quality=60):
        """More aggressive optimization for heavily scanned PDFs"""
        print(f"🔧 Aggressive PDF optimization: {input_pdf_path}")
        print(f"🎯 Target DPI: {target_dpi} (aggressive)")
        print(f"🗜️ JPEG quality: {jpeg_quality}% (aggressive)")

        output_dir = Path(output_pdf_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        input_doc = fitz.open(input_pdf_path)
        output_doc = fitz.open()

        for page_num in range(len(input_doc)):
            page = input_doc.load_page(page_num)
            print(f"📄 Processing page {page_num + 1}/{len(input_doc)}")

            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height

            print(f"   Original page size: {page_width:.0f} x {page_height:.0f} points")

            scale_factor = target_dpi / 72.0
            matrix = fitz.Matrix(scale_factor, scale_factor)

            pix = page.get_pixmap(matrix=matrix, alpha=False)

            new_width = page_width * scale_factor
            new_height = page_height * scale_factor

            print(f"   Scaled page size: {new_width:.0f} x {new_height:.0f} points")

            new_page = output_doc.new_page(width=new_width, height=new_height)
            img_data = pix.tobytes("jpeg", jpeg_quality)
            img_rect = fitz.Rect(0, 0, new_width, new_height)
            new_page.insert_image(img_rect, stream=img_data)

            pix = None
            print(f"   ✅ Page compressed to {target_dpi} DPI")

        print("💾 Saving aggressively optimized PDF...")

        output_doc.save(
            output_pdf_path,
            garbage=4, clean=True, deflate=True,
            deflate_images=True, deflate_fonts=True,
            linear=True, pretty=False
        )

        input_doc.close()
        output_doc.close()

        original_size = get_file_size_mb(input_pdf_path)
        final_size = get_file_size_mb(output_pdf_path)
        reduction = ((original_size - final_size) / original_size) * 100

        print(f"✅ Aggressive optimization completed!")
        print(f"📏 Original: {original_size:.2f} MB → Final: {final_size:.2f} MB")
        print(f"💾 Size reduction: {reduction:.1f}%")

    def scale_pdf_to_letter_high_quality(self, input_pdf_path, output_pdf_path,
                                         quality_mode="high", jpeg_quality=85):
        """Scale oversized PDF pages down to Letter size with better quality preservation"""
        print(f"🔧 High-Quality scaling to Letter size: {input_pdf_path}")
        print(f"🎯 Target: Letter (612 x 792 points)")
        print(f"🏆 Quality mode: {quality_mode}")
        print(f"🗜️ JPEG quality: {jpeg_quality}%")

        LETTER_WIDTH = 612
        LETTER_HEIGHT = 792

        quality_settings = {
            "high": {
                "render_scale": 2.0,
                "jpeg_quality": 90,
                "use_png": True
            },
            "medium": {
                "render_scale": 1.5,
                "jpeg_quality": 80,
                "use_png": False
            },
            "balanced": {
                "render_scale": 1.0,
                "jpeg_quality": 75,
                "use_png": False
            }
        }

        settings = quality_settings.get(quality_mode, quality_settings["high"])
        render_scale = settings["render_scale"]
        final_jpeg_quality = settings.get("jpeg_quality", jpeg_quality)
        use_png = settings.get("use_png", False)

        output_dir = Path(output_pdf_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        input_doc = fitz.open(input_pdf_path)
        output_doc = fitz.open()

        for page_num in range(len(input_doc)):
            page = input_doc.load_page(page_num)
            print(f"📄 Processing page {page_num + 1}/{len(input_doc)}")

            page_rect = page.rect
            original_width = page_rect.width
            original_height = page_rect.height

            print(f"   Original: {original_width:.0f} x {original_height:.0f} points")

            scale_x = LETTER_WIDTH / original_width
            scale_y = LETTER_HEIGHT / original_height
            page_scale_factor = min(scale_x, scale_y)

            final_width = original_width * page_scale_factor
            final_height = original_height * page_scale_factor

            print(f"   Page scale: {page_scale_factor:.3f}")
            print(f"   Final size: {final_width:.0f} x {final_height:.0f} points")

            total_scale = page_scale_factor * render_scale
            matrix = fitz.Matrix(total_scale, total_scale)

            print(f"   Rendering at {render_scale}x scale for quality")

            pix = page.get_pixmap(matrix=matrix, alpha=False)
            new_page = output_doc.new_page(width=final_width, height=final_height)

            image_list = page.get_images()
            text_blocks = page.get_text("blocks")

            has_much_text = len(text_blocks) > 5
            has_images = len(image_list) > 0

            if use_png and has_much_text and not has_images:
                img_data = pix.tobytes("png")
                print(f"   Using PNG format for text preservation")
            else:
                img_data = pix.tobytes("jpeg", final_jpeg_quality)
                print(f"   Using JPEG {final_jpeg_quality}% quality")

            img_rect = fitz.Rect(0, 0, final_width, final_height)
            new_page.insert_image(img_rect, stream=img_data)

            pix = None
            print(f"   ✅ Page processed with {quality_mode} quality")

        print("💾 Saving high-quality PDF...")

        output_doc.save(
            output_pdf_path,
            garbage=4, clean=True, deflate=True,
            deflate_images=True, deflate_fonts=True,
            linear=True, pretty=False
        )

        input_doc.close()
        output_doc.close()

        original_size = get_file_size_mb(input_pdf_path)
        final_size = get_file_size_mb(output_pdf_path)
        reduction = ((original_size - final_size) / original_size) * 100

        print(f"✅ High-quality scaling completed!")
        print(f"📏 Original: {original_size:.2f} MB → Final: {final_size:.2f} MB")
        print(f"💾 Size reduction: {reduction:.1f}%")


# Example usage and convenience functions
def create_pdf_optimizer(verbose=True):
    """Factory function to create PDF optimizer instance."""
    return PDFOptimizer(verbose=verbose)


def run_interactive_optimizer():
    """Run the interactive PDF optimizer."""
    optimizer = create_pdf_optimizer(verbose=True)

    if not optimizer.has_dependencies:
        print("❌ PyMuPDF not installed. Run: pip install PyMuPDF")
        return

    try:
        return optimizer.choose_optimization_method()
    except KeyboardInterrupt:
        print("\n\n👋 Optimization cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")


if __name__ == "__main__":
    run_interactive_optimizer()