# 💬 Level 1 — Streamlit UI

**Folder:** `01-streamlit-ui/`

Wraps the Level 0 terminal agent in a Streamlit chat interface. Same agent logic, same tools — now with a browser-based UI, sidebar quick-prompts, and chat history.

---

## What It Adds Over Level 0

- Streamlit chat UI with message history
- Sidebar with one-click example prompts
- Clear chat button
- Model and log directory displayed in the sidebar

---

## Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/)
- A [Gemini API key](https://aistudio.google.com/app/apikey)

---

## Setup

```bash
cd 01-streamlit-ui

uv sync
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-2-flash-preview
LOG_DIRECTORY=logs
```

Add `.log` files to the `logs/` directory:

```bash
cp /path/to/your/app.log logs/
```

---

## Run

```bash
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Example Prompts

| Prompt | What it does |
|---|---|
| `What log files are available?` | Lists all `.log` files |
| `Read sample_app.log` | Displays full file contents |
| `Search for ERROR in sample_app.log` | Finds matching lines |
| `Summarise everything and save it` | Analysis + writes `Summary.md` |

---

## Project Structure

```
01-streamlit-ui/
├── app.py                 # Streamlit UI entry point
├── src/
│   ├── __init__.py
│   ├── config.py          # Env vars + hardcoded agent instructions
│   ├── agents/
│   │   └── log_analyzer.py
│   └── tools/
│       └── log_tools.py
├── logs/
├── pyproject.toml
└── .env
```

---

## Output

Analysis summaries are saved to `Summary.md` in the project root.

---

## Next Level

➡️ **Level 2** promotes this to a production-grade Next.js + FastAPI architecture with session state.
