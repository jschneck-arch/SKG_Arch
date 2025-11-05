#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
SKG Brain — introspective decisions based on continuity themes
"""
from pathlib import Path
import json, random, time
from skg.skills_engine import run_skill
from skg.state import log_journal
from skg.paths import SKG_MEMORY_DIR

INDEX_PATH = Path("/var/lib/skg/continuity_index.jsonl")

THEME_KEYWORDS = ["energy","gravity","phase","sphere","audit","growth","council","reflection","anonym","federat","consensus"]

def self_reflect(limit_lines=800):
    if not INDEX_PATH.exists():
        return {"dominant_theme": None, "keywords": {}}
    counts = {k:0 for k in THEME_KEYWORDS}
    lines = INDEX_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit_lines:]
    for line in lines:
        try:
            j = json.loads(line)
            t = j.get("text","").lower()
        except Exception:
            continue
        for k in THEME_KEYWORDS:
            if k in t:
                counts[k] += 1
    dom = None
    if counts:
        dom = max(counts.items(), key=lambda kv: kv[1])[0]
    return {"dominant_theme": dom, "keywords": counts}

def think_cycle():
    themes = self_reflect()
    dom = themes.get("dominant_theme")
    # Naive mapping: choose a skill based on dominant theme (extend later)
    chosen = "reflect_test"
    result = {}
    try:
        result = run_skill(chosen)
    except Exception as e:
        result = {"error": str(e)}
    log_journal(f"Brain: theme={dom} skill={chosen}")
    return {"chosen": chosen, "theme": dom, "result": result}
