#!/usr/bin/env python3
"""
SKG Coder Validator
Promotes seed skills to active skills after syntax validation.
"""

import ast, json, os, time
from pathlib import Path

SKILLS = Path("/opt/skg/skills")
QUEUE = Path("/var/lib/skg/memory/skill_queue.jsonl")
LOG = Path("/var/log/skg/coder.log")

def log(entry):
    entry["ts"] = time.time()
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def validate_code(code):
    try:
        ast.parse(code)
        return True, "syntax ok"
    except Exception as e:
        return False, str(e)

def process_queue():
    if not QUEUE.exists():
        log({"event": "no_queue"})
        return
    lines = QUEUE.read_text().strip().splitlines()
    QUEUE.write_text("")  # clear after reading
    for line in lines:
        try:
            item = json.loads(line)
            name = item.get("skill")
            seed = SKILLS / f"seed_{name}.py"
            target = SKILLS / f"{name}.py"
            if not seed.exists():
                log({"event": "missing_seed", "skill": name})
                continue
            code = seed.read_text()
            ok, msg = validate_code(code)
            if not ok:
                log({"event": "invalid_seed", "skill": name, "error": msg})
                continue
            if target.exists():
                log({"event": "already_exists", "skill": name})
                continue
            target.write_text(code)
            os.chown(target, os.getuid(), os.getgid())
            log({"event": "promoted", "skill": name})
        except Exception as e:
            log({"event": "exception", "error": str(e)})

if __name__ == "__main__":
    process_queue()
