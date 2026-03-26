# Tasks: Streamlit-Temporal UI

**Input**: Design documents from `specs/002-streamlit-temporal-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure `src/workflows`, `src/agents`, `src/memory`, `logs`, `data` per plan.md
- [ ] T002 Initialize Python project with `uv` and install `streamlit`, `temporalio`, `pydantic`, `litellm`
- [ ] T003 [P] Configure `.gitignore` to exclude `__pycache__/`, `.venv/`, `data/*.db`, and `logs/*.log`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T004 Implement environment configuration in `src/config.py` (Temporal address, K8S_ENABLED, credentials detection)
- [ ] T005 [P] Create Temporal worker boilerplate in `worker.py` to register workflows and activities
- [ ] T006 Implement `TemporalClientProxy` in `src/agents/temporal_proxy.py` per contracts/workflow_client.md

**Checkpoint**: Foundation ready - Streamlit app can now be built on top of the Temporal proxy

---

## Phase 3: User Story 1 - Start Incident Workflow (Priority: P1) 🎯 MVP

**Goal**: Initiate an incident response workflow via a chat interface.

**Independent Test**: Type "start incident" in the Streamlit UI and verify a new workflow appears in the Temporal UI at `localhost:8233`.

### Tests for User Story 1

- [ ] T007 [P] [US1] Create unit test for `start_incident_workflow` in `tests/test_temporal_proxy.py`

### Implementation for User Story 1

- [ ] T008 [US1] Define initial `IncidentWorkflow` in `src/workflows/incident_workflow.py` with a simple log activity
- [ ] T009 [US1] Implement basic Streamlit chat UI in `app.py` with `st.chat_input` and `st.session_state` messages
- [ ] T010 [US1] Connect `app.py` to `TemporalClientProxy.start_incident_workflow` when user types "start incident"
- [ ] T011 [US1] Display acknowledgment message in `app.py` when workflow successfully starts

**Checkpoint**: User Story 1 functional - basic "Trigger" MVP complete.

---

## Phase 4: User Story 2 - Human Approval Gate (Priority: P2)

**Goal**: Approve or reject suggested remediations via the chat interface.

**Independent Test**: Start a workflow that waits for approval, type "yes" in chat, and verify the workflow receives the signal and completes.

### Tests for User Story 2

- [ ] T012 [P] [US2] Create integration test for `send_approval_signal` in `tests/test_temporal_proxy.py`

### Implementation for User Story 2

- [ ] T013 [US2] Update `IncidentWorkflow` in `src/workflows/incident_workflow.py` to include a `wait_for_external_signal` gate
- [ ] T014 [US2] Update `app.py` to detect "yes"/"no" inputs and call `TemporalClientProxy.send_approval_signal`
- [ ] T015 [US2] Add visual indicator in `app.py` when the system is waiting for human approval

**Checkpoint**: User Story 2 functional - Human-in-the-loop safety gate active.

---

## Phase 5: User Story 3 - View Workflow History (Priority: P3)

**Goal**: See the status and history of the incident response in the chat window.

**Independent Test**: Run a full workflow and verify that activities appear in the chat as they complete.

### Implementation for User Story 3

- [ ] T016 [US3] Implement `TemporalClientProxy.get_workflow_status` in `src/agents/temporal_proxy.py` to fetch event history
- [ ] T017 [US3] Implement background polling/refresh logic in `app.py` to update chat with workflow logs
- [ ] T018 [US3] Add error handling in `app.py` to display workflow failures or timeouts

**Checkpoint**: All user stories functional - Full visibility and control loop complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T019 [P] Update `README.md` with setup instructions from `quickstart.md`
- [ ] T020 Run full validation of `quickstart.md` local run instructions
- [ ] T021 Code cleanup and docstring updates in `src/`
- [ ] T022 Ensure `data/` and `logs/` directories are correctly handled in `app.py` and `worker.py`

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)** -> **Foundational (Phase 2)**
2. **Foundational (Phase 2)** -> **User Story 1 (Phase 3)**
3. **User Story 1 (Phase 3)** -> **User Story 2 (Phase 4)** (requires workflow to signal)
4. **User Story 1 (Phase 3)** -> **User Story 3 (Phase 5)** (requires status to fetch)
5. **All Stories** -> **Polish (Phase 6)**

### Parallel Opportunities

- T003 (gitignore) can run with T001/T002.
- T005 (worker boilerplate) and T006 (proxy) can run in parallel.
- Tests (T007, T012) can be written while implementation is in progress.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup structure and dependencies.
2. Build `config.py` and `temporal_proxy.py`.
3. Create a skeletal `IncidentWorkflow`.
4. Build the `app.py` chat shell.
5. **Validate**: Start a workflow from the UI.

### Incremental Delivery

- Add Signal logic (US2) to make it safe.
- Add History polling (US3) to make it observable.
