from typing import Annotated, TypedDict, List, Union
import operator

class AgentState(TypedDict):
    # Metadata for filtering
    model_id: str
    brand: str
    
    # Data inputs
    iot_telemetry: dict
    user_input: str
    
    # Brain state
    anomalies: List[str]
    retrieved_chunks: List[dict]
    diagnostic_json: dict  # The structured checklist from our new prompt
    
    # Conversation management
    chat_history: Annotated[list, operator.add]
    next_node: str
    is_resolved: bool