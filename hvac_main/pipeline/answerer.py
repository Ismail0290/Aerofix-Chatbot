import json
import logging
import urllib.request
import urllib.error
from typing import Any, Iterator

logger = logging.getLogger(__name__)

OLLAMA_URL  = "http://localhost:11434/api/chat"
MODEL_NAME  = "qwen2.5:3b"

def get_structured_answer(messages: list[dict[str, str]]) -> dict:
    """NEW: Forces Ollama to return a JSON object for Agentic nodes."""
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "format": "json", # Critical for structured logic
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw_data = resp.read().decode("utf-8")
            response_json = json.loads(raw_data)
            content = response_json.get("message", {}).get("content", "{}")
            return json.loads(content)
    except Exception as exc:
        logger.error(f"Failed to get structured response: {exc}")
        return {"error": "Failed to parse diagnostic JSON", "raw": str(exc)}

# Keep your existing stream_answer and get_answer below...