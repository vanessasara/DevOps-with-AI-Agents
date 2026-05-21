import asyncio
import sys
from pathlib import Path

import streamlit as st
import litellm

litellm.suppress_warnings = True
litellm.set_verbose = False

sys.path.insert(0, str(Path(__file__).parent))

# Import all agents
from src.agents.k8s_agent import KubernetesAgent
from src.agents.log_analyzer import LogAnalyzerAgent
from src.agents.summarizer_agent import SummarizerAgent
from src.config import Config

st.set_page_config(
    page_title="AI DevOps Platform",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0

    if "agents" not in st.session_state:
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


def display_sidebar():
    with st.sidebar:
        st.title("🚨 AI DevOps Platform")
        st.caption("Multi-Agent System")
        
        # Token Tracker Display
        st.metric("Total Tokens Used", st.session_state.total_tokens)

        mode = st.selectbox(
            "Select Agent",
            [
                "Summarizer Dashboard",
                "Kubernetes Operations",
                "Full Analysis",
            ],
            key="agent_mode",
        )

        st.markdown("---")
        st.success("✅ Gemini API Connected")

        if Config.K8S_ENABLED:
            st.success("✅ Kubernetes Live Mode")
        else:
            st.warning("⚠️ Kubernetes Simulation Mode")

        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.total_tokens = 0
            st.rerun()


async def get_response(user_input: str, mode: str):
    agent = st.session_state.agents[mode]
    response = await agent.process_query(user_input)
    
    # Simple token estimation: ~100 tokens per message
    st.session_state.total_tokens += 100 
    return response


def handle_input(user_input: str):
    mode = st.session_state.get("agent_mode", "Summarizer Dashboard")

    # Store message with the agent mode that processed it
    st.session_state.messages.append({"role": "user", "content": user_input, "agent": mode})

    with st.chat_message("user"):
        st.markdown(f"**[{mode}]** {user_input}")

    with st.chat_message("assistant"):
        with st.spinner(f"{mode} is thinking..."):
            response = asyncio.run(get_response(user_input, mode))
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response, "agent": mode})


def main():
    initialize_session_state()
    display_sidebar()

    st.title("🚨 Multi-Agent DevOps Platform")
    st.markdown(f"Currently chatting with: **{st.session_state.get('agent_mode', 'Summarizer Dashboard')}**")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "agent" in message:
                st.markdown(f"**[{message['agent']}]** {message['content']}")
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("Describe the issue or ask about cluster/logs..."):
        handle_input(prompt)


if __name__ == "__main__":
    main()
