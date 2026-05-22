import asyncio
import concurrent.futures
import sys
from pathlib import Path

import streamlit as st
import litellm

litellm.suppress_warnings = True
litellm.set_verbose = False

sys.path.insert(0, str(Path(__file__).parent))

from src.agents.log_analyzer import LogAnalyzerAgent, SummarizerAgent, KubernetesAgent
from src.config import Config

# Safe async runner for Streamlit — avoids event loop conflicts.
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

st.set_page_config(
    page_title="AI Incident Responder",
    page_icon="🚨",
    layout="wide",
)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        try:
            Config.validate()
            st.session_state.agents = {
                "Summarizer Dashboard": SummarizerAgent(),
                "Kubernetes Operations": KubernetesAgent(),
                "Full Analysis": LogAnalyzerAgent(),
            }
        except ValueError as e:
            st.error(f"Configuration error: {e}")
            st.stop()

def render_incident_card(severity: str, system: str, resource: str, cause: str):
    color = {"P1": "🔴", "P2": "🟠", "P3": "🟡", "Info": "🔵"}.get(severity, "⚪")
    st.markdown(f"""
| Field | Value |
|---|---|
| Severity | {color} **{severity}** |
| System | `{system}` |
| Resource | `{resource}` |
| Cause | {cause} |
    """)

def display_sidebar():
    with st.sidebar:
        st.title("🚨 AI Incident Responder")
        st.caption("Agents SDK · LiteLLM · Gemini → Groq fallback")
        st.markdown("---")
        
        mode = st.selectbox(
            "Select Agent Mode",
            ["Summarizer Dashboard", "Kubernetes Operations", "Full Analysis"],
            key="agent_mode",
        )
        
        st.markdown("---")
        st.subheader("Connected Tools")
        st.success("📋 Log Tools ✓")
        st.success("🐳 Docker ✓") if Config.DOCKER_ENABLED else st.warning("🐳 Docker ⚠ simulation")
        st.success("☸️ Kubernetes ✓") if Config.K8S_ENABLED else st.warning("☸️ K8s ⚠ simulation")
        st.success("🐙 GitHub CLI ✓") if Config.GITHUB_TOKEN else st.warning("🐙 GitHub ⚠ no token")
        st.success("🔌 MCP ✓") if Config.MCP_ENABLED else st.warning("🔌 MCP ⚠ disabled")
        
        st.markdown("---")
        st.caption(f"Model: `{Config.GEMINI_MODEL}`")
        if Config.FALLBACK_MODELS:
            st.caption(f"Fallback: `{Config.FALLBACK_MODELS[0]}`")
            
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

async def get_response(user_input: str, mode: str):
    agent = st.session_state.agents[mode]
    return await agent.process_query(user_input)

def handle_input(user_input: str):
    mode = st.session_state.get("agent_mode", "Summarizer Dashboard")
    
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input, "agent": mode})
    with st.chat_message("user"):
        st.markdown(f"**[{mode}]** {user_input}")

    # Show live agent work then render result
    with st.chat_message("assistant"):
        with st.status(f"🔍 {mode} analysing incident...", expanded=True) as status:
            st.write("🤖 Agent started...")
            st.write("🔧 Calling tools...")
            response = run_async(get_response(user_input, mode))
            status.update(label=f"✅ {mode} analysis complete", state="complete", expanded=False)
        st.markdown(response)

    # Append assistant message AFTER render
    st.session_state.messages.append({"role": "assistant", "content": response, "agent": mode})

def main():
    initialize_session_state()
    display_sidebar()

    st.title("🚨 AI DevOps Incident Responder")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "agent" in message:
                st.markdown(f"**[{message['agent']}]** {message['content']}")
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("Describe the issue or ask about cluster/logs/docker/github..."):
        handle_input(prompt)

if __name__ == "__main__":
    main()
