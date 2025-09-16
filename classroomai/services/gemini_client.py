import os
import json
from typing import List, Dict, Optional


def _get_api_key() -> str:
    """Return Gemini API key.
    Prefer 'Gemini_API_KEY' (user-specified),
    fallback to 'GEMINI_API_KEY' if not set.
    """
    key = os.getenv("Gemini_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Gemini API key not found. Set 'Gemini_API_KEY' (preferred) or 'GEMINI_API_KEY'.")
    return key


def _configure() -> None:
    # Lazy import to avoid hard dependency on install-time
    import google.generativeai as genai  # type: ignore
    genai.configure(api_key=_get_api_key())


def get_model(model_name: Optional[str] = None):
    """Get a configured GenerativeModel instance.
    Default model can be overridden by env 'GEMINI_MODEL', else 'gemini-1.5-flash'.
    """
    _configure()
    import google.generativeai as genai  # type: ignore
    name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    return genai.GenerativeModel(name)


def _safe_json(text: str) -> Dict:
    # Remove common Markdown fences if present
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`\n")
        # Possible language prefix like ```json
        first_newline = t.find("\n")
        if first_newline != -1:
            t = t[first_newline + 1 :]
    return json.loads(t)


def generate_learning_resources(topic: str, max_items: int = 5) -> List[Dict]:
    """Ask Gemini to produce strictly-JSON learning resources.

    Returns list of {title, url, snippet}.
    Falls back to empty list on hard failure (caller may add local fallbacks).
    """
    model = get_model()
    system = (
        "你是搜尋助理。請輸出嚴格 JSON（無多餘文字，無 Markdown）："
        '{"items":[{"title":string,"url":string,"snippet":string}]}'
        "。請回傳高品質、可直接學習的資源。"
    )
    resp = model.generate_content([{"role": "user", "parts": [system, f"Topic: {topic}"]}])
    try:
        data = _safe_json(resp.text or "{}")
        items = data.get("items", [])
        # Normalize & trim
        out: List[Dict] = []
        for it in items[: max(1, int(max_items))]:
            url = (it.get("url") or "").strip()
            title = (it.get("title") or "").strip()
            snippet = (it.get("snippet") or "").strip()
            if url and title:
                out.append({"source": "gemini", "url": url, "title": title, "snippet": snippet})
        return out
    except Exception:
        return []


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Create embeddings via Gemini text-embedding-004.
    Caller should handle similarity scoring.
    """
    _configure()
    import google.generativeai as genai  # type: ignore
    model = os.getenv("GEMINI_EMBED_MODEL", "text-embedding-004")
    # The SDK supports single-content embedding; do simple batching
    vectors: List[List[float]] = []
    for content in texts:
        res = genai.embed_content(model=model, content=content, task_type="retrieval_document")
        vectors.append(res["embedding"])  # type: ignore[index]
    return vectors


