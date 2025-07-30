from rich.console import Console
from rich.panel import Panel

console = Console()

ERROR_MESSAGES = {
    "pattern_not_found": "Pattern '{pattern}' not found. Use 'cliops patterns' to see available options.",
    "empty_prompt": "Empty prompt detected. Try: cliops \"your prompt here\"",
    "state_corrupted": "State file corrupted. Run 'cliops init' to reset.",
    "invalid_input": "Invalid input provided. Please check your command syntax."
}

def show_error(error_type: str, **kwargs):
    """Display user-friendly error messages with helpful guidance."""
    message = ERROR_MESSAGES.get(error_type, "An error occurred").format(**kwargs)
    console.print(Panel.fit(
        f"[bold red]Error:[/bold red] {message}",
        border_style="red"
    ))

def show_success_message(action: str, details: str = ""):
    """Display success feedback with optional details."""
    console.print(Panel.fit(
        f"[bold green]Success:[/bold green] {action}\n{details}",
        border_style="green"
    ))