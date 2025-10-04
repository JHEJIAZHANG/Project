import os
import re
import json
import requests
import time
from typing import List, Dict, Optional


# =====================
# Query 構建
# =====================

STOPWORDS = {"作業", "請", "完成", "報告", "說明"}


def _debug(msg: str) -> None:
    # 無條件列印，方便直接在 terminal 觀察
    print(f"[rec] {msg}")


def build_query(title: str, desc: str) -> str:
    text = f"{title or ''} {desc or ''}".strip()
    tokens = [w for w in text.split() if w and w not in STOPWORDS]
    return (" ".join(tokens[:8]) + " tutorial").strip()


# =====================
# 候選搜尋：YouTube（含短期快取） + Perplexity/DDG
# =====================

# 簡易快取（以 query 為 key），避免短時間重複外呼
_CAND_CACHE: Dict[str, tuple[float, List[Dict]]] = {}
_CACHE_TTL_SECONDS = int(os.getenv("REC_CACHE_TTL", "60") or "60")

def _cache_get(query: str) -> Optional[List[Dict]]:
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
    """使用 YouTube Data API v3 獲取準確的影片推薦"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        _debug("YouTube API key not found (YOUTUBE_API_KEY). Using search link fallback")
        # 如果沒有 API key，回退到搜尋連結
        q = requests.utils.quote(query)
        return [{
            "source": "youtube",
            "url": f"https://www.youtube.com/results?search_query={q}",
            "title": f"YouTube: {query}",
            "snippet": "YouTube 搜尋結果",
        }]
    
    try:
        # 使用 YouTube Data API v3 搜尋影片
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query + " tutorial",  # 添加 tutorial 關鍵字提高教學內容相關性
            "type": "video",
            "maxResults": 5,
            "order": "relevance",
            "key": api_key,
            "regionCode": "TW",  # 台灣地區
            "relevanceLanguage": "zh",  # 中文內容優先
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        items = []
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            items.append({
                "source": "youtube",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "title": snippet["title"],
                "snippet": snippet["description"][:200] + "..." if len(snippet["description"]) > 200 else snippet["description"],
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "channel": snippet["channelTitle"],
                "published": snippet["publishedAt"]
            })
        
        _debug(f"YouTube API returned {len(items)} videos")
        return items
        
    except Exception as e:
        _debug(f"YouTube API error: {e}")
        # API 失敗時回退到搜尋連結
        q = requests.utils.quote(query)
        return [{
            "source": "youtube",
            "url": f"https://www.youtube.com/results?search_query={q}",
            "title": f"YouTube: {query}",
            "snippet": "YouTube 搜尋結果",
        }]


def _fetch_youtube_piped(query: str) -> List[Dict]:
    # 已不使用，保留空實作避免引用錯誤
    return _fetch_youtube(query)


def fallback_learning_resources(query: str) -> List[Dict]:
    """Return YouTube videos and other learning resources.
    Always safe (no exceptions) and independent of API keys.
    """
    out: List[Dict] = []
    try:
        yt = _fetch_youtube(query)
        if yt:
            # 如果 YouTube API 返回多個結果，取前幾個
            out.extend(yt[:3])
    except Exception as e:
        _debug(f"fallback youtube error: {e}")
    
    # 確保至少有基本的學習資源
    return _ensure_minimum_items(query, out, min_items=2)


def _ensure_minimum_items(query: str, items: List[Dict], min_items: int = 2) -> List[Dict]:
    """確保至少回傳 min_items 筆結果；若不足，補上通用搜尋連結。
    不依賴任何金鑰，避免前後端空白畫面。
    """
    # 去重（以 url 為 key），保留 YouTube 搜尋與 Wikipedia
    seen = set()
    dedup: List[Dict] = []
    for it in items:
        url = (it.get("url") or "").strip()
        if url and url not in seen:
            seen.add(url)
            dedup.append(it)

    if len(dedup) >= min_items:
        return dedup

    # 補：YouTube 搜尋（移除 Wikipedia）
    q = requests.utils.quote(query)
    fallbacks = [
        {
            "source": "youtube",
            "url": f"https://www.youtube.com/results?search_query={q}",
            "title": f"YouTube: {query}",
            "snippet": "YouTube 搜尋結果"
        },
    ]

    for fb in fallbacks:
        if len(dedup) >= min_items:
            break
        if fb["url"] not in seen:
            seen.add(fb["url"])
            dedup.append(fb)

    return dedup


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
            _debug("Attempting to fetch from Perplexity...")
            items = _fetch_perplexity(query)
            _debug(f"perplexity/ddg items: {len(items)}")
            out += items
    except Exception as e:
        _debug(f"Perplexity fetch error: {e}")
    # 2) YouTube（含無金鑰管道）
    yt = _fetch_youtube(query)
    _debug(f"youtube items: {len(yt)}")
    out += yt
    # 最低保證：至少 2 筆
    out = _ensure_minimum_items(query, out, min_items=2)
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
    """使用統一的 DeepSeek 客戶端進行嵌入向量生成"""
    try:
        from services.deepseek_client import is_available
        if not is_available():
            raise RuntimeError("DeepSeek API not available")
        
        # 使用 OpenAI 兼容的嵌入 API
        from services.deepseek_client import _client
        client = _client()
        model = os.getenv("DEEPSEEK_EMBED_MODEL", "deepseek-embedding-2")
        
        response = client.embeddings.create(
            model=model,
            input=texts
        )
        vectors = [item.embedding for item in response.data]
        return vectors
    except Exception as e:
        # 如果 DeepSeek 客戶端不可用，回退到直接 API 調用
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
    _debug(f"_fetch_perplexity called with query: {query}")
    # 支援多種常見環境變數名稱
    api_key = (
        os.getenv("PERPLEXITY_API_KEY")
        or os.getenv("PPLX_API_KEY")
        or os.getenv("PERPLEXITYAI_API_KEY")
    )
    if not api_key:
        _debug("Perplexity API key not found (PERPLEXITY_API_KEY / PPLX_API_KEY / PERPLEXITYAI_API_KEY). Using DuckDuckGo fallback")
        return _fetch_ddg(query)
    
    _debug(f"Perplexity API key found, proceeding with API call")

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



