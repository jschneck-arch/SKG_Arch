#!/usr/bin/env python3
import json, time
from pathlib import Path

BASE = Path("/var/lib/skg/memory/chat")
BASE.mkdir(parents=True, exist_ok=True)

def append(session:str, role:str, content):
    p = BASE / f"{session}.jsonl"
    rec = {"ts": time.time(), "role": role, "content": content}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

def load(session:str, limit:int=20):
    p = BASE / f"{session}.jsonl"
    if not p.exists(): return []
    lines = p.read_text().splitlines()[-limit:]
    return [json.loads(x) for x in lines if x.strip()]
