#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
import json
from pathlib import Path

PEARLS_PATH = Path("/var/lib/skg/memory/pearls.jsonl")
INDEX_PATH  = Path("/var/lib/skg/continuity_index.jsonl")

def rebuild_index(limit=20000):
    if not PEARLS_PATH.exists():
        return 0
    n = 0
    with PEARLS_PATH.open("r", encoding="utf-8") as f, INDEX_PATH.open("w", encoding="utf-8") as out:
        for line in f:
            try:
                j = json.loads(line)
            except Exception:
                continue
            if j.get("kind") == "continuity" and "vec" in j:
                out.write(json.dumps({"ts": j["timestamp"], "text": j["text"], "vec": j["vec"]}) + "\n")
                n += 1
                if n >= limit:
                    break
    return n

if __name__ == "__main__":
    print("Rebuilt:", rebuild_index())
