#!/usr/bin/env python3
import time, json, os
from pathlib import Path

AUDIT = Path("/var/log/skg/governance.audit.jsonl")
POL = {
  "max_restart_rate_per_min": 6,     # anti-loop
  "require_annotation": True,        # caller must include 'why'
}

def audit(entry):
    entry["ts"] = time.time()
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as f: f.write(json.dumps(entry)+"\n")

def ethics_check(action: str, unit: str, why: str|None):
    if POL["require_annotation"] and not why:
        return False, "annotation required"
    # future: add reversible-checks, harm-min tests, etc.
    return True, "ok"

def allow(action: str, unit: str, who: str, why: str|None):
    ok, msg = ethics_check(action, unit, why)
    audit({"who": who, "action": action, "unit": unit, "why": why, "decision": "allow" if ok else "deny", "reason": msg})
    return ok, msg
