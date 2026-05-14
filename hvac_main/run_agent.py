import json
from agent.workflow import app

# 1. Load the mock IoT data
try:
    with open("mock_iot.json", "r") as f:
        iot_data = json.load(f)
except FileNotFoundError:
    print("Error: mock_iot.json not found! Create it first.")
    exit()

# 2. Initialize the State for the Agent
initial_state = {
    "model_id": iot_data["model_id"],
    "brand": iot_data["brand"],
    "iot_telemetry": iot_data,
    "user_input": "The unit is failing and showing error code E6.",
    "chat_history": [],
    "is_resolved": False,
    "anomalies": [],
    "retrieved_chunks": [],
    "diagnostic_json": {}
}

# 3. Run the Graph
print("\n" + "="*60)
print("  PHASE 2: STARTING AGENTIC DIAGNOSTIC WORKFLOW")
print("="*60 + "\n")

# Using .stream to watch the Agent move through nodes
for output in app.stream(initial_state):
    for node_name, state_update in output.items():
        print(f"\n[NODE COMPLETED]: {node_name.upper()}")
        
        # If we reached the predictor, show what it found
        if node_name == "predictor":
            diag = state_update.get("diagnostic_json", {})
            print(f"IDENTIFIED ERROR: {diag.get('error_code', 'Unknown')}")
            print(f"PROBABLE CAUSE: {', '.join(diag.get('probable_causes', []))}")
            
        # If we reached the interviewer, show the checklist
        if node_name == "interviewer":
            print("\n--- TECHNICIAN CHECKLIST ---")
            # Pull the full state to ensure we have the checklist
            current_state = app.get_state(config).values
            diag = state_update.get("diagnostic_json", current_state.get("diagnostic_json", {}))
            
            for step in diag.get("checklist", []):
                print(f" [ ] Step {step['step']}: {step['action']}")
                print(f"     Expected: {step['expected']}")