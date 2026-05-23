# 🚨 AI DevOps Incident Responder

A multi-agent DevOps incident response system built with the OpenAI Agents SDK, LiteLLM, and Gemini.
Agents collaborate via handoffs and use real CLI tools (`kubectl`, `docker`, `gh`) running on your machine.

## Architecture

```
User Query
    │
    ▼
Triage Agent  ──────────────────────────────────────┐
    │                                                │
    ├──► K8s Specialist    (kubectl commands)        │
    ├──► Docker Specialist (docker commands)         │  handoffs
    ├──► GitHub Specialist (gh CLI commands)         │
    └──► Healer Agent      (approved fixes only)     │
                                                     │
Summarizer Agent (full tool access, dashboard view) ─┘
```

## Model

```
Gemini only via LiteLLM
```
Set `GEMINI_API_KEY` and optionally `GEMINI_MODEL` in `.env`.

## Quick Start

### 1. Install dependencies
```bash
uv sync
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run
```bash
uv run streamlit run app.py
```

Open http://localhost:8501

## Prerequisites

| Tool | Required for | Install |
|---|---|---|
| `kubectl` | K8s tools | https://kubernetes.io/docs/tasks/tools |
| `docker` | Docker tools | https://docs.docker.com/get-docker |
| `gh` CLI | GitHub tools | https://cli.github.com |

- `kubectl` must be configured with a valid kubeconfig (`~/.kube/config`)
- `gh` must be authenticated: `gh auth login`
- Read-only `kubectl`, `docker`, and `gh` commands run through subprocess using your local CLI configuration
- Set `K8S_ENABLED=true` and `DOCKER_ENABLED=true` in `.env` only when you want approved restart/stop/patch actions to run for real
- Set `GITHUB_TOKEN` in `.env`; the app passes it to GitHub CLI as `GH_TOKEN`

## Agent Modes

| Mode | Description |
|---|---|
| **Summarizer Dashboard** | Executive-level infra health summary using all tools |
| **Kubernetes Operations** | Direct kubectl access — pods, logs, events, patches |
| **Full Analysis** | Routes through Triage → specialist agents via handoffs |

## Project Structure

```
03-1-final-project/
├── app.py                  # Streamlit UI
├── system_prompt.txt       # Agent system prompt
├── pyproject.toml          # Dependencies
├── .env.example            # Environment template
└── src/
    ├── config.py           # All config & env vars
    ├── agents/
    │   ├── triage_agent.py
    │   ├── k8s_agent.py
    │   ├── docker_agent.py
    │   ├── github_agent.py
    │   ├── healer_agent.py
    │   ├── summarizer_agent.py
    │   └── log_analyzer.py
    ├── tools/
    │   ├── k8s_tools.py
    │   ├── docker_tools.py
    │   ├── github_tools.py
    │   ├── healing_tools.py
    │   └── log_tools.py
    └── utils/
        └── model_factory.py
```
