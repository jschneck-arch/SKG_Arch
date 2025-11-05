#!/usr/bin/env python3
import json, time
from pathlib import Path

REFLECTIONS = Path("/var/lib/skg/memory/reflections.jsonl")
PRIORITIES = Path("/var/lib/skg/memory/priorities.jsonl")

def run(**_):
    """Assign weights to reflection proposals based on recency/frequency."""
    priorities = {}
    now = time.time()
    if REFLECTIONS.exists():
        for line in REFLECTIONS.open():
            try:
                r = json.loads(line)
                age = now - r["ts"]
                w = max(0, 10000 - age) / 10000
                priorities[r["proposal"]] = priorities.get(r["proposal"], 0) + w
            except Exception:
                continue
    sorted_items = sorted(priorities.items(), key=lambda x: -x[1])
    record = {"ts": now, "priorities": sorted_items}
    with PRIORITIES.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"ok": True, "priorities": sorted_items}
