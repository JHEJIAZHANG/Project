import os
import re
import json
import requests
import time
from typing import List, Dict


# =====================
# Query 構建
# =====================

STOPWORDS = {"作業", "請", "完成", "報告", "說明"}


def _debug(msg: str) -> None:
    # 無條件列印，方便直接在 terminal 觀察
    print(f"[rec] {msg}")


def build_query(title: str, desc: str) -> str:
    text = f"{title or ''} {desc or ''}"
    tokens = [w for w in text.split() if w and w not in STOPWORDS]
    return (" ".join(tokens[:8]) + " tutorial explain").strip()


# =====================
# 候選搜尋：YouTube（含短期快取） + Perplexity/DDG
# =====================

# 簡易快取（以 query 為 key），避免短時間重複外呼
_CAND_CACHE: Dict[str, tuple[float, List[Dict]]] = {}
_CACHE_TTL_SECONDS = int(os.getenv("REC_CACHE_TTL", "60") or "60")

def _cache_get(query: str) -> List[Dict] | None:
    try:
        ts, items = _CAND_CACHE.get(query, (0.0, []))
        if ts and (time.time() - ts) <= _CACHE_TTL_SECONDS:
            _debug(f"cache hit for query: '{query}' ttl={_CACHE_TTL_SECONDS}s")
            return [dict(it) for it in items]
    except Exception:
        pass
    return None

def _cache_set(query: str, items: List[Dict]) -> None:
    try:
        _CAND_CACHE[query] = (time.time(), [dict(it) for it in items])
    except Exception:
        pass

def _fetch_youtube(query: str) -> List[Dict]:
    api_key = os.getenv("YOUTUBE_API_KEY") or os.getenv("YT_API_KEY")
    if not api_key:
        _debug("YOUTUBE_API_KEY / YT_API_KEY not set, skipping YouTube")
        return []
    url = (
        "https://www.googleapis.com/youtube/v3/search?part=snippet&q="
        + requests.utils.quote(query)
        + f"&key={api_key}&type=video&maxResults=5"
    )
    last_err = None
    for attempt in range(2):
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()
            items = data.get("items", [])
            out = []
            for item in items:
                vid = item.get("id", {}).get("videoId")
                snippet = item.get("snippet", {})
                if not vid:
                    continue
                out.append(
                    {
                        "source": "youtube",
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "title": snippet.get("title", ""),
                        "snippet": snippet.get("description", ""),
                    }
                )
            return out
        except Exception as e:
            last_err = e
            _debug(f"youtube attempt {attempt+1} failed: {e}")
    _debug(f"youtube skipped after retries: {last_err}")
    return []


def fetch_candidates(query: str) -> List[Dict]:
    # 短期快取：避免重複花費與延遲
    cached = _cache_get(query)
    if cached is not None:
        return cached

    out: List[Dict] = []
    # 1) Perplexity（若有金鑰則啟用）
    try:
        if os.getenv("REC_DISABLE_PPLX"):
            _debug("REC_DISABLE_PPLX set, skipping Perplexity")
        else:
            items = _fetch_perplexity(query)
            _debug(f"perplexity/ddg items: {len(items)}")
            out += items
    except Exception:
        pass
    # 2) YouTube
    yt = _fetch_youtube(query)
    _debug(f"youtube items: {len(yt)}")
    out += yt
    _cache_set(query, out)
    return out


# =====================
# DeepSeek Embedding 版本（雲端）
# 若未設定金鑰，會退回本地簡易相似度（關鍵詞重疊）
# =====================

import math


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _deepseek_embed_batch(texts: List[str]) -> List[List[float]]:
    base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    api_key = os.getenv("DEEPSEEK_API_KEY")
    model = os.getenv("DEEPSEEK_EMBED_MODEL", "deepseek-embedding-2")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    url = f"{base_url}/v1/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "input": texts}
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    vectors = [item["embedding"] for item in data.get("data", [])]
    return vectors


def rerank(assignment_text: str, candidates: List[Dict]) -> List[Dict]:
    docs = [f"{c.get('title','')} {c.get('snippet','')}" for c in candidates]
    try:
        vecs = _deepseek_embed_batch([assignment_text] + docs)
        qvec = vecs[0]
        dvecs = vecs[1:]
        scores = [_cosine(qvec, dv) for dv in dvecs]
    except Exception:
        # 後備：以詞重疊比率估分
        q_tokens = set((assignment_text or "").lower().split())
        scores = []
        for d in docs:
            d_tokens = set((d or "").lower().split())
            inter = len(q_tokens & d_tokens)
            denom = (len(q_tokens) + len(d_tokens)) or 1
            scores.append(inter / denom)

    for c, s in zip(candidates, scores):
        c["score"] = float(s)
    return sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)


# =====================
# 多樣性過濾（來源均衡）
# =====================

