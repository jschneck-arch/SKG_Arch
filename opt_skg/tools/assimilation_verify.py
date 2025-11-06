#!/usr/bin/env python3
"""
SKG Assimilation Verifier — confirms all skills are alive and auditable.
"""
import json, os, time, hashlib, importlib.util
from pathlib import Path

SKILLS_DIR = Path("/home/skg/dev/skills")
STATE_FILE = Path("/var/lib/skg/state/assimilation_state.json")
AUDIT_LOG = Path("/var/lib/skg/memory/governance.audit.jsonl")

def hash_file(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        return ""

def entropy(lines):
    """basic Shannon-style entropy estimate"""
    chars = "".join(lines)
    unique = set(chars)
    if not unique:
        return 0
    import math
    probs = [chars.count(c)/len(chars) for c in unique]
    return -sum(p*math.log(p, 2) for p in probs)

def verify_skill(p: Path):
    try:
        spec = importlib.util.spec_from_file_location(p.stem, str(p))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        ok = hasattr(m, "run")
        return {"ok": ok, "entropy": entropy(p.read_text().splitlines())}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def audit(event, skill, details):
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": time.time(),
        "actor": "assimilation_verify",
        "event": event,
        "skill": skill,
        "details": details,
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

def main():
    results = {}
    for p in sorted(SKILLS_DIR.glob("*.py")):
        r = verify_skill(p)
        results[p.name] = r
        if not r["ok"]:
            audit("verification_failed", str(p), r)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({
        "ts": time.time(),
        "skills_checked": len(results),
        "results": results
    }, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
