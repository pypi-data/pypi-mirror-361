from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from contextlib import contextmanager

console = Console()

@contextmanager
def show_optimization_progress():
    """Show progress indicator during optimization."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("🔍 Analyzing prompt...", total=None)
        yield progress, task

@contextmanager 
def show_analysis_progress():
    """Show progress indicator during analysis."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("📊 Analyzing prompt structure...", total=None)
        yield progress, task