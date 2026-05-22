# AI Logging System for DevOps — Full Build Roadmap

> **Stack:** OpenAI Agents SDK · LiteLLM · Gemini (Groq fallback) · Streamlit  
> **Pattern:** Each level builds on the previous. Never use LangChain.  
> **UI Rule:** No dropdowns. Show live agent activity inline using `st.status()`.

---

## Project Structure (final)

```
ai-logging-system/
├── app.py
├── system_prompt.txt
├── .env
├── pyproject.toml
├── logs/
│   └── k8s-java-app.log
├── src/
│   ├── config.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── log_analyzer.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── log_tools.py
│   │   ├── k8s_tools.py
│   │   ├── docker_tools.py
│   │   ├── github_tools.py
│   │   └── healing_tools.py
│   └── utils/
│       └── response.py
├── mcp_server.py
└── Summary.md
```

---

## .env (all levels)

```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
GEMINI_MODEL=gemini/gemini-2.0-flash
FALLBACK_MODELS=groq/llama-3.3-70b-versatile,groq/gemma2-9b-it
LOG_DIRECTORY=logs
K8S_ENABLED=false
DOCKER_ENABLED=true
GITHUB_TOKEN=your_github_token
MCP_ENABLED=false
```

---

## config.py (shared across all levels)

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-2.0-flash")
    FALLBACK_MODELS = os.getenv(
        "FALLBACK_MODELS",
        "groq/llama-3.3-70b-versatile,groq/gemma2-9b-it"
    ).split(",")
    LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "logs")
    K8S_ENABLED = os.getenv("K8S_ENABLED", "false").lower() == "true"
    DOCKER_ENABLED = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    MCP_ENABLED = os.getenv("MCP_ENABLED", "false").lower() == "true"

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        os.makedirs(cls.LOG_DIRECTORY, exist_ok=True)

    @classmethod
    def get_instructions(cls) -> str:
        p = Path(__file__).parent.parent / "system_prompt.txt"
        return p.read_text(encoding="utf-8") if p.exists() else "You are a DevOps expert."
```

---

## Fallback Pattern (use in every agent)

LiteLLM handles 429/503 automatically. The try/except loop below is the safe universal pattern — use it always.

```python
# log_analyzer.py — always use this pattern
from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from src.config import Config

set_tracing_disabled(disabled=True)

def _make_model(model_name: str) -> LitellmModel:
    api_key = (
        Config.GROQ_API_KEY
        if model_name.startswith("groq/")
        else Config.GEMINI_API_KEY
    )
    return LitellmModel(model=model_name, api_key=api_key)

class LogAnalyzerAgent:
    def __init__(self):
        self.primary_model = Config.GEMINI_MODEL
        self.fallbacks = Config.FALLBACK_MODELS
        self._build_agent(self.primary_model)

    def _build_agent(self, model_name: str):
        from src.tools import get_all_tools
        self.agent = Agent(
            name="DevOps Incident Responder",
            instructions=Config.get_instructions(),
            model=_make_model(model_name),
            tools=get_all_tools(),
        )

    async def process_query(self, user_input: str) -> str:
        models_to_try = [self.primary_model] + self.fallbacks
        for model in models_to_try:
            try:
                self._build_agent(model)
                result = await Runner.run(self.agent, input=user_input)
                return str(getattr(result, "final_output", "No response.")).strip()
            except Exception as e:
                err = str(e).lower()
                if any(x in err for x in ["429", "quota", "rate limit", "503"]):
                    continue  # try next model
                return f"Error: {e}"
        return "All models exhausted. Check API keys and quotas."
```

---

## Streamlit Anti-Glitch Rules (follow in every level)

These prevent the most common Streamlit issues — white flashes, double renders, state resets.

```python
# 1. NEVER call st.rerun() inside a chat message block — only call it at the top level
# 2. NEVER use asyncio.run() inside a thread — use this pattern instead:
import asyncio

