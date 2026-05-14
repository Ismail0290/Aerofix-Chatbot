import json
import logging
import re
import uuid
from pathlib import Path
from typing import Any
import tiktoken

logger = logging.getLogger(__name__)

CHUNK_SIZE_TOKENS = 800
CHUNK_OVERLAP_TOKENS = 120
TOKENIZER_MODEL = "cl100k_base"

SECTION_HEADING_RE = re.compile(r"^(\d+(\.\d+)*)\s+.{3,}", re.MULTILINE)
TROUBLESHOOTING_HEADING_RE = re.compile(r"troubleshoot|fault|alarm|error code|symptom|remedy", re.IGNORECASE)

def build_chunks(
    elements: list[dict[str, Any]],
    image_meta: list[dict[str, Any]],
    output_dir: Path,
    model_metadata: dict[str, str] = None  # NEW: Model context
) -> list[dict[str, Any]]:
    enc = tiktoken.get_encoding(TOKENIZER_MODEL)
    page_to_images = _build_page_to_images(image_meta)
    
    # Ensure model_metadata is a dict
    model_meta = model_metadata or {"brand": "Generic", "model_id": "Unknown"}

    table_elements = [e for e in elements if e["type"] == "Table"]
    text_elements  = [e for e in elements if e["type"] not in ("Table", "Image", "PageBreak")]

    chunks: list[dict[str, Any]] = []

    # Inject model info into text chunks
    text_chunks = _build_text_chunks(text_elements, page_to_images, enc)
    for c in text_chunks:
        c.update(model_meta)
    chunks.extend(text_chunks)

    # Inject model info into table chunks
    table_chunks = _build_table_chunks(table_elements, page_to_images)
    for c in table_chunks:
        c.update(model_meta)
    chunks.extend(table_chunks)

    type_order = {"section": 0, "table": 1, "troubleshooting": 2}
    chunks.sort(key=lambda c: (c.get("page") or 0, type_order.get(c["chunk_type"], 9)))

    for i, chunk in enumerate(chunks):
        chunk["chunk_id"] = f"chunk_{i + 1:04d}"

    out_file = output_dir / "chunks.json"
    out_file.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    return chunks

# ... (Include your existing helper functions: _build_page_to_images, _detect_heading_info, etc. from original file)
# ──────────────────────────────────────────────
# Internal helpers (Add these to the bottom of pipeline/chunker.py)
# ──────────────────────────────────────────────

def _build_page_to_images(image_meta: list[dict[str, Any]]) -> dict[int, list[str]]:
    """Map page numbers → list of image_ids on that page."""
    mapping: dict[int, list[str]] = {}
    for im in image_meta:
        page = im.get("page")
        if page is not None:
            mapping.setdefault(page, []).append(im["image_id"])
    return mapping


def _detect_heading_info(text: str) -> tuple[str | None, str | None]:
    """Extract (section, subsection) from a heading string."""
    m = SECTION_HEADING_RE.match(text.strip())
    if not m:
        return None, None
    num = m.group(1)
    top_level = num.split(".")[0]
    return f"Section {top_level}", text.strip()


def _is_troubleshooting(text: str, section: str | None) -> bool:
    if section and TROUBLESHOOTING_HEADING_RE.search(section):
        return True
    return bool(TROUBLESHOOTING_HEADING_RE.search(text))


def _split_into_token_windows(text: str, enc, chunk_size: int, overlap: int) -> list[str]:
    """Sliding-window split by token count."""
    tokens = enc.encode(text)
    windows: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        window_tokens = tokens[start:end]
        windows.append(enc.decode(window_tokens))
        if end == len(tokens):
            break
        start += chunk_size - overlap
    return windows


def _build_text_chunks(text_elements, page_to_images, enc):
    """Group text elements by heading, then window-chunk each group."""
    groups = []
    current = None

    for el in text_elements:
        el_type = el.get("type", "")
        text = el.get("text", "").strip()
        page = el.get("page")

        if el_type == "Title":
            section, subsection = _detect_heading_info(text)
            is_trouble = _is_troubleshooting(text, section)
            current = {
                "section": section or text[:80],
                "subsection": subsection or text[:80],
                "pages": [page] if page else [],
                "texts": [text],
                "is_trouble": is_trouble,
            }
            groups.append(current)
        else:
            if current is None:
                current = {"section": "Preamble", "subsection": None, "pages": [], "texts": [], "is_trouble": False}
                groups.append(current)
            current["texts"].append(text)
            if page and page not in current["pages"]:
                current["pages"].append(page)

    chunks = []
    for group in groups:
        combined_text = "\n\n".join(group["texts"])
        pages = group["pages"]
        first_page = pages[0] if pages else None
        linked_images = []
        for pg in pages:
            linked_images.extend(page_to_images.get(pg, []))

        base_meta = {
            "section": group["section"],
            "subsection": group["subsection"],
            "page": first_page,
            "linked_images": linked_images,
        }

        if group["is_trouble"]:
            chunks.append({**base_meta, "chunk_id": str(uuid.uuid4()), "chunk_type": "troubleshooting", "text": combined_text})
        else:
            windows = _split_into_token_windows(combined_text, enc, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)
            for window in windows:
                chunks.append({**base_meta, "chunk_id": str(uuid.uuid4()), "chunk_type": "section", "text": window})
    return chunks


def _build_table_chunks(table_elements, page_to_images):
    chunks = []
    for el in table_elements:
        page = el.get("page")
        text = el.get("text", "").strip()
        table_html = el.get("table_html")
        linked_images = page_to_images.get(page, []) if page else []
        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "chunk_type": "table",
            "section": None,
            "subsection": None,
            "page": page,
            "text": text,
            "linked_images": linked_images,
        }
        if table_html:
            chunk["table_html"] = table_html
        chunks.append(chunk)
    return chunks