def diversify_by_source(items: List[Dict], max_total: int, per_source_limit: int = 3) -> List[Dict]:
    if max_total <= 0:
        return []
    counts = {}
    out: List[Dict] = []
    for it in items:
        if len(out) >= max_total:
            break
        src = (it.get("source") or "").lower()
        used = counts.get(src, 0)
        if used >= per_source_limit:
            continue
        out.append(it)
        counts[src] = used + 1
    return out


# =====================
# Perplexity 線上搜尋整合（可選）
# =====================

def _extract_urls(text: str) -> List[str]:
    if not text:
        return []
    # 簡單 URL 抽取
    pattern = r"https?://[\w\-\.\?\,\'/\\\+&%\$#_=:@]+"
    return re.findall(pattern, text)


def _fetch_ddg(query: str) -> List[Dict]:
    """DuckDuckGo Instant Answer API 作為無金鑰後備。"""
    url = (
        "https://api.duckduckgo.com/?q="
        + requests.utils.quote(query)
        + "&format=json&no_redirect=1&no_html=1&skip_disambig=1"
    )
    headers = {
        "User-Agent": os.getenv("WIKI_USER_AGENT", "NTUB-Assistant/1.0 (+contact: admin@localhost)")
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items: List[Dict] = []
        # 優先使用 RelatedTopics 的 FirstURL / Text
        for rt in data.get("RelatedTopics", [])[:10]:
            if isinstance(rt, dict):
                u = rt.get("FirstURL")
                t = rt.get("Text") or ""
                if u:
                    items.append({
                        "source": "duckduckgo",
                        "url": u,
                        "title": t[:120],
                        "snippet": t,
                    })
                    if len(items) >= 5:
                        break
        # 若沒有 RelatedTopics，回退使用 AbstractURL
        if not items:
            abs_url = data.get("AbstractURL")
            abs_text = data.get("AbstractText") or data.get("Heading") or ""
            if abs_url:
                items.append({
                    "source": "duckduckgo",
                    "url": abs_url,
                    "title": abs_text[:120] or abs_url,
                    "snippet": abs_text,
                })
        _debug(f"duckduckgo items: {len(items)}")
        return items
    except Exception as e:
        _debug(f"duckduckgo error: {e}")
        return []


def _fetch_perplexity(query: str) -> List[Dict]:
    # 支援多種常見環境變數名稱
    api_key = (
        os.getenv("PERPLEXITY_API_KEY")
        or os.getenv("PPLX_API_KEY")
        or os.getenv("PERPLEXITYAI_API_KEY")
    )
    if not api_key:
        _debug("Perplexity API key not found (PERPLEXITY_API_KEY / PPLX_API_KEY / PERPLEXITYAI_API_KEY). Using DuckDuckGo fallback")
        return _fetch_ddg(query)

    # 強制使用成本友善的 sonar 模型（忽略環境變數）
    model = "sonar"
    base = os.getenv("PERPLEXITY_API_BASE") or os.getenv("PPLX_API_BASE") or "https://api.perplexity.ai"
    url = base + "/chat/completions"

    _debug(f"using Perplexity model={model} base={base}")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    system_prompt = (
        "You are a search assistant. Return 5 high-quality learning resources for the given topic. "
        "Output STRICT JSON only, no extra text: {\"items\":[{\"title\":string,\"url\":string,\"snippet\":string}]}"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Topic: {query}"},
        ],
        # 省錢參數
        "max_tokens": 256,
        "enable_search_classifier": True,
        "web_search_options": {"search_context_size": "low"},
        "return_related_questions": False,
        # 適度保留溫度為低，以增強結構化輸出穩定性
        "temperature": 0.2,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        try:
            resp.raise_for_status()
        except Exception:
            # 若是 model 無效，原則上不應發生（已固定 sonar）。保留結構但不更換模型。
            try:
                body = resp.json() if hasattr(resp, 'json') else {}
            except Exception:
                body = {}
            err_type = (body.get("error", {}) or {}).get("type")
            if err_type == "invalid_model":
                _debug("perplexity invalid model for 'sonar' (unexpected). aborting this call.")
                resp.raise_for_status()
            resp.raise_for_status()
        data = resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        items: List[Dict] = []
        # 優先嘗試解析嚴格 JSON
        try:
            parsed = json.loads(content)
            for it in parsed.get("items", [])[:5]:
                url = it.get("url")
                title = it.get("title") or ""
                snippet = it.get("snippet") or ""
                if url:
                    items.append({
                        "source": "perplexity",
                        "url": url,
                        "title": title,
                        "snippet": snippet,
                    })
        except Exception:
            # 後備：從文字中抽取 URL
            urls = _extract_urls(content)[:5]
            for u in urls:
                items.append({
                    "source": "perplexity",
                    "url": u,
                    "title": u,
                    "snippet": "",
                })
        _debug(f"perplexity parsed items: {len(items)}")
        return items
    except Exception as e:
        try:
            if 'resp' in locals() and hasattr(resp, 'text'):
                _debug(f"perplexity error: {e} | body: {resp.text[:400]}")
            else:
                _debug(f"perplexity error: {e}")
        except Exception:
            _debug(f"perplexity error: {e}")
        return []



