from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import supabase
from hvac_main.pipeline.retriever import retrieve
from hvac_main.pipeline.prompt_builder import build_prompt
from hvac_main.pipeline.answerer import get_structured_answer
from pathlib import Path
import os

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])

class ChatRequest(BaseModel):
    query: str
    device_id: str | None = None

@router.post("")
async def chat_endpoint(req: ChatRequest):
    # 1. Fetch IoT Context if device_id is provided
    iot_context = None
    history_context = None
    if req.device_id:
        try:
            # Device info
            device_resp = supabase.table("devices").select("*").eq("id", req.device_id).single().execute()
            # Latest log
            log_resp = supabase.table("iot_logs").select("*").eq("device_id", req.device_id).order("timestamp", desc=True).limit(1).execute()
            # Maintenance History
            history_resp = supabase.table("maintenance_history").select("*").eq("device_id", req.device_id).execute()
            
            if device_resp.data:
                d = device_resp.data
                log = log_resp.data[0] if log_resp.data else {}
                iot_context = f"""
                Device: {d.get('model_number')} ({d.get('building_type')})
                Current Status: {d.get('current_status')}
                Live Telemetry:
                - Error Code: {log.get('error_code')}
                - Power: {log.get('power_consumption')}W
                - Pressure: {log.get('refrigerant_pressure')} PSI
                - Frequency: {log.get('compressor_frequency')}Hz
                """
                
                history_data = history_resp.data if history_resp.data else []
                history_context = "\n".join([
                    f"- {h.get('date')}: {h.get('issue')} (Fixed by: {h.get('action')})"
                    for h in history_data
                ]) if history_data else "No previous maintenance records."
        except Exception as e:
            print(f"Error fetching device context: {e}")

    # 2. Retrieve Manual Chunks
    try:
        db_path = Path("chroma_db") 
        chunks = retrieve(req.query, db_dir=db_path, k=5)
    except Exception as e:
        print(f"Retrieval error: {e}")
        chunks = []

    # 3. Build Prompt (IoT Context + History + Manual Chunks)
    messages = build_prompt(req.query, chunks, iot_context=iot_context, history_context=history_context)

    # 4. Get LLM Answer (Structured Diagnostic)
    try:
        answer = get_structured_answer(messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation failed: {str(e)}")
    
    return {
        "status": "success",
        "device_id": req.device_id,
        "diagnosis": answer,
        "sources": [
            {
                "chunk_id": c["chunk_id"],
                "section": c["section"],
                "page": c["page"],
                "text": c["text"][:200] + "..."
            } for c in chunks
        ]
    }
