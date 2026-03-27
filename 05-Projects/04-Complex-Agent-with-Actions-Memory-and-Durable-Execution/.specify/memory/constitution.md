<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- List of modified principles:
  - Principles updated and expanded with specific deliverables and architecture details from constitution.txt.
- Added sections:
  - Core Deliverables (Section 2 from source)
  - User Stories (Section 6 from source)
  - Detailed Definition of Done (Section 9 from source)
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ verified)
  - .specify/templates/spec-template.md (✅ verified)
  - .specify/templates/tasks-template.md (✅ verified)
- Follow-up TODOs: none
-->

# Level 4 AI Logging Agent Constitution

## 1. Mission
Build a production-grade AI incident response agent that detects, classifies, and remediates
infrastructure failures with human oversight. The system must feel like a real DevOps tool — fast,
observable, and trustworthy — not a demo. Every action must be auditable. No action must happen
without human approval.

## 2. Core Principles

### I. Mission-Driven Incident Response
The agent focuses on production-grade reliability. Every action must be auditable, and no remediation
steps are taken without explicit human approval via the dedicated gate.

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

## 3. Core Deliverables
1. A Streamlit chat interface that starts Temporal workflows and sends approval signals.
2. A Temporal-orchestrated incident response pipeline with durable execution and full audit trail.
3. An AI agent (OpenAI Agents SDK + Gemini via LiteLLM) that correlates logs across multiple pods.
4. MCP-connected tools for AWS RDS reboot and Slack notifications with safe placeholder fallback.
5. SQLite pattern memory that recognizes recurring incidents and surfaces known fixes.
6. A human approval gate enforced at three layers — system prompt, tool docstring, and Temporal Signal.

## 4. User Stories
1. As an on-call engineer, I want the agent to read all pod logs and correlate the issue across the
   cluster so I have full context before making a decision.
2. As an on-call engineer, I want the team to be alerted on Slack automatically before I am asked
   to approve any action.
3. As an on-call engineer, I want to type `yes` or `no` in a chat interface and have the system
   respond accordingly without any ambiguity.
4. As an on-call engineer, I want every step of the incident response recorded so I can audit what
   happened and why.
5. As an on-call engineer, I want the agent to tell me if it has seen this problem before and what
   fixed it last time.
6. As a developer, I want to run the whole system locally without any cloud accounts configured.

## 5. Success Criteria
- Agent correctly identifies connection pool exhaustion across all three pods from log evidence.
- Slack alert is sent before any infrastructure action is proposed.
- Workflow pauses durably at the approval gate — zero CPU consumed while waiting.
- Typing `yes` sends a Temporal Signal and triggers RDS reboot activity.
- Typing `no` ends the workflow cleanly with no action taken.
- Temporal UI at `localhost:8233` shows full event history for every workflow execution.
- Pattern memory correctly surfaces prior incident context on second run of the same issue.
- All five verification tests in Phase 15 pass before the level is marked complete.

## 6. Non-Goals & Risks

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
- **Risk**: Workflow approval timeout. **Mitigation**: 30-minute timeout; workflow ends cleanly.

## 7. Governance

### Amendment Procedure
Constitution supersedes all other practices. Amendments require documentation and approval. All PRs
and reviews must verify compliance with core principles, especially the approval gate.

### Versioning Policy
- MAJOR: Incompatible principle changes or removals.
- MINOR: New principle/section additions or material expansions.
- PATCH: Clarifications and wording fixes.

### Compliance Review
Definition of Done requires all Phase 15 tests to pass and Temporal UI event history verification.
AGENTS.md must be deleted and DONE.md created upon completion.

## 8. Definition of Done
- All phases in AGENTS.md completed in order.
- All three processes running: `temporal server start-dev`, `worker.py`, `app.py`.
- All five tests in Phase 15 pass.
- Temporal UI shows complete event history for at least two workflow executions.
- SQLite `data/incidents.db` exists and contains at least one incident record.
- Second run of the same incident shows pattern memory context in the agent response.
- AGENTS.md deleted from the project folder.
- DONE.md created with the summary of what was built.

**Version**: 1.1.0 | **Ratified**: 2026-03-26 | **Last Amended**: 2026-03-27
