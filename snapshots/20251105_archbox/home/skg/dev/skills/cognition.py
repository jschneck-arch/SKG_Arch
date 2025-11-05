#!/usr/bin/env python3
import json, time, requests
from pathlib import Path

LOG = Path("/var/log/skg/cognition.log")

def log_entry(kind, content):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.time(), "kind": kind, **content}) + "\n")

def run(*args, **kwargs):
    params = kwargs.get("params", kwargs)
    prompt = params.get("prompt") or (args[0] if args else None)
    if not prompt:
        return {"ok": False, "error": "prompt required"}

    try:
        r = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "tinyllama:latest", "prompt": prompt},
            timeout=15
        )
        data = r.json()
        response = data.get("response", data)
        log_entry("chosen_backend", {"backend": "ollama", "model": "tinyllama:latest", "timeout": 15})
        return {"ok": True, "response": response}
    except Exception as e:
        log_entry("ollama_error", {"error": str(e)})
        return {"ok": False, "error": str(e)}
