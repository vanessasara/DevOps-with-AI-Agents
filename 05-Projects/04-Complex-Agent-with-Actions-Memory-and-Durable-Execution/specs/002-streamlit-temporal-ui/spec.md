# Feature Specification: Streamlit-Temporal UI

**Feature Branch**: `002-streamlit-temporal-ui`  
**Created**: 2026-03-26  
**Status**: Draft  
**Input**: User description: "Streamlit chat interface that starts Temporal workflows and sends approval signals"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start Incident Workflow (Priority: P1)

As an on-call engineer, I want to initiate an incident response workflow via a chat interface so that the AI agent can begin diagnosing the infrastructure failure.

**Why this priority**: Core functionality needed to trigger any automated incident response.

**Independent Test**: Can be tested by typing a command in the chat and verifying that a Temporal workflow is started in the Temporal UI.

**Acceptance Scenarios**:

1. **Given** the Streamlit app is running, **When** I type "start incident diagnosis", **Then** a new Temporal workflow should appear in the Temporal dashboard.
2. **Given** a workflow is started, **When** the workflow begins, **Then** the chat interface should display an acknowledgment message.

---

### User Story 2 - Human Approval Gate (Priority: P2)

As an on-call engineer, I want to approve or reject suggested remediations via the chat interface so that destructive actions are never taken autonomously.

**Why this priority**: Critical for the "Human in the Loop" principle and safety.

**Independent Test**: Can be tested by sending a signal through the Streamlit interface and verifying that the Temporal workflow proceeds to the execution phase or terminates.

**Acceptance Scenarios**:

1. **Given** a workflow is waiting for approval, **When** I type "yes", **Then** the workflow should receive a "yes" signal and proceed.
2. **Given** a workflow is waiting for approval, **When** I type "no", **Then** the workflow should receive a "no" signal and terminate cleanly.

---

### User Story 3 - View Workflow History (Priority: P3)

As an on-call engineer, I want to see the status and history of the incident response in the chat window so that I have full visibility into what the system has done.

**Why this priority**: Essential for auditability and trust.

**Independent Test**: Can be tested by checking that the chat UI updates with real-time status updates from the Temporal workflow.

**Acceptance Scenarios**:

1. **Given** a workflow is running, **When** an activity completes, **Then** a message describing the activity result should appear in the chat.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a Streamlit-based chat interface for user interaction.
- **FR-002**: Users MUST be able to start a Temporal incident response workflow from the chat.
- **FR-003**: System MUST support sending "yes/no" approval signals to a running workflow.
- **FR-004**: System MUST display a clear audit trail of workflow events in the UI.
- **FR-005**: System MUST handle workflow timeouts (30 minutes) gracefully, notifying the user.
- **FR-006**: System MUST persist the chat session history across Streamlit reruns.

### Key Entities *(include if feature involves data)*

- **IncidentWorkflow**: Represents the durable execution of a diagnosis and remediation plan.
- **ApprovalSignal**: Represents the user's decision (True/False) to proceed with an action.
- **AuditTrail**: The collection of activity logs and status updates associated with a workflow.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Workflow starts within 2 seconds of the user command.
- **SC-002**: Signal delivery from UI to Temporal completes in under 1 second.
- **SC-003**: 100% of "yes/no" signals are recorded in the Temporal event history.
- **SC-004**: Users can verify the full audit trail in the Streamlit UI without refreshing.
