# docforge/cli/validation_ui.py
"""
Rich UI components for enhanced validation display
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich.prompt import Confirm, Prompt
from rich import box
from typing import Dict, List, Any, Optional
import time
from pathlib import Path

from .rich_interface import DocForgeUI


class ValidationUI:
    """Rich UI for displaying validation results and suggestions."""

    def __init__(self, ui: DocForgeUI):
        self.ui = ui
        self.console = ui.console

    def display_pdf_analysis(self, metadata: Dict[str, Any], file_path: str):
        """Display comprehensive PDF analysis."""

        # File info section
        file_info = [
            f"📄 File: [cyan]{Path(file_path).name}[/cyan]",
            f"📏 Size: [yellow]{self._format_size(metadata.get('file_size', 0))}[/yellow]",
            f"📑 Pages: [blue]{metadata.get('page_count', 0)}[/blue]"
        ]

        # Content analysis
        content_info = []
        if metadata.get('has_text'):
            content_info.append("📝 [green]✅ Contains extractable text[/green]")
        else:
            content_info.append("📝 [red]❌ No extractable text (likely scanned)[/red]")

        if metadata.get('has_images'):
            content_info.append("🖼️  [green]✅ Contains images[/green]")
        else:
            content_info.append("🖼️  [dim]❌ No images detected[/dim]")

        if metadata.get('is_encrypted'):
            content_info.append("🔒 [red]❌ Password protected[/red]")
        else:
            content_info.append("🔒 [green]✅ Not password protected[/green]")

        # Estimates
        estimates = []
        if metadata.get('estimated_ocr_time'):
            estimates.append(f"⏱️  OCR time: [yellow]~{metadata['estimated_ocr_time']:.0f}s[/yellow]")

        if metadata.get('estimated_optimization_savings'):
            savings = metadata['estimated_optimization_savings'] * 100
            estimates.append(f"🗜️  Optimization potential: [yellow]~{savings:.0f}%[/yellow]")

        # Combine all sections
        content_parts = file_info + [""] + content_info
        if estimates:
            content_parts += [""] + estimates

        panel = Panel(
            "\n".join(content_parts),
            title="📊 PDF Analysis",
            border_style="blue",
            title_align="left"
        )

        self.console.print(panel)

    def display_validation_suggestions(self, suggestions: List[str], title: str = "💡 Suggestions"):
        """Display validation suggestions in a clean format."""

        if not suggestions:
            return

        content = []
        for i, suggestion in enumerate(suggestions, 1):
            content.append(f"[green]{i}.[/green] {suggestion}")

        panel = Panel(
            "\n".join(content),
            title=title,
            border_style="green",
            title_align="left"
        )

        self.console.print(panel)

    def display_batch_analysis(self, analysis: Dict[str, Any]):
        """Display comprehensive batch operation analysis."""

        # Summary statistics
        stats_table = Table(box=box.SIMPLE)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow")

        stats_table.add_row("Total Files", str(analysis['total_files']))
        stats_table.add_row("Accessible Files", str(analysis['accessible_files']))
        stats_table.add_row("Total Size", self._format_size(analysis['total_size']))

        if analysis.get('estimated_processing_time'):
            time_str = self._format_time(analysis['estimated_processing_time'])
            stats_table.add_row("Estimated Time", time_str)

        # File analysis table (show first few files)
        file_table = Table(title="📁 File Analysis (Sample)", box=box.ROUNDED)
        file_table.add_column("File", style="cyan", no_wrap=True, max_width=30)
        file_table.add_column("Size", justify="right", style="yellow")
        file_table.add_column("Pages", justify="center", style="blue")
        file_table.add_column("Est. Time", justify="right", style="green")
        file_table.add_column("Status", justify="center")

        file_analysis = analysis.get('file_analysis', [])
        for file_info in file_analysis[:10]:  # Show first 10 files
            filename = Path(file_info['file']).name
            size = self._format_size(file_info['size'])
            pages = str(file_info.get('pages', '?'))
            est_time = f"{file_info.get('estimated_time', 0):.1f}s"

            if file_info.get('accessible', True):
                status = "[green]✅[/green]"
            else:
                status = "[red]❌[/red]"

            file_table.add_row(filename, size, pages, est_time, status)

        if len(file_analysis) > 10:
            file_table.add_row(
                f"... +{len(file_analysis) - 10} more",
                "", "", "", ""
            )

        # Display in columns
        stats_panel = Panel(stats_table, title="📊 Batch Summary", border_style="blue")

        self.console.print(stats_panel)
        self.console.print(file_table)

        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            self.display_validation_suggestions(recommendations, "💡 Batch Recommendations")

    def display_dry_run_preview(self, preview: Dict[str, Any]):
        """Display dry-run operation preview."""

        operation = preview['operation'].upper()

        # Operation info
        info_content = [
            f"🔧 Operation: [bold cyan]{operation}[/bold cyan]",
            f"📥 Input: [yellow]{Path(preview['input_path']).name}[/yellow]",
            f"📤 Output: [yellow]{Path(preview['output_path']).name}[/yellow]"
        ]

        if preview.get('estimated_time'):
            time_str = self._format_time(preview['estimated_time'])
            info_content.append(f"⏱️  Estimated time: [blue]{time_str}[/blue]")

        if preview.get('estimated_output_size'):
            size_str = self._format_size(preview['estimated_output_size'])
            info_content.append(f"📏 Estimated output size: [magenta]{size_str}[/magenta]")

        info_panel = Panel(
            "\n".join(info_content),
            title="🔍 Operation Preview",
            border_style="blue"
        )

        self.console.print(info_panel)

        # Files that will be created/overwritten
        if preview.get('will_create_files') or preview.get('will_overwrite_files'):
            file_changes = []

            for file_path in preview.get('will_create_files', []):
                file_changes.append(f"[green]✨ Create:[/green] {Path(file_path).name}")

            for file_path in preview.get('will_overwrite_files', []):
                file_changes.append(f"[yellow]⚠️  Overwrite:[/yellow] {Path(file_path).name}")

            if file_changes:
                changes_panel = Panel(
                    "\n".join(file_changes),
                    title="📝 File Changes",
                    border_style="yellow"
                )
                self.console.print(changes_panel)

        # Warnings
        warnings = preview.get('warnings', [])
        if warnings:
            warning_content = []
            for warning in warnings:
                warning_content.append(f"⚠️  {warning}")

            warning_panel = Panel(
                "\n".join(warning_content),
                title="⚠️ Warnings",
                border_style="red"
            )
            self.console.print(warning_panel)

        # Recommendations
        recommendations = preview.get('recommendations', [])
        if recommendations:
            self.display_validation_suggestions(recommendations, "💡 Recommendations")

    def display_similar_files(self, original_file: str, similar_files: List[str]):
        """Display similar files when original is not found."""

        if not similar_files:
            return

        self.console.print(f"\n[yellow]🔍 Similar files found for '[cyan]{original_file}[/cyan]':[/yellow]")

        for i, file_path in enumerate(similar_files, 1):
            filename = Path(file_path).name
            self.console.print(f"  [green]{i}.[/green] {filename}")

        self.console.print()

    def prompt_file_selection(self, similar_files: List[str], original_file: str) -> Optional[str]:
        """Prompt user to select from similar files."""

        if not similar_files:
            return None

        self.display_similar_files(original_file, similar_files)

        choices = [str(i) for i in range(1, len(similar_files) + 1)] + ['n', 'no']

        choice = Prompt.ask(
            f"Select a file to use instead (1-{len(similar_files)}) or 'n' to cancel",
            choices=choices,
            default='n'
        )

        if choice in ['n', 'no']:
            return None

        try:
            index = int(choice) - 1
            return similar_files[index]
        except (ValueError, IndexError):
            return None

    def confirm_operation_with_warnings(self, operation: str, warnings: List[str]) -> bool:
        """Confirm operation when warnings are present."""

        if not warnings:
            return True

        self.console.print(f"\n[yellow]⚠️  Warnings for {operation} operation:[/yellow]")
        for warning in warnings:
            self.console.print(f"  • {warning}")

        return Confirm.ask(f"\nProceed with {operation} operation despite warnings?")

    def display_parameter_correction(self, original_value: str, corrected_value: str,
                                     parameter_name: str):
        """Display parameter auto-correction."""

        correction_text = f"✨ Auto-corrected [yellow]{parameter_name}[/yellow]: " \
                          f"'[red]{original_value}[/red]' → '[green]{corrected_value}[/green]'"

        panel = Panel(
            correction_text,
            title="🔧 Parameter Correction",
            border_style="green"
        )

        self.console.print(panel)

    def display_validation_progress(self, files: List[str], description: str = "Validating files"):
        """Display progress for file validation."""

        class ValidationProgress:
            def __init__(self, ui_console, total_files):
                self.console = ui_console
                self.total_files = total_files
                self.progress = None
                self.task_id = None

            def __enter__(self):
                self.progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=self.console
                )
                self.progress.start()
                self.task_id = self.progress.add_task(
                    f"[cyan]{description}...", total=self.total_files
                )
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.progress:
                    self.progress.stop()

            def update(self, filename: str):
                if self.progress and self.task_id is not None:
                    self.progress.update(
                        self.task_id,
                        advance=1,
                        description=f"[cyan]Validating: {Path(filename).name}..."
                    )

        return ValidationProgress(self.console, len(files))

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _format_time(self, seconds: float) -> str:
        """Format time in human-readable format."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds / 60:.1f}m"
        else:
            return f"{seconds / 3600:.1f}h"


