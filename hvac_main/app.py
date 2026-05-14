import streamlit as st
import json
import uuid
from agent.workflow import app as agent_app

st.set_page_config(page_title="HVAC Co-Pilot Pro", layout="wide")

# 1. Persistent Thread Management
# This ensures LangGraph memory tracks this specific conversation
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

config = {"configurable": {"thread_id": st.session_state.thread_id}}

st.title("🔧 HVAC Master Tech AI (Phase 4)")
st.caption(f"Session ID: {st.session_state.thread_id}")

# 2. Load IoT Data
try:
    with open("mock_iot.json", "r") as f:
        iot = json.load(f)
except FileNotFoundError:
    st.error("Missing mock_iot.json file!")
    st.stop()

with st.sidebar:
    st.header("Live IoT Telemetry")
    st.json(iot)
    if st.button("Reset Session"):
        # Clears history and generates a new memory thread
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# 3. Chat History UI
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Main Interaction Logic
if prompt := st.chat_input("Enter symptom or 'Fixed'"):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare the State for the Agent
    input_state = {
        "model_id": iot["model_id"],
        "brand": iot["brand"],
        "iot_telemetry": iot,
        "user_input": prompt,
        "user_feedback": prompt,
        "is_resolved": False
    }
    
    with st.spinner("Analyzing manual & previous history..."):
        # Invoke the Agent with the config (for memory)
        result = agent_app.invoke(input_state, config=config)
        diag = result.get("diagnostic_json", {})

    # Display the Assistant's Response
    with st.chat_message("assistant"):
        st.markdown("### Diagnostic Report")
        
        # Display recommendation and safety warnings if any
        recommendation = diag.get('probable_causes', ['N/A'])[0]
        st.info(f"**Top Recommendation:** {recommendation}")
        
        if "safety_warning" in diag:
            st.warning(diag["safety_warning"])
        
        # Display the Checklist
        st.markdown("#### Steps to perform:")
        current_tid = st.session_state.thread_id
        
        for step in diag.get("checklist", []):
            # Unique key prevents Streamlit from getting confused by multiple checkboxes
            st.checkbox(
                f"{step['action']} (Expected: {step['expected']})", 
                key=f"s_{current_tid}_{step['step']}"
            )

    # Save to session history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"**Recommendation:** {recommendation}"
    })