import json
import logging
import re # NEW: For error code detection
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MODEL_NAME   = "BAAI/bge-small-en-v1.5"
COLLECTION   = "hvac_manual"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

def retrieve(
    query: str,
    db_dir: Path,
    k: int = 5,
    chunk_type: str | None = None,
    model_id: str | None = None  # NEW: Filter by model
) -> list[dict[str, Any]]:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer

    # 1. KEYWORD OVERRIDE: Detect HVAC Error Codes (e.g., E1, L5, P4)
    error_code_match = re.search(r'\b[A-Z][0-9]\b', query.upper())
    search_query = query
    if error_code_match:
        # Boost priority or modify query to focus on the code
        search_query = f"Error Code {error_code_match.group(0)} {query}"

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode(
        QUERY_PREFIX + search_query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).tolist()

    client = chromadb.PersistentClient(path=str(db_dir), settings=Settings(anonymized_telemetry=False))
    collection = client.get_collection(COLLECTION)

    # 2. ADVANCED METADATA FILTERING
    where_clauses = []
    if chunk_type:
        where_clauses.append({"chunk_type": chunk_type})
    if model_id:
        where_clauses.append({"model_id": model_id})
    
    where_filter = None
    if len(where_clauses) > 1:
        where_filter = {"$and": where_clauses}
    elif len(where_clauses) == 1:
        where_filter = where_clauses[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    chunks: list[dict[str, Any]] = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        chunks.append({
            "chunk_id": meta.get("chunk_id", ""),
            "chunk_type": meta.get("chunk_type", ""),
            "section": meta.get("section", ""),
            "subsection": meta.get("subsection", ""),
            "page": meta.get("page", ""),
            "text": doc,
            "distance": round(dist, 4),
            "model_id": meta.get("model_id", "Generic") # Return model context
        })
    return chunks