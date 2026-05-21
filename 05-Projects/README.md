# 🤖 DevOps with AI Agents — Project Quickstarts

A progressive series of AI-powered DevOps projects, each level building on the last.

---

## The Levels

| Level | Folder | Stack | Key Feature |
|---|---|---|---|
| [0 — Terminal Prototype](./QUICKSTART-00-terminal-prototype.md) | `00-terminal-prototype/` | Python + LiteLLM | Working terminal agent, proven core |
| [1 — Streamlit UI](./QUICKSTART-01-streamlit-ui.md) | `01-streamlit-ui/` | Python + Streamlit | Browser chat interface |
| [2 — Next.js + FastAPI](./QUICKSTART-02-nextjs-production.md) | `02-nextjs-production/` | Next.js + FastAPI | Production architecture |
| [3 — Decision Making](./QUICKSTART-03-decision-making.md) | `03-decision-making/` | Python + Streamlit | Severity classification + approval gate + K8s actions |

---

## Common Prerequisites (all levels)

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- A [Gemini API key](https://aistudio.google.com/app/apikey)

---

## Common `.env` Variables

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-2-flash-preview   # default if not set
LOG_DIRECTORY=logs                            # default if not set
```

Level 3 adds:
```env
K8S_ENABLED=false    # set true for live kubectl
```

---

## Start Here

If you're new to the project, start at **Level 0** and work up:

```bash
cd 00-terminal-prototype
uv sync
# add .env with GEMINI_API_KEY
uv run python -m src
```

Each level's quickstart describes exactly what's new and how to run it.
