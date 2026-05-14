from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver  # NEW: For persistence
from agent.graph_state import AgentState
from pipeline.retriever import retrieve
from pipeline.answerer import get_structured_answer
from pipeline.agent_prompts import DIAGNOSTIC_PROMPT

# --- Nodes ---

def analyzer_node(state: AgentState):
    """Entry point: Extracts the core technical error code."""
    print("--- [Node: Analyzer] ---")
    iot = state.get("iot_telemetry", {})
    # Prioritize IoT error codes over chat text
    query = iot.get("sensors", {}).get("error_code_raw") or state["user_input"]
    
    return {
        "anomalies": [f"Fault Code Detected: {query}"],
        "user_input": query
    }

def predictor_node(state: AgentState):
    """RAG Node: Pulls manual data and injects page citations."""
    print("--- [Node: Predictor] ---")
    query = state["user_input"]
    
    # 1. Retrieve specific manual chunks
    chunks = retrieve(query, db_dir="vector_db", model_id=state["model_id"])
    
    # 2. Extract unique page numbers for citations (Phase 4)
    pages = sorted(list(set([str(c.get('page', '?')) for c in chunks])))
    citation = f" [Source: Manual Page {', '.join(pages)}]"
    
    context = "\n\n".join([c['text'] for c in chunks])
    messages = [{"role": "system", "content": DIAGNOSTIC_PROMPT.format(context_text=context, query=query)}]
    
    # 3. Generate JSON
    prediction = get_structured_answer(messages)
    
    # Append citation to the primary cause
    if prediction.get("probable_causes"):
        prediction["probable_causes"][0] += citation

    return {
        "diagnostic_json": prediction,
        "retrieved_chunks": chunks
    }

def interviewer_node(state: AgentState):
    """The 'Human-in-the-loop' gatekeeper."""
    print("--- [Node: Interviewer] ---")
    
    user_feedback = state.get("user_feedback", "").lower()
    last_diag = state.get("diagnostic_json", {})
    current_cause = last_diag.get("probable_causes", ["Unknown"])[0]

    # Success Case
    if any(word in user_feedback for word in ["fixed", "resolved", "yes", "worked"]):
        return {
            "is_resolved": True,
            "chat_history": [{"role": "assistant", "content": "✅ Issue marked as resolved."}]
        }

    # Failure/Loop Case: Feedback provided but issue persists
    if user_feedback:
        print(f"❌ Feedback received: {user_feedback}. Re-calculating...")
        return {
            "is_resolved": False,
            "chat_history": [{"role": "user", "content": user_feedback}],
            # We update the query to tell the Predictor to find something NEW
            "user_input": f"{state['user_input']} - Not caused by {current_cause}"
        }

    return {"is_resolved": False}

# --- Build the Graph ---

workflow = StateGraph(AgentState)

workflow.add_node("analyzer", analyzer_node)
workflow.add_node("predictor", predictor_node)
workflow.add_node("interviewer", interviewer_node)

workflow.set_entry_point("analyzer")
workflow.add_edge("analyzer", "predictor")
workflow.add_edge("predictor", "interviewer")

def should_continue(state: AgentState):
    if state.get("is_resolved"):
        return END
    # Stop execution here to wait for technician's click in UI
    return END

workflow.add_conditional_edges("interviewer", should_continue)

# --- Phase 4: Persistence Layer ---
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)