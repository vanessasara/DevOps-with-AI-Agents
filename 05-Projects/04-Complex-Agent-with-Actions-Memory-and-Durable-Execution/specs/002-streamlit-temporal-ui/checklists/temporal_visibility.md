# Checklist: Temporal Workflow Visibility

**Feature**: `002-streamlit-temporal-ui`
**Created**: 2026-03-27
**Purpose**: Unit tests for requirements quality concerning mapping Temporal workflows to the Streamlit UI.
**Target Audience**: Reviewer (PR) Carry-over

## Requirement Completeness
- [ ] CHK001 - Are the specific workflow states (Running, Completed, Failed, Timed Out) defined for the UI display? [Gap]
- [ ] CHK002 - Is the mapping between Temporal "Activity Results" and Streamlit "Chat Messages" explicitly specified? [Completeness, Spec §US3]
- [ ] CHK003 - Are loading/waiting states defined for the UI when a workflow is active but no new events are available? [Gap]
- [ ] CHK004 - Does the spec define behavior for concurrent workflows (e.g., if a second incident is started while one is running)? [Gap, Spec §FR-002]

## Requirement Clarity
- [ ] CHK005 - Is the "background polling/refresh logic" quantified with a specific interval (e.g., every 5 seconds)? [Clarity, Spec §SC-004, Plan §T017]
- [ ] CHK006 - Is "gracefully notifying the user" on timeout quantified with specific UI components (e.g., toast, alert, chat message)? [Clarity, Spec §FR-005]
- [ ] CHK007 - Is "clear audit trail" defined with specific fields (e.g., timestamp, activity name, result)? [Clarity, Spec §FR-004]

## Requirement Consistency
- [ ] CHK008 - Do "yes/no" approval requirements align with how the UI displays the current wait state? [Consistency, Spec §US2]
- [ ] CHK009 - Is the chat session history persistence (FR-006) consistent with how Temporal History is retrieved? [Consistency, Spec §FR-006]

## Scenario Coverage
- [ ] CHK010 - Are requirements defined for displaying historical workflows after a session restart? [Coverage, Spec §FR-006]
- [ ] CHK011 - Are requirements specified for when the Temporal service is unreachable or the proxy fails? [Coverage, Exception Flow, Gap]
- [ ] CHK012 - Does the spec define the UI behavior for a "Rejected" remediation (re-entry or termination)? [Coverage, Spec §US2]

## Measurability
- [ ] CHK013 - Can the "2-second workflow start" outcome be objectively measured via the UI? [Measurability, Spec §SC-001]
- [ ] CHK014 - Is there a measurable threshold for "real-time" status updates in the chat? [Measurability, Spec §US3]
