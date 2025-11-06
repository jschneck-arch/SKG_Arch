#!/usr/bin/env python3
"""
SKG Auto-Assimilator
Scans overlay skills, validates and promotes verified ones.
"""

import shutil, time, json
from pathlib import Path

OVERLAY = Path("/home/skg/.skg_overlay/patches")
TARGET  = Path("/home/skg/dev/skills")
STATE   = Path("/var/lib/skg/state")
AUDIT   = Path("/var/lib/skg/memory/governance.audit.jsonl")

def validate_skill(path: Path):
    """Basic static check."""
    text = path.read_text(errors="ignore")
    if "os.system" in text or "__import__" in text:
        return False, "banned_pattern"
    return True, None

def promote_skill(f: Path):
    TARGET.mkdir(parents=True, exist_ok=True)
    dest = TARGET / f.name
    shutil.copy2(f, dest)
    return dest

def record(event, target, ok, detail):
    evt = {
        "ts": time.time(),
        "actor": "auto_assimilator",
        "event": event,
        "target": str(target),
        "ok": ok,
        "detail": detail,
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(evt) + "\n")

def main():
    OVERLAY.mkdir(parents=True, exist_ok=True)
    for f in sorted(OVERLAY.glob("*.py")):
        ok, why = validate_skill(f)
        if ok:
            record("candidate", f, True, {})
            dest = promote_skill(f)
            record("promoted", dest, True, {"from": str(f)})
        else:
            record("rejected", f, False, {"why": why})
    time.sleep(5)

if __name__ == "__main__":
    main()
