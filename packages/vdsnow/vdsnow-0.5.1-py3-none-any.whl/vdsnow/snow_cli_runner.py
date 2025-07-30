import subprocess
from typing import List
from rich.console import Console

console = Console()

def run_snow_command(command_parts: List[str], use_local_context: bool) -> None:
    """
    A centralized wrapper for all 'snow' CLI commands.

    It automatically adds '--connection headless' if not in local context.
    It also provides standardized error handling.
    """
    base_command = ["snow"]
    if not use_local_context:
        # This is the core logic for CI/CD
        base_command.extend(["--connection", "headless"])

    full_command = base_command + command_parts

    try:
        # `check=True` will automatically raise a CalledProcessError on failure.
        subprocess.run(full_command, check=True)

    except FileNotFoundError:
        console.print("\n[bold red]❌ ERROR: `snow` command not found.[/bold red]")
        console.print("   Please ensure the Snowflake CLI is installed and in your system's PATH.")
        # Re-raise to halt execution
        raise

    except subprocess.CalledProcessError:
        # snowcli will have already printed a detailed error message.
        # We just add a concluding message and re-raise the exception so that
        # calling functions (like the audit) know that a failure occurred.
        console.print(f"\n[bold red]❌ Sub-command failed: {' '.join(full_command)}[/bold red]")
        raise
