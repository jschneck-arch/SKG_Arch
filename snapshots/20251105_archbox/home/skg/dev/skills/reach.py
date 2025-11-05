#!/usr/bin/env python3
import json, time, requests
from pathlib import Path

MEM_PATH = Path("/var/lib/skg/memory/reach.jsonl"); MEM_PATH.parent.mkdir(parents=True, exist_ok=True)

def run(prompt: str = "", query: str = "", limit: int = 3, **_):
    q = query or prompt
    if not q:
        return {"ok": False, "error": "No query/prompt provided"}
    try:
        r = requests.get("https://api.duckduckgo.com/", params={"q": q, "format":"json", "no_redirect":"1"}, timeout=10)
        data = r.json()
        results = []
        for t in data.get("RelatedTopics", [])[:limit]:
            if isinstance(t, dict) and "Text" in t:
                results.append(t["Text"])
        MEM_PATH.open("a", encoding="utf-8").write(json.dumps({"ts": time.time(), "kind":"reach", "q": q, "results": results}) + "\n")
        return {"ok": True, "query": q, "results": results}
    except Exception as e:
        return {"ok": False, "error": str(e)}
