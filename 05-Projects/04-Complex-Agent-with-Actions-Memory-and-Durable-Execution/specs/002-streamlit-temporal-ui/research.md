# Research: Streamlit-Temporal UI

## Decision: Background Polling for UI Updates
- **Chosen**: Streamlit `st.fragment` or `st.empty` with a `while True` loop and `time.sleep` (or `st.rerun` at an interval).
- **Rationale**: Streamlit does not support native push from a server. Polling the Temporal Client for workflow status is the most reliable way to update the chat UI with activity logs.
- **Alternatives Considered**: 
  - WebSockets: Overly complex for a local DevOps tool; not natively supported in Streamlit's model without external components.
  - Streamlit `st_autorefresh`: Third-party component, avoid external dependencies where possible.

## Decision: Temporal Client Session Management
- **Chosen**: Store the `TemporalClient` instance in `st.session_state`.
- **Rationale**: Connecting to Temporal on every rerun is inefficient. Maintaining a single persistent client per session ensures lower latency for signal delivery and status checks.
- **Alternatives Considered**: Global client instance (risky in multi-user Streamlit, though not a current non-goal).

## Decision: Three-Layer Approval Gate Implementation
- **Chosen**:
  1. **Prompt**: "Always ask for approval before calling destructive tools."
  2. **Docstring**: "DO NOT call this tool unless the user has explicitly typed 'yes'."
  3. **Signal**: The Temporal workflow pauses at `workflow.wait_condition` until a "yes/no" signal is received.
- **Rationale**: Aligns strictly with Principle V of the Constitution.
- **Alternatives Considered**: Single layer UI-only check (rejected as unsafe).

## Decision: Workflow Persistence in UI
- **Chosen**: SQLite session history for the chat + Temporal History for the workflow state.
- **Rationale**: `st.session_state` is lost on browser refresh. SQLite ensures the chat log persists (FR-006).
