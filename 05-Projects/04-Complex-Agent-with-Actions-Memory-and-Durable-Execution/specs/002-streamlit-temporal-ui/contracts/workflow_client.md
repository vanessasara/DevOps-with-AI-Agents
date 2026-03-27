# Contract: UI -> Temporal Client Proxy

## TemporalClientProxy Interface

### `start_incident_workflow(workflow_id: str) -> WorkflowHandle`
- **Description**: Connects to Temporal and starts `IncidentWorkflow`.
- **Input**: Unique string for workflow identification.
- **Output**: Returns a handle to the running workflow.
- **Error**: `TemporalConnectionError` if server is unreachable.

### `send_approval_signal(workflow_id: str, approved: bool) -> None`
- **Description**: Sends a "yes/no" signal to the specified workflow.
- **Input**: `workflow_id` (str), `approved` (bool).
- **Output**: None (void).
- **Error**: `WorkflowNotFoundError` if the handle is invalid or expired.

### `get_workflow_status(workflow_id: str) -> WorkflowStatus`
- **Description**: Polled by the UI to update the status and history.
- **Input**: `workflow_id`.
- **Output**:
  - `status`: RUNNING | COMPLETED | FAILED.
  - `history`: List of activity log messages.
  - `waiting_for_approval`: Boolean.
