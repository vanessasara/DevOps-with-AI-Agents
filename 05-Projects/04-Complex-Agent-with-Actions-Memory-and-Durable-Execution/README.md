# AI Logging System for DevOps - Incident Response Agent

This project implements a Streamlit-based chat interface that initiates and manages Temporal workflows for incident diagnosis and remediation.

## Prerequisites

1. **Temporal Server**: Ensure the Temporal dev server is running.
   ```bash
   temporal server start-dev
   ```
2. **Python Environment**: Use `uv` to manage dependencies.
   ```bash
   uv sync
   ```

## Getting Started

### 1. Start the Temporal Worker
The worker listens for workflow tasks and activities.
```bash
uv run worker.py
```

### 2. Start the Streamlit UI
Run the chat interface.
```bash
uv run streamlit run app.py
```

## How to Use
1. Open the Streamlit UI at `http://localhost:8501`.
2. Type `start incident` to initiate a new diagnosis workflow.
3. The system will wait for your approval. Type `yes` to proceed with remediation or `no` to reject it.
4. View the final result in the chat window.

## Monitoring
- **Temporal UI**: [http://localhost:8233](http://localhost:8233) - View detailed workflow history and event logs.
- **Streamlit UI**: [http://localhost:8501](http://localhost:8501) - Interaction gateway.

## Project Structure
- `app.py`: Streamlit UI.
- `worker.py`: Temporal worker registration.
- `src/workflows/`: Temporal workflow definitions.
- `src/agents/`: Temporal client proxy and agent logic.
- `src/config.py`: Environment configuration.
