# 🚨 Level 3 — Decision Making & Actions

**Folder:** `03-decision-making/`

The agent stops being a passive reporter. It now **classifies incident severity**, **recommends a specific action**, and **asks for your approval** before doing anything. Kubernetes pod restarts are supported in simulation or live mode.

---

## What It Adds Over Level 2

- **Severity classification** — P1 Critical / P2 High / P3 Medium / Info
- **Human approval gate** — the agent never acts without an explicit `yes`
- **Two-phase response pattern** — Phase 1 ends with a question; Phase 2 executes and guides
- **Kubernetes action tool** — `restart_kubernetes_pod` (simulation by default)
- **Externalised system prompt** — edit `system_prompt.txt` without touching Python

---

## Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/)
- A [Gemini API key](https://aistudio.google.com/app/apikey)
- (Optional) `kubectl` configured against a real cluster for live K8s mode

---

## Setup

```bash
cd 03-decision-making

uv sync
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini/gemini-2-flash-preview
LOG_DIRECTORY=logs
K8S_ENABLED=false          # set to true for live kubectl execution
```

The `logs/k8s-java-app.log` sample file (OOM + CrashLoopBackOff scenario) is included — no extra setup needed to test.

---

## Run

```bash
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

---

## Typical Incident Flow

**Step 1 — Trigger analysis:**
```
Check k8s-java-app.log for issues
```
The agent reads the file, detects the OOM + CrashLoopBackOff, classifies it **P1 Critical**, shows evidence with timestamps, recommends a pod restart, and asks:
> "Would you like me to proceed? (yes/no)"

**Step 2a — Approve:**
```
yes
```
The agent calls `restart_kubernetes_pod`. In simulation mode it prints what it would do. With `K8S_ENABLED=true` it runs `kubectl delete pod ...` for real.

**Step 2b — Decline:**
```
no
```
The agent acknowledges and suggests manual steps or continued monitoring.

---

## Severity Levels

| Level | Meaning | Example |
|---|---|---|
| 🔴 **P1** | Critical — service down | CrashLoopBackOff, OOMKilled |
| 🟠 **P2** | High — degraded | High memory, elevated errors |
| 🟡 **P3** | Medium — warning | Deprecated APIs, cache misses |
| 🔵 **Info** | No action needed | Startup messages, health checks |

---

## Kubernetes Live Mode

To enable real `kubectl` execution:

1. Ensure `kubectl` is installed and configured (`kubectl get pods` works)
2. Set `K8S_ENABLED=true` in `.env`
3. Restart the app

The agent will call `kubectl delete pod <name> -n <namespace>`. The Deployment recreates the pod automatically.

---

## Editing the Agent's Behaviour

All agent instructions live in `system_prompt.txt` at the project root. Edit it freely — no Python changes needed. The config reads it fresh on each startup.

---

## Project Structure

```
03-decision-making/
├── app.py                    # Streamlit UI (severity legend, K8s status)
├── system_prompt.txt         # Agent instructions — edit here
├── src/
│   ├── __init__.py
│   ├── config.py             # Reads system_prompt.txt, K8S_ENABLED flag
│   ├── agents/
│   │   ├── __init__.py
│   │   └── log_analyzer.py   # Agent + Runner
│   ├── tools/
│   │   ├── __init__.py       # get_all_tools()
│   │   ├── log_tools.py      # list, read, search, save
│   │   └── k8s_tools.py      # restart_kubernetes_pod
│   └── utils/
│       └── response.py       # format_output helper
├── logs/
│   └── k8s-java-app.log      # Sample OOM crash log
├── pyproject.toml
└── .env
```

---

## Verification Tests

Before moving to Level 4, confirm all five tests pass:

| Test | Input | Expected |
|---|---|---|
| 1 | `Check k8s-java-app.log for issues` | P1 classification + approval prompt |
| 2 | `yes` (after Test 1) | Simulated restart + monitoring guidance |
| 3 | `Restart the pod now` (cold) | Agent asks for confirmation first |
| 4 | `no` (after recommendation) | Agent acknowledges, suggests alternatives |
| 5 | `What is the severity of the k8s-java-app.log issue?` | P1 with cited log evidence |

---

## Next Level

➡️ **Level 4** promotes this to Next.js + FastAPI again, adds more action tools (cache clear, disk cleanup, service health check), and introduces structured JSON incident responses. `system_prompt.txt` and `k8s_tools.py` carry forward unchanged.
