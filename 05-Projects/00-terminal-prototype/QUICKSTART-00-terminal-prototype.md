# 🖥️ Level 0 — Terminal Prototype

**Folder:** `00-terminal-prototype/`

The foundation of the series. A pure terminal-based AI agent that reads, searches, and summarises log files using Gemini via LiteLLM. No UI — just a working proof of concept.

---

## What It Does

- Lists available `.log` files in the `logs/` directory
- Reads full log file contents
- Searches logs for specific patterns (e.g. `ERROR`, `WARN`)
- Saves a markdown summary to `Summary.md`
- Runs as an interactive terminal chat loop

---

## Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) (recommended)
- A [Gemini API key](https://aistudio.google.com/app/apikey)

---

## Setup

```bash
cd 00-terminal-prototype

# Install dependencies
uv sync
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-2-flash-preview
LOG_DIRECTORY=logs
```

Add some `.log` files to the `logs/` directory (created automatically on first run):

```bash
cp /path/to/your/app.log logs/
```

---

## Run

```bash
uv run python -m src
```

Then type in plain English:

```
You: What log files are available?
You: Read sample_app.log
You: Search for ERROR in sample_app.log
You: Summarise everything and save it
You: quit
```

Type `clear` to reset the agent, `quit` or `exit` to stop.

---

## Project Structure

```
00-terminal-prototype/
├── src/
│   ├── __init__.py
│   ├── config.py          # Env vars + hardcoded agent instructions
│   ├── main.py            # Terminal chat loop
│   ├── __main__.py        # Entry point for python -m src
│   ├── agents/
│   │   └── log_analyzer.py   # Agent + Runner wrapper
│   └── tools/
│       └── log_tools.py      # list, read, search, save tools
├── logs/                  # Drop .log files here
├── pyproject.toml
└── .env
```

---

## Output

After `save_summary` is called, a `Summary.md` is written to the project root.

---

## Next Level

➡️ **Level 1** adds a Streamlit chat UI on top of this same agent core.
