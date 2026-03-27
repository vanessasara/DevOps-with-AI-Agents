# Quickstart: Streamlit-Temporal UI

## Prerequisites
1. Temporal dev server must be running: `temporal server start-dev`
2. All dependencies installed: `uv pip install -r requirements.txt` (including `streamlit`, `temporalio`)

## Local Run Instructions

1. **Start the Temporal Worker**:
   ```bash
   python worker.py
   ```

2. **Start the Streamlit App**:
   ```bash
   streamlit run app.py
   ```

3. **Interact with the Chat**:
   - Type `start incident` to initiate a workflow.
   - When prompted for approval, type `yes` or `no`.
   - Monitor status updates in the chat window.

## Monitoring
- Temporal UI: `http://localhost:8233`
- Streamlit UI: `http://localhost:8501`
