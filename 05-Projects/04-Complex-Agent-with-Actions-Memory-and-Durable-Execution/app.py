import streamlit as st
import asyncio
import uuid
from src.agents.temporal_proxy import TemporalClientProxy

st.title("Incident Response Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "proxy" not in st.session_state:
    st.session_state.proxy = TemporalClientProxy()

if "active_workflow_id" not in st.session_state:
    st.session_state.active_workflow_id = None

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message the assistant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()

    if "start incident" in prompt_lower:
        workflow_id = f"incident-{uuid.uuid4()}"
        st.session_state.active_workflow_id = workflow_id
        
        async def start_wf():
            await st.session_state.proxy.start_incident_workflow(workflow_id)
            return f"Workflow started: {workflow_id}. Waiting for approval (type 'yes' or 'no')."

        with st.spinner("Starting incident workflow..."):
            response = asyncio.run(start_wf())
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    elif prompt_lower in ["yes", "no"] and st.session_state.active_workflow_id:
        approved = prompt_lower == "yes"
        workflow_id = st.session_state.active_workflow_id
        
        async def send_sig_and_wait():
            await st.session_state.proxy.send_approval_signal(workflow_id, approved)
            result = await st.session_state.proxy.get_workflow_result(workflow_id)
            return f"Signal '{prompt_lower}' sent. Workflow result: {result}"

        with st.spinner(f"Sending {prompt_lower} signal and awaiting completion..."):
            response = asyncio.run(send_sig_and_wait())
        
        # Clear active workflow after signal sent (assuming final decision)
        st.session_state.active_workflow_id = None
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    else:
        response = "I can start incidents ('start incident') and handle approvals ('yes' or 'no')."
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
