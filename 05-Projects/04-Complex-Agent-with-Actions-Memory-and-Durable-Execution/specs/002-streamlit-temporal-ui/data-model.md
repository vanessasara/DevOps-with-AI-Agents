# Data Model: Streamlit-Temporal UI

## Entities

### IncidentWorkflow
- **Workflow ID**: Unique identifier (UUID or incident-based slug).
- **Status**: RUNNING, COMPLETED, FAILED, TIMED_OUT.
- **Start Time**: Timestamp of when the on-call engineer initiated.
- **Last Event**: Most recent activity completion or signal received.

### ApprovalSignal
- **Signal Name**: `approval`.
- **Payload**: `bool` (True for yes, False for no).
- **Sender**: `on-call engineer` (via chat UI).
- **Received At**: Timestamp recorded by Temporal.

### AuditTrail
- **Events**: List of `WorkflowEvent`.
- **WorkflowEvent**:
  - `type`: ActivityStarted, ActivityCompleted, SignalReceived, MarkerAdded.
  - `message`: Text description for display in Streamlit chat.
  - `timestamp`: UTC.

## State Transitions
1. **PENDING**: Workflow started, awaiting diagnosis activities.
2. **WAITING_APPROVAL**: Diagnosis complete, paused for `approval` signal.
3. **EXECUTING**: Signal "yes" received, remediation activities running.
4. **TERMINATED**: Signal "no" received or timeout occurred.
5. **FINAL**: Result recorded in SQLite memory and UI.