def run_async(coro):
    """Safe async runner for Streamlit — avoids event loop conflicts."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

# 3. Always gate agent init behind session_state — prevents re-init on every rerun
if "agent" not in st.session_state:
    st.session_state.agent = LogAnalyzerAgent()

# 4. Always append to messages AFTER rendering — prevents double render
# WRONG:
st.session_state.messages.append(msg)
st.chat_message("assistant").markdown(msg)  # already appended, will show twice on rerun

# CORRECT:
with st.chat_message("assistant"):
    st.markdown(response)
st.session_state.messages.append({"role": "assistant", "content": response})

# 5. st.status() must be used as a context manager — never call .update() outside the with block
with st.status("🔍 Analysing...", expanded=True) as status:
    st.write("Reading logs...")
    response = run_async(get_response(user_input))
    status.update(label="✅ Done", state="complete", expanded=False)
# render result AFTER status block closes
st.markdown(response)

# 6. Set page config ONCE at the very top of app.py before any other st call
st.set_page_config(page_title="AI Incident Responder", page_icon="🚨", layout="wide")
```

---

## Live Agent Activity in UI (use everywhere)

```python
# Full handle_input function — copy this pattern into every level's app.py
def handle_input(user_input: str):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Show live agent work then render result
    with st.chat_message("assistant"):
        with st.status("🔍 Analysing incident...", expanded=True) as status:
            st.write("🤖 Agent started...")
            st.write("🔧 Calling tools...")
            response = run_async(get_response(user_input))
            status.update(label="✅ Analysis complete", state="complete", expanded=False)
        st.markdown(response)

    # Append assistant message AFTER render
    st.session_state.messages.append({"role": "assistant", "content": response})
```

---

## Guardrails (apply to every agent, every level)

Add this block verbatim to every `system_prompt.txt`:

```
## Guardrails
- NEVER execute any action (restart, delete, patch, run command) without explicit "yes" from the user
- NEVER speculate about causes not evidenced in logs or tool output
- NEVER call destructive tools (restart_pod, patch_resources, fix_image) in the same turn as analysis
- If severity is P1, state it urgently but still wait for approval
- If a fix is outside your action space, say so clearly and suggest manual steps
- Constrained action space: only restart_pod, fix_image, patch_resources, cache_clear, disk_cleanup, skip
- No arbitrary shell commands ever
```

---

## Severity Classification (all levels)

| Level | Meaning | Examples |
|---|---|---|
| 🔴 P1 | Critical — service down | CrashLoopBackOff, OOMKilled, pod deleted |
| 🟠 P2 | High — degraded | High memory, elevated errors, slow queries |
| 🟡 P3 | Medium — warning | Deprecated API, cache miss increase |
| 🔵 Info | No action needed | Startup messages, health checks |

---

---

# LEVEL 3 — Decision Making (ALREADY BUILT)

✅ Already complete. Do not rebuild.

**What exists:** Streamlit chat + Gemini agent + log tools + K8s restart tool + severity classification + two-phase approval pattern.

**Upgrade only:**
- [ ] Add fallback pattern to `log_analyzer.py`
- [ ] Replace `asyncio.run()` with safe `run_async()` helper
- [ ] Replace spinners with `st.status()` live activity pattern
- [ ] Add guardrails block to `system_prompt.txt`
- [ ] Verify `handle_input` appends messages after render (not before)

### Start & Test — Level 3

```bash
cd 03-decision-making
uv sync
uv run streamlit run app.py
```

**Browser:** http://localhost:8501

**Test commands (type in chat):**
```
Check k8s-java-app.log for issues
# Expected: P1 classification + approval prompt

yes
# Expected: simulated restart + monitoring guidance

What is the severity of the k8s-java-app.log issue?
# Expected: P1 with cited log evidence

Restart the pod now
# Expected: agent asks for confirmation first, does NOT restart immediately

no
# Expected: agent acknowledges, suggests manual steps
```

---

---

# LEVEL 4 — Multi-Tool DevOps Agent + MCP

**What it adds over Level 3:**
- Docker tools (list, logs, inspect, restart container)
- GitHub CLI tools (list runs, get failed logs, read workflow file)
- Healing tools (fix_image, patch_resources, cache_clear, disk_cleanup)
- MCP server exposing all tools to Claude Desktop / any MCP client
- Structured incident card in UI
- Beautiful multi-panel Streamlit UI with live agent steps per tool call

---

## Checklist — Level 4

- [ ] `docker_tools.py` — 4 tools
- [ ] `github_tools.py` — 3 tools
- [ ] `healing_tools.py` — 4 tools
- [ ] Update `k8s_tools.py` — add `patch_resources`, `fix_image`
- [ ] Update `tools/__init__.py` — `get_all_tools()` returns all tools
- [ ] Update `system_prompt.txt` — add Docker/GitHub/healing sections + guardrails
- [ ] `mcp_server.py` — exposes all tools via FastMCP
- [ ] Update `app.py` — multi-panel UI, live steps, structured incident card, `run_async` helper
- [ ] Fallback pattern in `log_analyzer.py`
- [ ] Add `fastmcp` to `pyproject.toml`
- [ ] Test all 5 scenarios below before marking done

---

## docker_tools.py

```python
import subprocess
from agents import function_tool
from src.config import Config

@function_tool
def list_containers() -> str:
    """List all Docker containers (running and stopped) with their status."""
    r = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
    return r.stdout or r.stderr

@function_tool
def get_container_logs(container_name: str) -> str:
    """Get the last 100 lines of logs from a Docker container."""
    r = subprocess.run(
        ["docker", "logs", "--tail", "100", container_name],
        capture_output=True, text=True
    )
    return r.stdout + r.stderr

@function_tool
def inspect_container(container_name: str) -> str:
    """Get detailed info about a Docker container: state, config, mounts, network."""
    r = subprocess.run(
        ["docker", "inspect", container_name],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr

@function_tool
def restart_container(container_name: str, reason: str) -> str:
    """Restart a Docker container. ALWAYS get explicit user approval before calling.
    Never call this without the user saying yes."""
    if not Config.DOCKER_ENABLED:
        return f"[SIMULATED] docker restart {container_name}\nReason: {reason}"
    r = subprocess.run(
        ["docker", "restart", container_name],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr
```

---

## github_tools.py

```python
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
    return out[:5000] + "\n[truncated]" if len(out) > 5000 else out

@function_tool
def get_workflow_file(workflow_name: str) -> str:
    """Read a GitHub Actions workflow YAML file. Pass filename like 'ci.yml'."""
    path = Path(f".github/workflows/{workflow_name}")
    return path.read_text() if path.exists() else f"Not found: {path}"
```

---

## healing_tools.py

```python
import subprocess
from agents import function_tool
from src.config import Config

@function_tool
def fix_image(resource_type: str, resource_name: str, namespace: str, correct_image: str, reason: str) -> str:
    """Patch a Kubernetes resource to fix a wrong container image.
    ALWAYS get explicit user approval before calling."""
    if not Config.K8S_ENABLED:
        return f"[SIMULATED] kubectl set image {resource_type}/{resource_name} app={correct_image} -n {namespace}\nReason: {reason}"
    r = subprocess.run(
        ["kubectl", "set", "image", f"{resource_type}/{resource_name}",
         f"app={correct_image}", "-n", namespace],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr

@function_tool
def patch_resources(resource_type: str, resource_name: str, namespace: str, memory_limit: str, reason: str) -> str:
    """Patch memory limits on a Kubernetes resource.
    ALWAYS get explicit user approval before calling."""
    patch = f'{{"spec":{{"template":{{"spec":{{"containers":[{{"name":"app","resources":{{"limits":{{"memory":"{memory_limit}"}}}}}}]}}}}}}}}'
    if not Config.K8S_ENABLED:
        return f"[SIMULATED] kubectl patch {resource_type} {resource_name} -n {namespace}\nPatch: {patch}\nReason: {reason}"
    r = subprocess.run(
        ["kubectl", "patch", resource_type, resource_name, "-n", namespace,
         "--patch", patch],
        capture_output=True, text=True
    )
    return r.stdout or r.stderr

@function_tool
def cache_clear(service_name: str, reason: str) -> str:
    """Simulate clearing application cache for a service.
    ALWAYS get explicit user approval before calling."""
    return f"[SIMULATED] Cache cleared for {service_name}.\nReason: {reason}"

@function_tool
def disk_cleanup(path: str, reason: str) -> str:
    """Simulate disk cleanup at a path.
    ALWAYS get explicit user approval before calling."""
    return f"[SIMULATED] Disk cleanup at {path}.\nReason: {reason}"
```

---

## mcp_server.py

```python
"""
MCP Server — exposes all DevOps tools via Model Context Protocol.
Works with Claude Desktop, VS Code, Cursor, any MCP client.
Run: uv run python mcp_server.py
"""
import subprocess
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("DevOps Tools")

@mcp.tool
def list_pods(namespace: str = "default") -> str:
    """List all pods in a Kubernetes namespace."""
    r = subprocess.run(["kubectl", "get", "pods", "-n", namespace], capture_output=True, text=True)
    return r.stdout or r.stderr

@mcp.tool
def describe_pod(pod_name: str, namespace: str = "default") -> str:
    """Describe a Kubernetes pod including events."""
    r = subprocess.run(["kubectl", "describe", "pod", pod_name, "-n", namespace], capture_output=True, text=True)
    return r.stdout or r.stderr

@mcp.tool
def get_k8s_events(namespace: str = "default") -> str:
    """Get recent Kubernetes events sorted by timestamp."""
    r = subprocess.run(["kubectl", "get", "events", "-n", namespace, "--sort-by=.lastTimestamp"], capture_output=True, text=True)
    return r.stdout or r.stderr

@mcp.tool
def list_containers() -> str:
    """List all Docker containers."""
    r = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
    return r.stdout or r.stderr

@mcp.tool
def get_container_logs(container_name: str) -> str:
    """Get logs from a Docker container."""
    r = subprocess.run(["docker", "logs", "--tail", "100", container_name], capture_output=True, text=True)
    return r.stdout + r.stderr

@mcp.tool
def list_workflow_runs(status: str = "failure") -> str:
    """List recent GitHub Actions workflow runs."""
    r = subprocess.run(["gh", "run", "list", "--status", status, "--limit", "5"], capture_output=True, text=True)
    return r.stdout or r.stderr

if __name__ == "__main__":
    mcp.run()
```

---

## app.py additions — Level 4 UI

```python
# Add run_async helper at top of app.py (replaces asyncio.run everywhere)
import asyncio
import concurrent.futures

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

# Structured incident card
def render_incident_card(severity: str, system: str, resource: str, cause: str):
    color = {"P1": "🔴", "P2": "🟠", "P3": "🟡", "Info": "🔵"}.get(severity, "⚪")
    st.markdown(f"""
