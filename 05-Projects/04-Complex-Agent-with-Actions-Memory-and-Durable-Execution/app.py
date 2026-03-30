import streamlit as st
import asyncio
import uuid
import time
from src.agents.temporal_proxy import TemporalClientProxy
from src.memory.pattern_store import PatternStore

st.set_page_config(page_title="AI Incident Response Agent", page_icon="🤖")
st.title("🤖 AI Incident Response Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "proxy" not in st.session_state:
    st.session_state.proxy = TemporalClientProxy()

if "active_workflow_id" not in st.session_state:
    st.session_state.active_workflow_id = None

# Sidebar for Pattern Memory and Settings
with st.sidebar:
    st.header("Settings & Memory")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.active_workflow_id = None
        st.rerun()
    
    st.divider()
    st.subheader("Recent Patterns")
    store = PatternStore()
    with st.expander("View Pattern Store"):
        context = store.get_context_for_agent("connection")
        if context:
            st.text(context)
        else:
            st.info("No patterns stored yet.")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

async def start_and_monitor(workflow_id):
    await st.session_state.proxy.start_incident_workflow(workflow_id)
    return f"Incident workflow **{workflow_id}** started. Reading logs and analyzing..."

async def signal_and_monitor(workflow_id, approved):
    await st.session_state.proxy.send_approval_signal(workflow_id, approved)
    # Wait for the workflow to complete and get the result
    result = await st.session_state.proxy.get_workflow_result(workflow_id)
    return f"Signal sent. **Workflow Result:**\n\n{result}"

if prompt := st.chat_input("Message the assistant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()

    if "start incident" in prompt_lower:
        workflow_id = f"incident-{uuid.uuid4().hex[:8]}"
        st.session_state.active_workflow_id = workflow_id
        
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown("⏳ Starting incident workflow...")
            
            response = asyncio.run(start_and_monitor(workflow_id))
            status_placeholder.markdown(response)
            
            # Add to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Optional: Poll for status until it needs approval or completes
            # For simplicity in this demo, we just inform the user we are analyzing.
            # The next message will likely be from the user (yes/no) after reading Slack or wait.

    elif prompt_lower in ["yes", "no"] and st.session_state.active_workflow_id:
        approved = prompt_lower == "yes"
        workflow_id = st.session_state.active_workflow_id
        
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown(f"⏳ Sending {prompt_lower} signal and awaiting completion...")
            
            response = asyncio.run(signal_and_monitor(workflow_id, approved))
            status_placeholder.markdown(response)
            
            # Add to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        # Clear active workflow after signal sent
        st.session_state.active_workflow_id = None
            
    else:
        response = "I can start incidents ('start incident') and handle approvals ('yes' or 'no')."
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
