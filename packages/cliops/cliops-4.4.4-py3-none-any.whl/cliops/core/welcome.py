from rich.console import Console
from rich.panel import Panel

console = Console()

def show_welcome_banner():
    """Display welcome banner for first-time users."""
    console.print(Panel(
        "[bold blue]Welcome to cliops v4.2.4[/bold blue]\n"
        "[dim]// your terminal just hired a prompt engineer //[/dim]",
        style="blue", expand=False
    ))

def show_first_run_tips():
    """Show helpful tips for new users."""
    console.print(Panel.fit(
        "[bold yellow]Getting Started Tips:[/bold yellow]\n\n"
        "- Use [bold]cliops \"your prompt\"[/bold] for quick optimization\n"
        "- Set project context with [bold]cliops state set ARCHITECTURE \"React\"[/bold]\n"
        "- Analyze prompts with [bold]cliops analyze \"prompt text\"[/bold]\n"
        "- View patterns with [bold]cliops patterns[/bold]",
        border_style="yellow"
    ))