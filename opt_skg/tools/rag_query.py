#!/usr/bin/env python3
# Simple local search across /opt/skg and /var/lib/skg/memory; returns top-k snippets.
import os, re, json
from pathlib import Path

ROOTS = [Path("/opt/skg"), Path("/var/lib/skg/memory")]
INCLUDE_EXT = {".py",".md",".txt",".json",".jsonl",".yaml",".yml",".service"}

def search(query:str, k:int=6):
    toks = [t.lower() for t in re.findall(r"\w+", query)]
    hits = []
    for root in ROOTS:
        for p in root.rglob("*"):
            if not p.is_file(): continue
            if p.suffix.lower() not in INCLUDE_EXT: continue
            try:
                text = p.read_text(errors="ignore")
            except Exception:
                continue
            score=0
            lower=text.lower()
            for t in toks:
                score += lower.count(t)
            if score>0:
                # Make small snippets around first match
                i = max(0, lower.find(toks[0]) - 120)
                snippet=text[i:i+600].replace("\n"," ")[:600]
                hits.append({"path": str(p), "score": score, "snippet": snippet})
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:k]

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv)>1 else "skg"
    print(json.dumps({"ok":True,"results":search(q)}, indent=2))
