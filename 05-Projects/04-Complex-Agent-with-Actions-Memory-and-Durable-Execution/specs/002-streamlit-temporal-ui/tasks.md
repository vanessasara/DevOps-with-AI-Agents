# Tasks: Level 4 AI Logging Agent

**Constitution**: `constitution.txt`
**Goal**: Production-grade AI incident response agent with human approval gate

---

## Phase 1: Core Infrastructure ✓ (Complete)

- [X] Project structure: `src/`, `app.py`, `worker.py`
- [X] Dependencies: `uv` with `streamlit`, `temporalio`, `pydantic`, `litellm`
- [X] `.gitignore` for Python artifacts
- [X] Basic Temporal workflow with signal approval

---

## Phase 2: Agent & Tools ✓ (Complete)

- [X] Add `openai` package for OpenAI Agents SDK
- [X] Add `mcp` package for tool connectivity
- [X] Run `uv sync`
- [X] Create `system_prompt.txt` with three-layer approval instructions
- [X] Include: "Never execute destructive actions without human approval"
- [X] Include: "Read all log files before drawing conclusions"
- [X] Create `src/tools/__init__.py`
- [X] Create `src/tools/aws_tools.py` with placeholder RDS reboot function
- [X] Create `src/tools/slack_tools.py` with placeholder notification function
- [X] Add `@function_tool` docstrings requiring human approval
- [X] Create `src/agents/incident_agent.py` using OpenAI Agents SDK (via LiteLLM)
- [X] Connect agent to LiteLLM for Gemini fallback
- [X] Load system prompt from `system_prompt.txt`
- [X] Register tools with agent

---

## Phase 3: Pattern Memory ✓ (Complete)

- [X] Create `src/memory/__init__.py`
- [X] Create `src/memory/pattern_store.py` with SQLite connection
- [X] Create `incidents` table schema (id, pattern, resolution, timestamp)
- [X] Memory Functions: `save_incident` and `get_context_for_agent`

---

## Phase 4: Sample Logs ✓ (Complete)

- [X] Create `logs/pod-1.log` with connection pool exhaustion errors
- [X] Create `logs/pod-2.log` with connection pool exhaustion errors
- [X] Create `logs/pod-3.log` with connection pool exhaustion errors
- [X] Ensure logs show correlation pattern (same error across pods)

---

## Phase 5: Enhanced Workflow ✓ (Complete)

- [X] Create `src/workflows/activities.py` with log reading, analysis, and tools
- [X] Update `src/workflows/incident_workflow.py` to sequence activities and signals
- [X] Update `worker.py` to register new activities

---

## Phase 6: UI Integration ✓ (Complete)

- [X] Update `app.py` to display progress, handle signals, and show pattern memory

---

## Phase 7: Verification Tests ✓ (Complete)

- [X] Test 1: Agent identifies connection pool exhaustion across all 3 pods
- [X] Test 2: Slack alert sent before infrastructure action proposed
- [X] Test 3: Workflow pauses durably at approval gate
- [X] Test 4: `yes` signal triggers RDS reboot, `no` ends cleanly
- [X] Test 5: Pattern memory surfaces context on second run

---

## Progress Tracking

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Core Infrastructure | ✓ Complete | Basic workflow works |
| 2. Agent & Tools | ✓ Complete | Agent + Tools integrated |
| 3. Pattern Memory | ✓ Complete | SQLite storage ready |
| 4. Sample Logs | ✓ Complete | Correlation logs created |
| 5. Enhanced Workflow | ✓ Complete | Complex workflow logic |
| 6. UI Integration | ✓ Complete | Interactive Streamlit UI |
| 7. Verification | ✓ Complete | All core tests pass |
