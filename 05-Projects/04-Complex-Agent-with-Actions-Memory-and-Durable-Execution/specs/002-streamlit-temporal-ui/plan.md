# Implementation Plan: Streamlit-Temporal UI

**Branch**: `002-streamlit-temporal-ui` | **Date**: 2026-03-26 | **Spec**: [specs/002-streamlit-temporal-ui/spec.md]
**Input**: Feature specification from `/specs/002-streamlit-temporal-ui/spec.md`

## Summary
Build a Streamlit-based chat interface that acts as the primary user gateway to Temporal workflows. It allows starting workflows for incident diagnosis and sending human approval signals (yes/no) to manage destructive remediations safely.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: `streamlit`, `temporalio`, `pydantic`, `litellm`
**Storage**: Temporal (for workflow state), SQLite (for pattern memory)
**Testing**: `pytest`
**Target Platform**: Local laptop (Linux)
**Project Type**: Single project
**Performance Goals**: Start workflow < 2s, Signal delivery < 1s
**Constraints**: No cloud credentials required, full audibility via Temporal History
**Scale/Scope**: Local incident response agent

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **Mission-Driven**: Auditable actions, human oversight via signals.
- [X] **Layers**: UI (`app.py`), Temporal (`worker.py`), Agent (`src/agents/`).
- [X] **Placeholder Mode**: `config.py` detects missing credentials.
- [X] **Temporal-Driven**: Temporal handles durability and audit.
- [X] **Multi-Layer Approval Gate**: Signal-based hard gate.
- [X] **Minimalist Data**: SQLite for memory, `uv` for packages.

## Project Structure

### Documentation (this feature)

```text
specs/002-streamlit-temporal-ui/
├── plan.md              # This file
├── research.md          # Decision log (Polling, SessionState, Signals)
├── data-model.md        # IncidentWorkflow, ApprovalSignal entities
├── quickstart.md        # Run instructions
├── contracts/           # UI -> Temporal client contract
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
app.py                  ← Streamlit UI main entry point
worker.py               ← Temporal worker registration
src/
├── config.py           ← Environment and placeholder configuration
├── workflows/          ← Workflow and activity definitions
└── agents/             ← Agent logic and Temporal client proxy
```

**Structure Decision**: Single-project structure with clear separation between UI, Worker, and Source modules.