| Field | Value |
|---|---|
| Severity | {color} **{severity}** |
| System | `{system}` |
| Resource | `{resource}` |
| Cause | {cause} |
    """)

# Sidebar — show all tool status
def display_sidebar():
    with st.sidebar:
        st.title("🚨 AI Incident Responder")
        st.caption("Agents SDK · LiteLLM · Gemini → Groq fallback")
        st.markdown("---")
        st.subheader("Connected Tools")
        st.success("📋 Log Tools ✓")
        st.success("🐳 Docker ✓") if Config.DOCKER_ENABLED else st.warning("🐳 Docker ⚠ simulation")
        st.success("☸️ Kubernetes ✓") if Config.K8S_ENABLED else st.warning("☸️ K8s ⚠ simulation")
        st.success("🐙 GitHub CLI ✓") if Config.GITHUB_TOKEN else st.warning("🐙 GitHub ⚠ no token")
        st.success("🔌 MCP ✓") if Config.MCP_ENABLED else st.warning("🔌 MCP ⚠ disabled")
        st.markdown("---")
        st.caption(f"Model: `{Config.GEMINI_MODEL}`")
        st.caption(f"Fallback: `{Config.FALLBACK_MODELS[0]}`")
```

---

## pyproject.toml — Level 4

```toml
[project]
name = "ai-logging-system"
version = "0.4.0"
requires-python = ">=3.12"
dependencies = [
    "openai-agents[litellm]>=0.0.19",
    "python-dotenv",
    "streamlit",
    "fastmcp",
]
```

---

## Start & Test — Level 4

### Prerequisites

```bash
# Verify Docker is running
docker ps

# Verify kubectl is available (simulation mode works without a real cluster)
kubectl version --client

# Verify GitHub CLI is installed and authenticated
gh auth status

# Install dependencies
cd 04-multi-tool
uv sync
```

### Create broken test fixtures

```bash
# Broken Docker container (exits after 2 seconds)
docker run -d --name broken-app nginx:alpine sh -c "echo 'starting...' && sleep 2 && exit 1"

# Verify it is crash-looping
docker ps -a
# You should see broken-app with status "Exited (1)"

# (Optional) broken K8s pod — only if kubectl points to a real cluster
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: broken-pod
  namespace: default
spec:
  containers:
  - name: app
    image: nginx:alpine
    command: ["sh", "-c", "echo 'starting...' && sleep 2 && exit 1"]
EOF
```

### Run the app

```bash
uv run streamlit run app.py
```

**Browser:** http://localhost:8501

### Test commands (type in chat)

```
# Docker scenario
Why is broken-app crashing?
# Expected: agent calls list_containers + get_container_logs, diagnoses exit code 1

yes
# Expected: simulated restart (or real if DOCKER_ENABLED=true)

# K8s scenario (simulation mode)
Check k8s-java-app.log for issues
# Expected: P1 OOM diagnosis + restart recommendation + approval prompt

# GitHub scenario
Show me recent failed GitHub Actions runs
# Expected: calls list_workflow_runs, lists failures

What went wrong in run <id from above>?
# Expected: calls get_failed_logs, explains the failure

# Healing scenario
The memory-hog pod is OOMKilled, fix it
# Expected: recommends patch_resources, asks approval before doing anything
```

### Run MCP server separately (for Claude Desktop)

```bash
# Terminal 2
uv run python mcp_server.py
```

**Claude Desktop config** (`~/.config/Claude/claude_desktop_config.json` on Linux):
```json
{
  "mcpServers": {
    "devops-tools": {
      "command": "/absolute/path/to/04-multi-tool/.venv/bin/python3",
      "args": ["/absolute/path/to/04-multi-tool/mcp_server.py"]
    }
  }
}
```
Fully quit and reopen Claude Desktop. You should see 6 tools available.

### Cleanup

```bash
docker rm -f broken-app
kubectl delete pod broken-pod --ignore-not-found
```

---

---

# LEVEL 5 — Temporal Durable Execution

**What it adds over Level 4:**
- Temporal workflows wrap every agent action — crash-proof, retryable
- Kill the worker mid-diagnosis, restart it, it resumes exactly where it left off
- Full audit trail in Temporal UI
- Auto-heal mode via `starter.py`
- Streamlit shows workflow run status live — running / completed / failed

---

## Checklist — Level 5

- [ ] Install Temporal CLI
- [ ] Add `temporalio` to `pyproject.toml` and run `uv sync`
- [ ] `workflows/heal_workflow.py` — `HealingWorkflow` with approval signal
- [ ] `activities/k8s_activities.py` — each K8s tool call as a Temporal activity
- [ ] `worker.py` — registers workflows + activities, stays running
- [ ] `starter.py` — triggers auto-heal without UI interaction
- [ ] Update `app.py` — show workflow run ID + status panel in sidebar
- [ ] Fallback pattern still applies inside `call_claude` activity
- [ ] Test crash recovery scenario before marking done
- [ ] Test Temporal UI audit trail before marking done

---

## workflows/heal_workflow.py

```python
from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
import asyncio

@workflow.defn
class HealingWorkflow:
    def __init__(self):
        self._approved = False

    @workflow.run
    async def run(self, pod_name: str, namespace: str) -> str:
        logs = await workflow.execute_activity(
            "get_pod_logs",
            args=[pod_name, namespace],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        diagnosis = await workflow.execute_activity(
            "call_claude_diagnose",
            args=[logs],
            start_to_close_timeout=timedelta(seconds=60),
        )
        # Pause here — wait for user to send approval signal from UI
        await workflow.wait_condition(lambda: self._approved)
        result = await workflow.execute_activity(
            "execute_fix",
            args=[pod_name, namespace, diagnosis],
            start_to_close_timeout=timedelta(seconds=30),
        )
        return result

    @workflow.signal
    def approve(self):
        self._approved = True
```

---

## worker.py

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.heal_workflow import HealingWorkflow
from activities.k8s_activities import get_pod_logs, call_claude_diagnose, execute_fix

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="healing-queue",
        workflows=[HealingWorkflow],
        activities=[get_pod_logs, call_claude_diagnose, execute_fix],
    )
    print("[OK] KubeHealer worker running — Ctrl+C to stop")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## pyproject.toml — Level 5

```toml
[project]
name = "ai-logging-system"
version = "0.5.0"
requires-python = ">=3.12"
dependencies = [
    "openai-agents[litellm]>=0.0.19",
    "python-dotenv",
    "streamlit",
    "fastmcp",
    "temporalio",
]
```

---

## Start & Test — Level 5

### Prerequisites

```bash
# Install Temporal CLI
# Linux:
curl -sSf https://temporal.download/cli.sh | sh

# Verify
temporal --version

# Install dependencies
cd 05-temporal
uv sync
```

### Start everything (4 terminals)

```bash
# Terminal 1 — Temporal server
temporal server start-dev
# Wait for: "Temporal server is running"

# Terminal 2 — Worker
uv run python worker.py
# Wait for: "[OK] KubeHealer worker running"

# Terminal 3 — Streamlit UI
uv run streamlit run app.py

# Terminal 4 — (optional) watch pods heal in real time
kubectl get pods -w
```

**Browsers:**
- Streamlit UI: http://localhost:8501
- Temporal UI: http://localhost:8233

### Test commands

```bash
# In Streamlit chat:
Heal my cluster
# Expected: agent scans pods, diagnoses each, shows findings

approve all fixes
# Expected: sends approval signal to Temporal workflow, fixes execute

# Crash recovery test:
# 1. Start healing in chat
# 2. Go to Terminal 2 (worker) → Ctrl+C to kill it
# 3. Open http://localhost:8233 → workflow shows "Running" with some activities done
# 4. Restart worker: uv run python worker.py
# 5. Workflow resumes — completed activities are NOT re-run

# Auto-heal without UI:
uv run python starter.py
```

### Cleanup

```bash
kind delete cluster --name kubehealer
# Stop Temporal: Ctrl+C in Terminal 1
# Stop worker: Ctrl+C in Terminal 2
```

---

---

# LEVEL 6 — Full AIOps Platform (Multi-Agent)

**What it adds over Level 5:**
- Multi-agent orchestration — Triage Agent routes to K8s / Docker / GitHub / Healer specialist
- Each agent has its own system prompt and constrained tool set — cannot call other agents' tools
- Live handoff shown in UI — which agent is active updates in real time
- Persistent incident log saved to `incidents.json`
- Export incident report as markdown

---

## Checklist — Level 6

- [ ] `agents/triage_agent.py` — classifies environment, never diagnoses itself
- [ ] `agents/k8s_agent.py` — K8s specialist, K8s tools only
- [ ] `agents/docker_agent.py` — Docker specialist, Docker tools only
- [ ] `agents/github_agent.py` — CI/CD specialist, GitHub tools only
- [ ] `agents/healer_agent.py` — executes approved fixes only, no analysis tools
- [ ] Handoff wiring in `log_analyzer.py` using OpenAI Agents SDK `handoff()`
- [ ] `incident_store.py` — append every incident to `incidents.json`
- [ ] Update `app.py` — active agent name shown live, handoff animation, incident log panel
- [ ] Guardrails enforced per agent — each agent's instructions name its allowed tools explicitly
- [ ] Test routing: Docker question → Docker agent; K8s question → K8s agent
- [ ] Test handoff visible in UI before marking done

---

## Multi-agent wiring — log_analyzer.py

```python
from agents import Agent, Runner, handoff, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from src.config import Config
from src.tools.k8s_tools import list_pods, describe_pod, restart_kubernetes_pod, fix_image, patch_resources
from src.tools.docker_tools import list_containers, get_container_logs, inspect_container, restart_container
from src.tools.github_tools import list_workflow_runs, get_failed_logs, get_workflow_file
from src.tools.healing_tools import cache_clear, disk_cleanup

set_tracing_disabled(disabled=True)

def _make_model(model_name: str) -> LitellmModel:
    api_key = Config.GROQ_API_KEY if model_name.startswith("groq/") else Config.GEMINI_API_KEY
    return LitellmModel(model=model_name, api_key=api_key)

k8s_agent = Agent(
    name="K8s Specialist",
    instructions="Diagnose Kubernetes issues only. Use only K8s tools. Never call Docker or GitHub tools.",
    model=_make_model(Config.GEMINI_MODEL),
    tools=[list_pods, describe_pod, restart_kubernetes_pod, fix_image, patch_resources],
)

docker_agent = Agent(
    name="Docker Specialist",
    instructions="Diagnose Docker issues only. Use only Docker tools. Never call K8s or GitHub tools.",
    model=_make_model(Config.GEMINI_MODEL),
    tools=[list_containers, get_container_logs, inspect_container, restart_container],
)

github_agent = Agent(
    name="GitHub Specialist",
    instructions="Diagnose GitHub Actions CI/CD failures only. Use only GitHub tools.",
    model=_make_model(Config.GEMINI_MODEL),
    tools=[list_workflow_runs, get_failed_logs, get_workflow_file],
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You are the first responder. Read the user's question and immediately hand off to the right specialist.
    - Kubernetes / k8s / pod / namespace / OOM / CrashLoop → K8s Specialist
    - Docker / container / docker run → Docker Specialist
    - GitHub / CI / workflow / Actions / pipeline → GitHub Specialist
    Never diagnose yourself. Never use tools yourself. Always hand off immediately.
    """,
    model=_make_model(Config.GEMINI_MODEL),
    handoffs=[handoff(k8s_agent), handoff(docker_agent), handoff(github_agent)],
)

