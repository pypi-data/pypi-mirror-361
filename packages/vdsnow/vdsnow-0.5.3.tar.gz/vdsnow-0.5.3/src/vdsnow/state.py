import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from vdsnow.snow_cli_runner import run_snow_command

from rich.console import Console

console = Console()
STATE_FILE = Path("vdstate.json")

def load_state() -> Dict[str, Any]:
    """
    Loads the vdstate.json file.
    Returns a dictionary keyed by file path for efficient lookups.
    """
    if not STATE_FILE.exists():
        return {}

    try:
        with open(STATE_FILE, "r") as f:
            state_data = json.load(f)

        # Convert the list of objects into a path-keyed dictionary
        return {item['path']: item for item in state_data.get('files', [])}
    except (json.JSONDecodeError, KeyError):
        console.print(f"[bold yellow]Warning: Could not parse '{STATE_FILE}'. Treating as empty state.[/bold yellow]")
        return {}


def save_state(new_state_files: list) -> None:
    """
    Saves the new state to vdstate.json, overwriting the old file.
    """
    now_utc = datetime.now(timezone.utc).isoformat()

    full_state = {
        "vdsnow_version": "1.0", # can get this from __version__ later
        "generated_at": now_utc,
        "files": new_state_files
    }

    with open(STATE_FILE, "w") as f:
        json.dump(full_state, f, indent=2)

    console.print(f"   [dim]State updated successfully in '{STATE_FILE}'[/dim]")


def get_state_from_remote(database: str, schema: str, path: str, use_local_context: bool) -> None:
    """
    Runs 'snow sql -q "GET @RAW.VD.VDSNOW file:///<path>/to/project/"
    This provides a wrapper around the snowcli command, showing live output.
    """
    console.print("\n[bold cyan]🧪 Running 'snow get vdstate.json'...[/bold cyan]")

    LOCAL_PATH: Path = Path(path).resolve()
    COMMAND: str = fr"GET @{database}.{schema}.VDSNOW file:///{LOCAL_PATH}/"

    run_snow_command(["sql", "-q", COMMAND], use_local_context)
