# docforge/cli/rich_interface.py - Enhanced with beautiful error display

"""
Enhanced Rich CLI interface with comprehensive error display
"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich import box
from typing import List, Dict, Any, Optional
import time
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console

# Import our error handling system
from ..core.exceptions import DocForgeException, ProcessingResult

# Initialize Rich console
console = Console()


class DocForgeUI:
    """Enhanced Rich UI manager with comprehensive error handling."""

    def __init__(self) -> None:
        self.console: Console = Console()

    def print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"✅ [bold green]{message}[/bold green]")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"❌ [bold red]Error:[/bold red] {message}")

    def print_banner(self):
        """Display DocForge banner."""
        banner = """[bold blue]
╔══════════════════════════════════════════════════════════════╗
║                          DocForge 🔨                         ║
║        Forge perfect documents with precision & power        ║
╚══════════════════════════════════════════════════════════════╝[/bold blue]"""
        self.console.print(Panel(banner.strip(), border_style="blue"))

    def print_warning(self, message: str):
        """Print warning message."""
        self.console.print(f"⚠️  [bold yellow]Warning:[/bold yellow] {message}")

    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"ℹ️  [bold blue]Info:[/bold blue] {message}")

    def display_error_details(self, error: 'DocForgeException') -> None:
        """Display comprehensive error information with suggestions."""

        # Error header
        error_text = Text()
        error_text.append("❌ Error: ", style="bold red")
        error_text.append(error.message, style="red")

        # Create main error panel content
        content_parts = []

        # Error code and type
        if error.error_code:
            content_parts.append(f"[dim]Error Code:[/dim] [yellow]{error.error_code}[/yellow]")

        # Context information
        if error.context:
            content_parts.append("\n[bold cyan]Details:[/bold cyan]")
            for key, value in error.context.items():
                if key == 'file_path':
                    content_parts.append(f"  [dim]File:[/dim] {value}")
                elif key == 'file_exists':
                    status = "✅ exists" if value else "❌ not found"
                    content_parts.append(f"  [dim]File Status:[/dim] {status}")
                elif key == 'current_directory':
                    content_parts.append(f"  [dim]Working Directory:[/dim] {value}")
                elif 'size' in key.lower():
                    formatted_size = self._format_file_size(value) if isinstance(value, int) else value
                    content_parts.append(f"  [dim]{key.replace('_', ' ').title()}:[/dim] {formatted_size}")
                else:
                    content_parts.append(f"  [dim]{key.replace('_', ' ').title()}:[/dim] {value}")

        # Suggestions
        if error.suggestions:
            content_parts.append("\n[bold green]💡 How to fix this:[/bold green]")
            for i, suggestion in enumerate(error.suggestions, 1):
                content_parts.append(f"  [green]{i}.[/green] {suggestion}")

        # Create the error panel
        error_panel = Panel(
            "\n".join(content_parts),
            title="🚨 Error Details",
            border_style="red",
            title_align="left"
        )

        self.console.print(error_panel)

    def display_processing_result(self, result: ProcessingResult):
        """Display a comprehensive processing result."""

        if result.success:
            # Success display
            self.print_success(result.message)

            # Show processing time if available
            if result.processing_time:
                self.print_info(f"Completed in {result.processing_time:.2f} seconds")

            # Show output file info
            if result.output_file:
                self.print_info(f"Output saved to: {result.output_file}")

            # Show warnings if any
            if result.warnings:
                self.print_warning(f"Completed with {len(result.warnings)} warning(s):")
                for warning in result.warnings:
                    self.console.print(f"  ⚠️  {warning}")

            # Show metadata if available
            if result.metadata:
                self._display_metadata(result.metadata)

        else:
            # Error display
            if result.error:
                self.display_error_details(result.error)
            else:
                self.print_error(result.message)

            # Show partial results if available
            if result.processing_time:
                self.print_info(f"Failed after {result.processing_time:.2f} seconds")

    def _display_metadata(self, metadata: Dict[str, Any]):
        """Display metadata in a nice format."""
        if not metadata:
            return

        # Filter out internal/boring metadata
        display_metadata = {}
        for key, value in metadata.items():
            if key not in ['_internal', '_debug'] and value is not None:
                display_metadata[key] = value

        if display_metadata:
            content = []
            for key, value in display_metadata.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (int, float)) and 'size' in key.lower():
                    value = self._format_file_size(value)
                content.append(f"• [bold]{formatted_key}:[/bold] [cyan]{value}[/cyan]")

            if content:
                panel = Panel(
                    "\n".join(content),
                    title="📊 Processing Details",
                    border_style="blue"
                )
                self.console.print(panel)

    def display_validation_error(self, field: str, value: Any, expected: str, suggestions: List[str]):
        """Display validation error with helpful context."""

        content_parts = [
            f"[red]Invalid value for {field}[/red]",
            f"[dim]Got:[/dim] [yellow]{repr(value)}[/yellow]",
            f"[dim]Expected:[/dim] [green]{expected}[/green]"
        ]

        if suggestions:
            content_parts.append("\n[bold green]💡 How to fix this:[/bold green]")
            for i, suggestion in enumerate(suggestions, 1):
                content_parts.append(f"  [green]{i}.[/green] {suggestion}")

        error_panel = Panel(
            "\n".join(content_parts),
            title="❌ Validation Error",
            border_style="red"
        )

        self.console.print(error_panel)

    def display_file_not_found_help(self, file_path: str, context: Dict[str, Any]):
        """Display helpful information for file not found errors."""

        content_parts = [
            f"[red]Cannot find file:[/red] [yellow]{file_path}[/yellow]"
        ]

        # Check if it's a path issue
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            content_parts.append(f"\n[dim]Directory doesn't exist:[/dim] {parent_dir}")

        # Show current directory context
        if 'current_directory' in context:
            content_parts.append(f"\n[dim]Current directory:[/dim] {context['current_directory']}")

        # Show similar files if any
        if os.path.dirname(file_path):
            similar_files = self._find_similar_files(file_path)
            if similar_files:
                content_parts.append(f"\n[bold cyan]📁 Similar files found:[/bold cyan]")
                for similar_file in similar_files[:5]:  # Limit to 5 suggestions
                    content_parts.append(f"  • {similar_file}")

        # Suggestions
        suggestions = [
            "Check the file path spelling",
            "Use an absolute path instead of relative",
            "Ensure the file exists in the specified location",
            "Check file permissions"
        ]

        content_parts.append("\n[bold green]💡 Suggestions:[/bold green]")
        for i, suggestion in enumerate(suggestions, 1):
            content_parts.append(f"  [green]{i}.[/green] {suggestion}")

        error_panel = Panel(
            "\n".join(content_parts),
            title="📁 File Not Found",
            border_style="red"
        )

        self.console.print(error_panel)

    def _find_similar_files(self, file_path: str, max_suggestions: int = 5) -> List[str]:
        """Find files with similar names in the directory."""
        try:
            directory = os.path.dirname(file_path) or "."
            filename = os.path.basename(file_path)

            if not os.path.exists(directory):
                return []

            similar_files = []
            for file in os.listdir(directory):
                if file.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
                    # Simple similarity check
                    if (filename.lower() in file.lower() or
                            file.lower() in filename.lower() or
                            self._files_similar(filename, file)):
                        similar_files.append(os.path.join(directory, file))

            return similar_files[:max_suggestions]
        except:
            return []

    def _files_similar(self, file1: str, file2: str) -> bool:
        """Simple similarity check for filenames."""
        # Remove extensions and compare
        name1 = os.path.splitext(file1)[0].lower()
        name2 = os.path.splitext(file2)[0].lower()

        # Check if they share common words or are similar length
        words1 = set(name1.replace('_', ' ').replace('-', ' ').split())
        words2 = set(name2.replace('_', ' ').replace('-', ' ').split())

        return len(words1.intersection(words2)) > 0

    def create_progress_bar(self, description: str = "Processing..."):
        """Create a rich progress bar."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        )

    def display_results_table(self,
                              results: List[Dict[str, Any]],
                              title: str = "Processing Results") -> None:
        """Display processing results in a formatted table."""
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Size", justify="right", style="magenta")
        table.add_column("Time", justify="right", style="blue")
        table.add_column("Output", style="green")

        for result in results:
            # Handle both old dict format and new ProcessingResult format
            if isinstance(result, ProcessingResult):
                success = result.success
                input_file = result.input_file or "Unknown"
                output_file = result.output_file or "N/A"
                processing_time = result.processing_time or 0
                file_size = result.metadata.get('file_size', 0)
            else:
                # Legacy dict format
                success = result.get('success', False)
                input_file = result.get('input_file', 'Unknown')
                output_file = result.get('output_file', 'N/A')
                processing_time = result.get('processing_time', 0)
                file_size = result.get('file_size', 0)

            # Status with appropriate styling
            if success:
                status = "[green]✅ Success[/green]"
            else:
                status = "[red]❌ Failed[/red]"

            # File size formatting
            size = self._format_file_size(file_size)

            # Processing time
            proc_time = f"{processing_time:.2f}s"

            table.add_row(
                input_file,
                status,
                size,
                proc_time,
                output_file
            )

        self.console.print(table)

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def display_operation_summary(self, operation: str, input_files: int,
                                  success_count: int, total_time: float):
        """Display operation summary."""
        if input_files == 0:
            input_files = 1  # Prevent division by zero

        success_rate = (success_count / input_files * 100)
        avg_time = total_time / input_files

        summary_text = f"""[bold cyan]{operation} Complete![/bold cyan]

📊 Summary:
• Files processed: [bold]{success_count}/{input_files}[/bold]
• Success rate: [bold green]{success_rate:.1f}%[/bold green]
• Total time: [bold blue]{total_time:.2f}s[/bold blue]
• Average per file: [bold yellow]{avg_time:.2f}s[/bold yellow]"""

        summary_panel = Panel(
            summary_text,
            title="🎉 Operation Summary",
            border_style="green"
        )
        self.console.print(summary_panel)

    def confirm_action(self, message: str) -> bool:
        """Confirm user action."""
        return Confirm.ask(f"⚠️  {message}")

    def display_config_panel(self, config: Dict[str, Any]):
        """Display current configuration."""
        config_text = "\n".join([f"• [bold]{key}:[/bold] [cyan]{value}[/cyan]"
                                 for key, value in config.items()])

        panel = Panel(
            config_text,
            title="⚙️ Current Configuration",
            border_style="blue"
        )
        self.console.print(panel)

    def display_suggestions_panel(self, title: str, suggestions: List[str]):
        """Display a panel with helpful suggestions."""
        content = []
        for i, suggestion in enumerate(suggestions, 1):
            content.append(f"[green]{i}.[/green] {suggestion}")

        panel = Panel(
            "\n".join(content),
            title=f"💡 {title}",
            border_style="green"
        )
        self.console.print(panel)