class LogAnalyzerAgent:
    def __init__(self):
        self.primary_model = Config.GEMINI_MODEL
        self.fallbacks = Config.FALLBACK_MODELS

    async def process_query(self, user_input: str) -> str:
        models_to_try = [self.primary_model] + self.fallbacks
        for model in models_to_try:
            try:
                result = await Runner.run(triage_agent, input=user_input)
                return str(getattr(result, "final_output", "No response.")).strip()
            except Exception as e:
                err = str(e).lower()
                if any(x in err for x in ["429", "quota", "rate limit", "503"]):
                    continue
                return f"Error: {e}"
        return "All models exhausted. Check API keys and quotas."
```

---

## Active agent display — app.py addition

```python
AGENT_COLORS = {
    "Triage Agent": "🟣",
    "K8s Specialist": "☸️",
    "Docker Specialist": "🐳",
    "GitHub Specialist": "🐙",
    "Healer Agent": "🔧",
}

# In handle_input, show which agent is active inside st.status:
with st.status("🔍 Analysing...", expanded=True) as status:
    st.write("🟣 Triage Agent — classifying issue...")
    response = run_async(get_response(user_input))
    # Parse agent name from response metadata if available, else show generic
    active = st.session_state.get("last_agent", "Specialist Agent")
    icon = AGENT_COLORS.get(active, "🤖")
    status.update(label=f"✅ {icon} {active} completed", state="complete", expanded=False)
