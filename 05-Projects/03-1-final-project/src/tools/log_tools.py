"""Log tools — read and search local log files."""
from pathlib import Path
from agents import function_tool
from ..config import Config


@function_tool
def list_log_files() -> str:
    """List all available .log files in the configured log directory."""
    files = sorted(Path(Config.LOG_DIRECTORY).glob("*.log"))
    if not files:
        return f"No .log files found in '{Config.LOG_DIRECTORY}/'."
    return "Available log files:\n" + "\n".join(
        f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)" for f in files
    )


@function_tool
def read_log_file(filename: str) -> str:
    """Read the full content of a log file."""
    path = Path(Config.LOG_DIRECTORY) / filename
    try:
        content = path.read_text(encoding="utf-8")
        return f"📄 {filename} — {content.count(chr(10)) + 1} lines\n\n{content}"
    except FileNotFoundError:
        return f"❌ File '{filename}' not found in '{Config.LOG_DIRECTORY}/'."
    except Exception as exc:
        return f"❌ Error reading file: {exc}"


@function_tool
def search_logs(filename: str, search_term: str) -> str:
    """Search for a term (case-insensitive) in a specific log file."""
    path = Path(Config.LOG_DIRECTORY) / filename
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        matches = [
            f"Line {i + 1}: {line}"
            for i, line in enumerate(lines)
            if search_term.lower() in line.lower()
        ]
        if not matches:
            return f"No matches for '{search_term}' in {filename}."
        return f"🔍 {len(matches)} match(es) for '{search_term}' in {filename}:\n\n" + "\n".join(matches)
    except FileNotFoundError:
        return f"❌ File '{filename}' not found."
    except Exception as exc:
        return f"❌ Error: {exc}"


@function_tool
def save_summary(summary: str) -> str:
    """Save an analysis summary to Summary.md."""
    try:
        Path("Summary.md").write_text(f"# DevOps Analysis Summary\n\n{summary}", encoding="utf-8")
        return "✅ Summary saved to Summary.md."
    except Exception as exc:
        return f"❌ Failed to save summary: {exc}"


def get_log_tools() -> list:
    return [list_log_files, read_log_file, search_logs, save_summary]
