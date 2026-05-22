import subprocess
from pathlib import Path
from agents import function_tool

@function_tool
def list_workflow_runs(status: str = "failure") -> str:
    """List recent GitHub Actions workflow runs. Use status='failure' for failures."""
    r = subprocess.run(
        ["gh", "run", "list", "--status", status, "--limit", "5"],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr

@function_tool
def get_failed_logs(run_id: str) -> str:
    """Get failed step logs from a GitHub Actions run. Pass the run ID."""
    r = subprocess.run(
        ["gh", "run", "view", run_id, "--log-failed"],
        capture_output=True, text=True
    )
    out = r.stdout + r.stderr
    return out[:5000] + "
[truncated]" if len(out) > 5000 else out

@function_tool
def get_workflow_file(workflow_name: str) -> str:
    """Read a GitHub Actions workflow YAML file. Pass filename like 'ci.yml'."""
    path = Path(f".github/workflows/{workflow_name}")
    return path.read_text() if path.exists() else f"Not found: {path}"


def get_github_tools():
    return [list_workflow_runs, get_failed_logs, get_workflow_file]