```

---

## pyproject.toml — Level 6

```toml
[project]
name = "ai-logging-system"
version = "0.6.0"
requires-python = ">=3.12"
dependencies = [
    "openai-agents[litellm]>=0.0.19",
    "python-dotenv",
    "streamlit",
    "fastmcp",
    "temporalio",
]
```

---

## Start & Test — Level 6

### Prerequisites

```bash
cd 06-full-agentic
uv sync

# Ensure broken fixtures exist for routing tests
docker run -d --name broken-app nginx:alpine sh -c "sleep 2 && exit 1"
```

### Start

```bash
# Terminal 1 — Temporal (if using Level 5 Temporal features)
temporal server start-dev

# Terminal 2 — Worker (if using Level 5 Temporal features)
uv run python worker.py

# Terminal 3 — Streamlit
uv run streamlit run app.py
```

**Browser:** http://localhost:8501  
**Temporal UI:** http://localhost:8233

### Test commands

```bash
# Routing tests — verify triage hands off to the right agent
Why is broken-app crashing?
# Expected: UI shows "🐳 Docker Specialist" active, Docker tools called

Check k8s-java-app.log for issues
# Expected: UI shows "☸️ K8s Specialist" active, P1 classification

Show me recent GitHub Actions failures
# Expected: UI shows "🐙 GitHub Specialist" active, workflow runs listed

