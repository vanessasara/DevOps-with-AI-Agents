# Contract: Workflow Client (UI -> Temporal)

## Purpose
Defines how the Streamlit UI interacts with the Temporal service to manage workflows.

## Interface: `TemporalClientProxy`

### `start_incident_workflow(incident_type: str) -> str`
Initiates a new `IncidentWorkflow` and returns the `workflow_id`.
- **Input**: `incident_type` (e.g., "reboot-rds")
- **Output**: `workflow_id` (string)
- **Error**: `TemporalServiceError` if connection fails.

### `send_approval_signal(workflow_id: str, decision: bool) -> None`
Sends the "yes/no" signal to the specified workflow.
- **Input**: `workflow_id`, `decision` (boolean)
- **Output**: None
- **Error**: `WorkflowNotFoundError` or `SignalDeliveryError`.

### `get_workflow_status(workflow_id: str) -> IncidentWorkflow`
Retrieves the current status and event history for UI rendering.
- **Input**: `workflow_id`
- **Output**: `IncidentWorkflow` object
- **Error**: `WorkflowNotFoundError`.
