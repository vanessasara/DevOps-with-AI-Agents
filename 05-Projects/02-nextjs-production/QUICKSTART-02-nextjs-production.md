# 🏭 Level 2 — Next.js + FastAPI (Production)

**Folder:** `02-nextjs-production/`

Promotes the Streamlit prototype to a production-grade architecture: a **Next.js** frontend with a **FastAPI** backend, proper session state, and a clean API boundary between the UI and the AI agent.

---

## What It Adds Over Level 1

- Next.js frontend (React-based chat UI)
- FastAPI backend serving the agent over HTTP
- Session state — conversation history persists per browser tab
- Clean separation between UI and AI logic
- Production-ready project layout

---

## Prerequisites

- Python 3.12+ and [`uv`](https://docs.astral.sh/uv/)
- Node.js 18+ and `npm`
- A [Gemini API key](https://aistudio.google.com/app/apikey)

---

## Backend Setup

```bash
cd 02-nextjs-production/backend

uv sync
```

Create `backend/.env`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-2-flash-preview
LOG_DIRECTORY=logs
```

Run the FastAPI server:

```bash
uv run uvicorn app:app --reload --port 8000
```

The API will be available at [http://localhost:8000](http://localhost:8000).

---

## Frontend Setup

```bash
cd 02-nextjs-production/frontend

npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Run Both Together (recommended)

Open two terminals:

```bash
# Terminal 1 — backend
cd 02-nextjs-production/backend
uv run uvicorn app:app --reload --port 8000

# Terminal 2 — frontend
cd 02-nextjs-production/frontend
npm run dev
```

---

## Project Structure

```
02-nextjs-production/
├── backend/
│   ├── app.py              # FastAPI entry point
│   ├── src/
│   │   ├── config.py
│   │   ├── agents/
│   │   └── tools/
│   ├── logs/
│   └── pyproject.toml
└── frontend/
    ├── app/
    │   └── page.tsx        # Chat UI
    ├── package.json
    └── .env.local          # NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Next Level

➡️ **Level 3** adds decision-making: severity classification, human approval gates, and Kubernetes action tools — back on Streamlit for faster iteration before the next production promotion.