# Guardrail tests
Restart the broken-app container
# Expected: agent asks for confirmation, does NOT restart immediately

Delete all pods in production
# Expected: agent refuses — outside constrained action space

# Incident log test
cat incidents.json
# Expected: every incident appended with timestamp, severity, resource, action taken
```

### Cleanup

```bash
docker rm -f broken-app
kind delete cluster --name devops-demo
# Stop Temporal and worker with Ctrl+C
```

---

---

## Global Rules (Gemini must never violate these)

1. **Never use LangChain** — always OpenAI Agents SDK + LiteLLM
2. **Never call destructive tools without user approval** — enforced in system_prompt + tool docstrings
3. **Always try Gemini first, fall back to Groq on 429/quota** — use the fallback loop above
4. **Always show live agent activity** — `st.status()` with `st.write()` steps inside, never a plain spinner
5. **Guardrails in every system_prompt.txt** — copy the guardrails block verbatim at every level
6. **Anti-glitch rules always apply** — use `run_async()`, append messages after render, gate agent init behind session_state
7. **Each level is a separate folder** — `03-decision-making/`, `04-multi-tool/`, `05-temporal/`, `06-full-agentic/`
8. **MCP server updated at every level** — always exposes all tools for that level
9. **`st.set_page_config()` called once, first line of app.py** — never inside a function or conditional

---

## Quick Verification Table

| Level | Start command | Browser | Key test |
|---|---|---|---|
| 3 ✅ | `uv run streamlit run app.py` | :8501 | OOM log → P1 → approval → simulated restart |
| 4 | `uv run streamlit run app.py` | :8501 | Docker broken container → diagnose → approve → restart |
| 4 MCP | `uv run python mcp_server.py` | Claude Desktop | 6 tools visible in Claude Desktop |
| 5 | Temporal + worker + streamlit | :8501 + :8233 | Kill worker mid-workflow → restart → resumes |
| 6 | Temporal + worker + streamlit | :8501 + :8233 | Docker question → Docker agent in UI; K8s question → K8s agent |
