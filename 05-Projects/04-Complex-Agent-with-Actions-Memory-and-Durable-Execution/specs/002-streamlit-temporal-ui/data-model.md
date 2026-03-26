# Data Model: Streamlit-Temporal UI

## Entities

### IncidentWorkflow
Represents the durable execution of a diagnosis and remediation plan managed by Temporal.

| Field | Type | Description |
|---|---|---|
| workflow_id | string | Unique identifier for the Temporal execution |
| status | enum | [Running, Waiting_For_Approval, Completed, Failed, Timed_Out] |
| start_time | iso8601 | When the workflow was initiated |
| logs | array[string] | Audit trail of activities completed |
| error | string? | Details of any failure |

### ApprovalSignal
Represents the user's decision (True/False) to proceed with a remediation action.

| Field | Type | Description |
|---|---|---|
| decision | boolean | True for 'yes', False for 'no' |
| timestamp | iso8601 | When the signal was sent |
| source | string | Source of the signal (e.g., "Streamlit UI") |

### ChatSession
Represents the user's local interaction history in the Streamlit app.

| Field | Type | Description |
|---|---|---|
| session_id | string | Local session ID |
| messages | array[object] | Collection of {role, content} pairs for rendering |
| active_workflow_id | string? | Reference to the current running workflow |
