<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- List of modified principles:
  - [PRINCIPLE_1_NAME] → I. Mission-Driven Incident Response
  - [PRINCIPLE_2_NAME] → II. Layers and Separation of Concerns
  - [PRINCIPLE_3_NAME] → III. Placeholder Mode (Safe Fallbacks)
  - [PRINCIPLE_4_NAME] → IV. Temporal-Driven Durability & Audit
  - [PRINCIPLE_5_NAME] → V. Multi-Layer Human Approval Gate
  - [PRINCIPLE_6_NAME] → VI. Minimalist Data & Infrastructure
- Added sections: Operational Constraints & Success Criteria, Non-Goals & Risks
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated - check logic aligns)
  - .specify/templates/spec-template.md (✅ updated - requirements align)
  - .specify/templates/tasks-template.md (✅ updated - task types align)
- Follow-up TODOs: none
-->

# Level 4 AI Logging Agent Constitution

## Core Principles

### I. Mission-Driven Incident Response
Build a production-grade AI incident response agent that detects, classifies, and remediates
infrastructure failures with human oversight. The system must feel like a real DevOps tool — fast,
observable, and trustworthy — not a demo. Every action must be auditable. No action must happen
without human approval.

### II. Layers and Separation of Concerns
Layers never reach across each other. Tools do not know about workflows. Workflows do not import
from `app.py`. The agent does not know about Temporal. Each layer has one job. Folder structure
must strictly follow the defined hierarchy.

### III. Placeholder Mode (Safe Fallbacks)
AWS, Slack, and Kubernetes all run in simulation mode when credentials are not configured. The
agent still receives a response and can complete its reasoning. Nothing breaks. Nothing is hidden.
This ensures the system is testable in any environment.

### IV. Temporal-Driven Durability & Audit
The workflow is the source of truth for what happened. Not logs. Not print statements. The
Temporal event history is the audit trail. Every activity input and output is stored
automatically. Durability is owned by Temporal.

### V. Multi-Layer Human Approval Gate
Human approval is required for every destructive action, always. This is enforced at three layers:
system prompt, tool docstring, and Temporal Signal. One layer failing does not compromise the
others. Typing `yes` or `no` in the UI must be unambiguous.

### VI. Minimalist Data & Infrastructure
SQLite is the only database for pattern memory. `uv` is used for package management. No external
database dependencies, no Docker required for development. The system must run fully on a laptop
without cloud credentials.

## Operational Constraints & Success Criteria

### Constraints
- Must run fully on a laptop without cloud credentials (placeholder mode).
- Temporal must be started with `temporal server start-dev`.
- SQLite only — no external database dependencies.
- `uv` for package management.
- K8S_ENABLED=false by default.
- All five verification tests in Phase 15 must pass.

### Success Criteria
- Agent identifies connection pool exhaustion across pods from log evidence.
- Slack alert sent before any infrastructure action is proposed.
- Workflow pauses durably at the approval gate (zero CPU consumed while waiting).
- Temporal UI shows full event history for every workflow execution.
- Pattern memory surfaces prior incident context.

## Non-Goals & Risks

### Non-Goals
- No autonomous execution — human approval is ALWAYS required.
- No frontend beyond Streamlit at this level.
- No distributed agent teams or cloud deployment.
- No authentication or multi-user support.
- No real-time log streaming (file-based logs only).

### Risks & Mitigations
- **Risk**: Agent calls reboot without approval. **Mitigation**: Three-layer gate (prompt +
  docstring + Signal).
- **Risk**: Temporal/Worker not running. **Mitigation**: Documented start order and verification
  tests.
- **Risk**: Missing credentials. **Mitigation**: Placeholder mode detection in config.

## Governance

### Amendment Procedure
Constitution supersedes all other practices. Amendments require documentation and approval. All PRs
and reviews must verify compliance with core principles, especially the approval gate.

### Versioning Policy
- MAJOR: Incompatible principle changes or removals.
- MINOR: New principle/section additions.
- PATCH: Clarifications and wording fixes.

### Compliance Review
Definition of Done requires all Phase 15 tests to pass and Temporal UI event history verification.
AGENTS.md must be deleted and DONE.md created upon completion.

**Version**: 1.0.0 | **Ratified**: 2026-03-26 | **Last Amended**: 2026-03-26