class BatchProgressTracker:
    """Enhanced batch progress tracker with error handling."""

    def __init__(self, ui: DocForgeUI):
        self.ui = ui
        self.progress = None
        self.task_id = None
        self.results = []
        self.errors = []

    def start_batch(self, total_files: int, operation: str):
        """Start batch processing with progress tracking."""
        self.progress = self.ui.create_progress_bar()
        self.progress.start()
        self.task_id = self.progress.add_task(
            f"[cyan]{operation}...", total=total_files
        )
        self.results = []
        self.errors = []

    def update_progress(self, result: ProcessingResult):
        """Update progress with a ProcessingResult."""
        # Store result
        self.results.append(result)

        # Track errors separately
        if not result.success:
            self.errors.append(result)

        # Update progress bar
        if self.progress and self.task_id is not None:
            display_name = os.path.basename(result.input_file) if result.input_file else "file"

            if result.success:
                self.progress.update(
                    self.task_id,
                    advance=1,
                    description=f"[green]✅ {display_name}[/green]"
                )
            else:
                self.progress.update(
                    self.task_id,
                    advance=1,
                    description=f"[red]❌ {display_name}[/red]"
                )

    def finish_batch(self, operation: str):
        """Finish batch processing and show comprehensive results."""
        if self.progress:
            self.progress.stop()

        # Calculate statistics
        success_count = sum(1 for r in self.results if r.success)
        total_time = sum(r.processing_time for r in self.results if r.processing_time)

        # Display results table
        self.ui.display_results_table(self.results, f"{operation} Results")

        # Display summary
        self.ui.display_operation_summary(
            operation, len(self.results), success_count, total_time
        )

        # Display error summary if there were errors
        if self.errors:
            self.ui.console.print(f"\n[bold red]❌ {len(self.errors)} Error(s) Occurred:[/bold red]")

            # Group errors by type
            error_groups = {}
            for result in self.errors:
                if result.error:
                    error_type = result.error.__class__.__name__
                    if error_type not in error_groups:
                        error_groups[error_type] = []
                    error_groups[error_type].append(result)

            # Display error summary
            for error_type, error_results in error_groups.items():
                self.ui.console.print(f"\n[yellow]{error_type}:[/yellow] {len(error_results)} file(s)")
                for result in error_results[:3]:  # Show first 3 examples
                    filename = os.path.basename(result.input_file) if result.input_file else "unknown"
                    self.ui.console.print(f"  • {filename}: {result.message}")

                if len(error_results) > 3:
                    self.ui.console.print(f"  • ... and {len(error_results) - 3} more")

            # Show common suggestions
            if error_groups:
                common_suggestions = [
                    "Check the error details above for specific issues",
                    "Verify input files are valid and accessible",
                    "Ensure you have proper permissions",
                    "Try processing files individually to isolate problems"
                ]
                self.ui.display_suggestions_panel("Troubleshooting Tips", common_suggestions)
