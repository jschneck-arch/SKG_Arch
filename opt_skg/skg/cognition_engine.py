#!/usr/bin/env python3
"""
SKG Cognition Engine
Chooses the best available backend: local Ollama -> OpenAI -> internal reflection.
Append-only audit to /var/log/skg/cognition.log
"""

import os, time, json, requests
from pathlib import Path

COG_LOG = Path("/var/log/skg/cognition.log")
COG_LOG.parent.mkdir(parents=True, exist_ok=True)

def _audit(kind, payload):
    try:
        with COG_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "kind": kind, **payload}, ensure_ascii=False) + "\n")
    except Exception:
        pass

def _ollama_models(endpoint:str) -> set:
    try:
        r = requests.get(f"{endpoint.rstrip('/')}/api/tags", timeout=3)
        if r.ok:
            j = r.json()
            return {m.get("name","") for m in j.get("models", []) if isinstance(m, dict)}
    except Exception:
        pass
    return set()

def _ollama_generate(endpoint:str, model:str, prompt:str, timeout:int=30, num_predict:int=128) -> str | None:
    payload = {
        "model": model, "prompt": prompt, "stream": False,
        "options": {"num_predict": num_predict, "temperature": 0.6, "repeat_penalty": 1.1}
    }
    try:
        r = requests.post(f"{endpoint.rstrip('/')}/api/generate", json=payload, timeout=timeout)
        if r.ok:
            j = r.json()
            txt = j.get("response","").strip()
            return txt or None
    except Exception as e:
        _audit("ollama_error", {"error": str(e)})
    return None

def _openai_chat(api_key:str, prompt:str, model:str="gpt-4o-mini", timeout:int=60) -> str | None:
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"},
            json={"model": model, "messages":[{"role":"user","content":prompt}], "temperature":0.7, "max_tokens":256},
            timeout=timeout
        )
        if r.ok:
            j = r.json()
            return (j["choices"][0]["message"]["content"] or "").strip()
    except Exception as e:
        _audit("openai_error", {"error": str(e)})
    return None

def _internal_reflect(prompt:str, pearls_path:str="/var/lib/skg/memory/pearls.jsonl", tail:int=100) -> str:
    # Minimal offline fallback: echo prompt and list recent kinds as a reflective sketch
    kinds = {}
    try:
        p = Path(pearls_path)
        if p.exists():
            lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()[-tail:]
            import json as _j
            for ln in lines:
                try:
                    k = _j.loads(ln).get("kind","_")
                    kinds[k] = kinds.get(k,0)+1
                except Exception:
                    pass
    except Exception:
        pass
    summary = ", ".join(f"{k}:{v}" for k,v in sorted(kinds.items(), key=lambda x:-x[1])[:8]) or "no_recent_events"
    return f"[offline-reflection]\nprompt={prompt}\nrecent={summary}"

def reflect(prompt:str, context:dict|None=None) -> dict:
    context = context or {}
    endpoint = os.getenv("LLM_ENDPOINT","http://127.0.0.1:11434")
    model = os.getenv("LLM_MODEL","phi3")
    openai_key = os.getenv("OPENAI_API_KEY","")

    # 1) try local ollama quickly
    if model in _ollama_models(endpoint):
        for to,np in [(15,96),(30,128),(45,160)]:
            txt = _ollama_generate(endpoint, model, prompt, timeout=to, num_predict=np)
            if txt:
                _audit("chosen_backend", {"backend":"ollama", "model":model, "timeout":to})
                return {"backend":"ollama", "model":model, "text":txt}

    # 2) fallback to openai if key
    if openai_key:
        txt = _openai_chat(openai_key, prompt)
        if txt:
            _audit("chosen_backend", {"backend":"openai", "model":"gpt-4o-mini"})
            return {"backend":"openai", "model":"gpt-4o-mini", "text":txt}

    # 3) offline internal
    txt = _internal_reflect(prompt)
    _audit("chosen_backend", {"backend":"internal"})
    return {"backend":"internal", "model":"", "text":txt}
