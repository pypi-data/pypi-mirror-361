import os
import subprocess
import time
from pathlib import Path
from typing import Tuple, Optional
import sys
from vdsnow.context import get_default_context
from vdsnow.compiler import compile_plan
from vdsnow.state import load_state, save_state
from vdsnow.audit import get_create_audit_infra_sql, get_insert_sql
from vdsnow.snow_cli_runner import run_snow_command

from rich.console import Console

console = Console()


def check_version() -> None:
    """Run snowcli app deploy --stage <stage>."""
    try:
        cmd = ["snow", "--version"]
        print(f"✅ Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(e.returncode)


# --- Helper Functions ---

def _run_snow_query(query: str, use_local_context: bool):
    """A robust wrapper for executing 'snow sql -q'."""
    console.print(f"\n[bold cyan]Executing query via snowcli...[/bold cyan]")

    run_snow_command(["sql", "-q", query], use_local_context)


# --- Public CLI-Facing Functions ---

def execute(
    file: Optional[str] = None,
    query: Optional[str] = None,
    use_local_context: bool = False,
    differ_mode: bool = False,
    audit_enabled: bool = False,
    env: Optional[str] = None
) -> None:
    """
    Executes SQL against Snowflake.
    - In local mode, it runs the file in the default sandbox context.
    - In headless mode, it compiles the file to handle dynamic context switching.
    """
    if query:
        db, schema = get_default_context()
        if not db or not schema:
            console.print("[bold red]❌ ERROR: Could not determine default context for query.[/bold red]")
            return
        final_query = f"use schema {db}.{schema}; {query}"
        console.print(f"\n[bold cyan]Executing query...[/bold cyan]")
        _run_snow_query(final_query, use_local_context)
        return

    if not file:
        return

    if audit_enabled:
        console.print("\n[bold dim]Ensuring audit table exists...[/bold dim]")
        _run_snow_query(get_create_audit_infra_sql(), use_local_context)

    # --- Setup for execution and auditing ---
    start_time = time.time()
    status = "SUCCESS"
    error_message = None
    executed_nodes = []
    commands_to_run = []
    full_new_state = []

    try:
        file_path = Path(file)
        if not file_path.exists():
            console.print(f"[bold red]❌ ERROR: File not found at '{file}'[/bold red]")
            return

        # 1
        old_state = load_state() if differ_mode else {}

        # 2. Compile the plan. This function correctly handles local vs headless context.
        commands_to_run, full_new_state = compile_plan(
            start_file=file_path,
            use_local_context=use_local_context,
            differ_mode=differ_mode,
            old_state=old_state
        )

        if not commands_to_run:
            console.print("\n[bold green]✅ No changes detected. Your infrastructure is up-to-date.[/bold green]")
            # If there's nothing to run, there's no need to update the state file.
            return

        console.print(f"\n[bold cyan]🚀 Executing {len(commands_to_run)} steps...[/bold cyan]")
        for i, node in enumerate(commands_to_run):
            console.print(f"   [dim]Step {i+1}/{len(commands_to_run)}: Applying {node['path']}...[/dim]")
            _run_snow_query(node['command'], use_local_context)

        # 4. Always save the new, complete state after a successful run.
        console.print("\n[bold green]✅ Deployment execution finished.[/bold green]")
        save_state(full_new_state)

    except Exception as e:
        status = "FAILURE"
        error_message = str(e)
        console.print(f"\n[bold red]❌ EXECUTION FAILED: {error_message}[/bold red]")
        raise # Re-raise to ensure the CLI exits with a non-zero status code

    finally:
        # This block runs on success, failure, or "no changes".
        if audit_enabled:
            console.print("\n[bold dim]Writing audit record...[/bold dim]")
            end_time = time.time()

            audit_record = {
                "status": status,
                "env": env,
                "files_planned_count": len(commands_to_run),
                "files_executed_count": len(executed_nodes),
                "execution_time_sec": round(end_time - start_time, 2),
                "git_commit_sha": os.getenv("GITHUB_SHA", "local_run"),
                "executed_files": [node['path'] for node in executed_nodes],
                "error_message": error_message,
            }

            audit_insert_sql = get_insert_sql(audit_record)
            _run_snow_query(audit_insert_sql, use_local_context)
            console.print("[bold green]✅ Audit record saved successfully.[/bold green]")


def plan(file: str, use_local_context: bool, differ_mode: bool) -> None:
    """
    Displays the execution plan for a given file without running it.
    Can show a full plan or a differential plan.
    """
    file_path = Path(file)
    if not file_path.exists():
        console.print(f"[bold red]❌ ERROR: File not found at '{file}'[/bold red]")
        return

    console.print(f"\n[bold cyan]📖 Generating execution plan for '{file_path}'...[/bold cyan]")

    old_state = load_state() if differ_mode else {}
    commands_to_run, _ = compile_plan(
        start_file=file_path,
        use_local_context=use_local_context,
        differ_mode=differ_mode,
        old_state=old_state
    )

    if not commands_to_run:
        console.print("\n[bold green]✅ No changes detected. Your infrastructure is up-to-date.[/bold green]")
        return

    console.print(f"\n[bold]Execution Plan ({len(commands_to_run)} steps):[/bold]")
    for i, node in enumerate(commands_to_run):
        console.print(f"  {i+1}. {node['command']}")


def refresh_state(file: str, use_local_context: bool) -> None:
    """
    Compiles a plan and updates the vdstate.json file without executing any SQL.
    """
    file_path = Path(file)
    if not file_path.exists():
        console.print(f"[bold red]❌ ERROR: File not found at '{file}'[/bold red]")
        return

    console.print(f"\n[bold cyan]🔄 Refreshing state from '{file_path}'...[/bold cyan]")

    # We only need the full new state, so we can ignore the commands_to_run.
    # We set differ_mode=False because we want to capture the *entire* current state.
    _, full_new_state = compile_plan(
        start_file=file_path,
        use_local_context=use_local_context,
        differ_mode=False,
        old_state={}
    )

    if not full_new_state:
        console.print("[yellow]Warning: Compilation resulted in an empty state. No changes made.[/yellow]")
        return

    # Save the newly compiled state.
    save_state(full_new_state)
    console.print("\n[bold green]✅ State file has been refreshed successfully.[/bold green]")
