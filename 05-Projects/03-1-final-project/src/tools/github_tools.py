"""GitHub tools - real gh CLI commands using the GitHub CLI."""

import os
import subprocess
from pathlib import Path

from agents import function_tool

from ..config import Config


def _gh_env() -> dict[str, str]:
    env = os.environ.copy()
    if Config.GITHUB_TOKEN and not env.get("GH_TOKEN"):
        env["GH_TOKEN"] = Config.GITHUB_TOKEN
    return env


def _gh(*args: str, timeout: int = 20) -> str:
    """Run a gh CLI command and return combined stdout/stderr."""
    try:
        result = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_gh_env(),
        )
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode != 0:
            return f"gh exited with code {result.returncode}:\n{output.strip()}"
        return output.strip() or "gh command completed with no output."
    except FileNotFoundError:
        return "gh CLI not found. Install it and authenticate with GITHUB_TOKEN/GH_TOKEN or `gh auth login`."
    except subprocess.TimeoutExpired:
        return f"gh CLI timed out after {timeout}s."
    except Exception as exc:
        return f"gh error: {exc}"


@function_tool
def github_auth_status() -> str:
    """Check whether the GitHub CLI is installed and authenticated."""
    return _gh("auth", "status", timeout=10)


@function_tool
def list_workflow_runs(status: str = "failure") -> str:
    """List recent GitHub Actions workflow runs filtered by status."""
    return _gh("run", "list", "--status", status, "--limit", "5")


@function_tool
def get_failed_logs(run_id: str) -> str:
    """Get failed step logs from a GitHub Actions run. Pass the numeric run ID."""
    output = _gh("run", "view", run_id, "--log-failed", timeout=30)
    if len(output) > 5000:
        return output[:5000] + "\n[truncated - output exceeds 5000 chars]"
    return output


@function_tool
def get_workflow_file(workflow_name: str) -> str:
    """Read a GitHub Actions workflow YAML file. Pass filename e.g. ci.yml."""
    path = Path(".github/workflows") / workflow_name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"Not found: {path}"


@function_tool
def list_open_prs() -> str:
    """List open pull requests in the current repository."""
    return _gh("pr", "list", "--state", "open", "--limit", "10")


@function_tool
def get_pr_checks(pr_number: str) -> str:
    """Get CI check status for a pull request. Pass the PR number."""
    return _gh("pr", "checks", pr_number)


def get_github_tools() -> list:
    return [
        github_auth_status,
        list_workflow_runs,
        get_failed_logs,
        get_workflow_file,
        list_open_prs,
        get_pr_checks,
    ]
