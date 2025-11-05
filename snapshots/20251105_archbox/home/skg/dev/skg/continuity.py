#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
import json, time
from pathlib import Path
from skg.encoder import encode_text

CONTINUITY_DIR = Path("/opt/skg/skg_docs")
PEARLS_PATH = Path("/var/lib/skg/memory/pearls.jsonl")

def parse_lines(path: Path):
    txt = path.read_text(encoding="utf-8", errors="ignore")
    for line in txt.splitlines():
        s = line.strip()
        if s:
            yield s

def ingest_new_exports():
    if not CONTINUITY_DIR.exists():
        return []
    imported = []
    for p in sorted(CONTINUITY_DIR.glob("chat_full_restore_*.txt")):
        mark = p.with_suffix(".imported")
        if mark.exists():
            continue
        with PEARLS_PATH.open("a", encoding="utf-8") as out:
            for s in parse_lines(p):
                vec = encode_text(s)
                pearl = {
                    "timestamp": time.time(),
                    "kind": "continuity",
                    "source": str(p),
                    "text": s,
                    "vec": vec
                }
                out.write(json.dumps(pearl, ensure_ascii=False) + "\n")
        mark.write_text(time.strftime("%Y-%m-%d %H:%M:%S"))
        imported.append(p.name)
    return imported

if __name__ == "__main__":
    print("Imported:", ingest_new_exports())
