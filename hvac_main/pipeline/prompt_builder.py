"""
Prompt Builder — assembles the system + user prompt from retrieved chunks.
"""

from typing import Any

SYSTEM_PROMPT = """You are an expert HVAC technician assistant. 
You will be provided with three types of context:
1. LIVE DEVICE DATA: Real-time telemetry from the unit.
2. MAINTENANCE HISTORY: Previous repairs and issues for this specific device.
3. MANUAL EXCERPTS: Technical documentation from the manufacturer.

Your goal is to provide a precise diagnostic JSON object.
The JSON must follow this exact structure:
{
  "analysis": "A brief explanation of what is wrong, correlating logs with manual and history.",
  "root_cause": "The most likely single cause of the problem.",
  "severity_score": 1-100 (Where 100 is critical/emergency),
  "prep_list": {
    "tools": ["Tool 1", "Tool 2"],
    "parts": ["Part A", "Part B"]
  },
  "recommended_action": "Immediate next step for the technician."
}

- Use the Maintenance History to check for recurring patterns.
- If the answer is not in the context, say so in the analysis — do not guess."""


def build_prompt(query: str, chunks: list[dict[str, Any]], iot_context: str | None = None, history_context: str | None = None) -> list[dict[str, str]]:
    """
    Returns an OpenAI-style messages list ready for the LLM endpoint.
    """
    context_blocks: list[str] = []

    for i, chunk in enumerate(chunks, start=1):
        header_parts = [f"[{i}]"]
        if chunk.get("subsection"):
            header_parts.append(chunk["subsection"])
        elif chunk.get("section"):
            header_parts.append(chunk["section"])
        if chunk.get("page"):
            header_parts.append(f"p.{chunk['page']}")
        
        header = " | ".join(header_parts)
        context_blocks.append(f"{header}\n{chunk['text'].strip()}")

    manual_context = "\n\n---\n\n".join(context_blocks)

    user_message = "DIAGNOSTIC REQUEST:\n"
    if iot_context:
        user_message += f"--- LIVE DEVICE DATA ---\n{iot_context}\n\n"
    
    if history_context:
        user_message += f"--- MAINTENANCE HISTORY ---\n{history_context}\n\n"
    
    user_message += f"--- TECHNICAL MANUAL EXCERPTS ---\n{manual_context}\n\n"
    user_message += f"QUESTION/ISSUE: {query}"

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_message},
    ]
