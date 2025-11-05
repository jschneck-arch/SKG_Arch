#!/usr/bin/env python3
import json, time, requests
from pathlib import Path

LOG_PATH = Path("/var/lib/skg/memory/conversations.jsonl")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def run(*args, **kwargs):
    params = kwargs.get("params", kwargs)
    prompt = params.get("prompt") or (args[0] if args else None)
    who = params.get("who", "observer")

    if not prompt:
        return {"ok": False, "error": "prompt required"}

    ts = time.time()
    entry = {"ts": ts, "who": who, "prompt": prompt}
    try:
        r = requests.post(
            "http://127.0.0.1:5055/skill/cognition",
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt},
            timeout=60,
        )
        data = r.json()
        entry["response"] = data
    except Exception as e:
        entry["response"] = {"error": str(e)}

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return {"ok": True, "ts": ts, "input": prompt, "response": entry["response"]}
