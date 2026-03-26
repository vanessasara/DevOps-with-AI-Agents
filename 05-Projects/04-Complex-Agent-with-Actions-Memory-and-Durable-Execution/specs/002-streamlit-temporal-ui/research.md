# Research: Streamlit-Temporal UI

## 1. Streamlit and Temporal Event Loop Integration
**Decision**: Use a global Temporal client managed in Streamlit's `st.session_state`.
**Rationale**: Streamlit reruns the script on every interaction. Maintaining a single Temporal client prevents overhead and connection exhaustion.
**Alternatives considered**: Creating a client per request (too slow, resource intensive).

## 2. Real-time Workflow Status Updates
**Decision**: Implement a background polling mechanism or use Streamlit's `st.empty()` to render the latest workflow history from the Temporal Event History.
**Rationale**: Temporal workflows are long-running and durable. The UI needs to reflect state changes (e.g., when an activity completes or an approval is requested).
**Alternatives considered**: WebSockets (too complex for a local Streamlit app).

## 3. Human Approval Gate Implementation
**Decision**: Capture user input ("yes"/"no") through `st.chat_input` and translate it to a Temporal Signal sent to the specific `WorkflowID`.
**Rationale**: Aligns with the multi-layer gate principle (Temporal Signal is the hard gate).
**Alternatives considered**: UI buttons (Streamlit's `st.button` can be tricky with chat-based history).

## 4. Environment and Secrets
**Decision**: Use `.env` file and `src/config.py` for all environment variables, including `TEMPORAL_ADDRESS` and `K8S_ENABLED`.
**Rationale**: Strictly follows the constitution and ensures portability to placeholder mode.