class SmartValidationMixin:
    """Mixin for CLI interface to add smart validation capabilities."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_ui = ValidationUI(self.ui) if hasattr(self, 'ui') and self.ui else None

    def smart_validate_file(self, file_path: str, operation: str = None) -> Dict[str, Any]:
        """
        Perform smart file validation with Rich UI display.

        Args:
            file_path: Path to file to validate
            operation: Operation type for context-specific validation

        Returns:
            Dict with validation results and metadata
        """
        from ..core.validators import SmartFileValidator

        try:
            # Basic file validation
            validated_path = SmartFileValidator.validate_input_file(file_path, ['.pdf'])

            # PDF content analysis
            self.print_message("Analyzing PDF content...", "info")
            metadata = SmartFileValidator.validate_pdf_content(validated_path)

            # Display analysis if UI available
            if self.validation_ui:
                self.validation_ui.display_pdf_analysis(metadata, str(validated_path))

            # Operation-specific validation
            if operation == 'ocr' and metadata.get('has_text'):
                warning = "PDF already contains extractable text - OCR may not be necessary"
                self.print_message(warning, "warning")

                if self.validation_ui:
                    if not self.validation_ui.confirm_operation_with_warnings('OCR', [warning]):
                        raise ValidationError(
                            'user_choice', 'cancelled', 'user confirmation',
                            ['Choose a different operation or confirm OCR is needed']
                        )

            return {
                'validated_path': str(validated_path),
                'metadata': metadata,
                'success': True
            }

        except FileNotFoundError as e:
            # Try to find similar files
            similar_files = SmartFileValidator.suggest_similar_files(file_path)

            if similar_files and self.validation_ui:
                selected_file = self.validation_ui.prompt_file_selection(similar_files, file_path)
                if selected_file:
                    self.print_message(f"Using selected file: {selected_file}", "info")
                    return self.smart_validate_file(selected_file, operation)

            raise e

    def smart_validate_parameters(self, args) -> Dict[str, Any]:
        """
        Perform smart parameter validation with auto-correction.

        Args:
            args: Parsed command line arguments

        Returns:
            Dict with validated and possibly corrected parameters
        """
        from ..core.validators import SmartParameterValidator

        corrections = {}

        # Language validation with auto-correction
        if hasattr(args, 'language') and args.language:
            try:
                validated_lang, suggestions = SmartParameterValidator.validate_and_suggest_language(args.language)

                if validated_lang != args.language:
                    # Auto-correction occurred
                    if self.validation_ui:
                        self.validation_ui.display_parameter_correction(
                            args.language, validated_lang, 'language'
                        )
                    corrections['language'] = validated_lang
                    args.language = validated_lang

            except ValidationError as e:
                if self.validation_ui:
                    self.validation_ui.display_validation_suggestions(e.suggestions, "Language Suggestions")
                raise e

        # Quality validation
        if hasattr(args, 'quality') and args.quality:
            SmartParameterValidator.validate_quality(args.quality)

        # Page range validation (will be validated against actual PDF later)
        if hasattr(args, 'pages') and args.pages:
            SmartParameterValidator.validate_page_range(args.pages)

        return corrections

    def preview_operation(self, operation: str, args) -> bool:
        """
        Show operation preview and get user confirmation.

        Args:
            operation: Operation type
            args: Command arguments

        Returns:
            True if user confirms, False otherwise
        """
        from ..core.validators import DryRunValidator

        if not self.validation_ui:
            return True  # Skip preview if no Rich UI

        try:
            # Generate preview
            preview = DryRunValidator.preview_operation(
                operation=operation,
                input_path=args.input,
                output_path=args.output,
                **{k: v for k, v in vars(args).items() if k not in ['input', 'output']}
            )

            # Display preview
            self.validation_ui.display_dry_run_preview(preview)

            # Get confirmation if there are warnings or overwriting files
            warnings = preview.get('warnings', [])
            will_overwrite = preview.get('will_overwrite_files', [])

            if warnings or will_overwrite:
                all_warnings = warnings + [f"Will overwrite: {f}" for f in will_overwrite]
                return self.validation_ui.confirm_operation_with_warnings(operation, all_warnings)

            return True

        except Exception as e:
            self.print_message(f"Preview failed: {str(e)}", "warning")
            return True  # Continue with operation if preview fails
