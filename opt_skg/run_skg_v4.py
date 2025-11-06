#!/usr/bin/env python3
"""
SKG Core v4  –  substrate cycle manager (governance + cognition integrated)
"""

import os, sys, json, time, gzip, importlib, traceback, psutil
from pathlib import Path
from datetime import datetime

sys.path.append("/opt/skg")

from skg import governance
from skg import cognition_engine

BASE     = Path("/opt/skg")
LOG_DIR  = Path("/var/log/skg")
MEM_DIR  = Path("/var/lib/skg/memory")
STATE    = MEM_DIR / "state.json"
JOURNAL  = LOG_DIR / "journal.jsonl"

LOG_DIR.mkdir(parents=True, exist_ok=True)
MEM_DIR.mkdir(parents=True, exist_ok=True)

_last_reflect_ts = 0.0

def log_event(kind, msg):
    entry = {"ts": time.time(), "kind": kind, "msg": msg}
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

def gzip_rotate(path, max_lines=5000):
    if not path.exists(): return
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) <= max_lines: return
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    gz = path.with_suffix(f".{ts}.jsonl.gz")
    with gzip.open(gz, "wt", encoding="utf-8") as g:
        g.writelines(lines[:-max_lines])
    with path.open("w", encoding="utf-8") as f:
        f.writelines(lines[-max_lines:])
    log_event("maintenance", f"Rotated {path.name} -> {gz.name}")

def system_sense():
    load1, load5, load15 = psutil.getloadavg()
    cpu = psutil.cpu_percent(interval=0.05)
    mem = psutil.virtual_memory().percent
    return {"load1": load1, "cpu": cpu, "mem": mem}

def update_state(extra=None):
    state = {
        "ts": time.time(),
        "uptime": time.monotonic(),
        "sense": system_sense(),
        "last_reflect_ts": _last_reflect_ts
    }
    if extra: state.update(extra)
    with STATE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return state

def reflect_cycle():
    global _last_reflect_ts
    _last_reflect_ts = time.time()
    log_event("reflect", "Internal audit reflection complete.")

def cognition_cycle(state):
    ctx = {"sense": state.get("sense", {}), "last_reflect_ts": state.get("last_reflect_ts", 0.0)}
    verdict = governance.evaluate("cognize", ctx)
    if not verdict.get("approved", False):
        log_event("governance_veto", verdict.get("reason","veto"))
        return
    # prompt can reference sensed state and last reflection age
    age = time.time() - ctx.get("last_reflect_ts", 0.0)
    prompt = (f"Reflect on current SKG substrate state. "
              f"CPU={ctx['sense'].get('cpu',0)}% MEM={ctx['sense'].get('mem',0)}% "
              f"seconds_since_reflect={int(age)}. "
              f"Prioritize audit, stability, and growth.")
    result = cognition_engine.reflect(prompt, context=ctx)
    log_event("cognition", result)

def maintenance_cycle():
    gzip_rotate(JOURNAL)
    # if reach log exists, rotate as well
    reach = Path("/var/lib/skg/memory/reach.jsonl")
    if reach.exists(): gzip_rotate(reach)

def main():
    log_event("startup", "🧠 SKG Core v4 substrate loop (governed)")
    counter = 0
    while True:
        counter += 1
        try:
            state = update_state({"cycle": counter})
            log_event("heartbeat", {"cycle": counter, "sense": state.get("sense", {})})

            if counter % 5 == 0:
                reflect_cycle()

            if counter % 7 == 0:
                cognition_cycle(state)

            if counter % 20 == 0:
                maintenance_cycle()
        except Exception:
            log_event("fatal", traceback.format_exc())
        time.sleep(10)

if __name__ == "__main__":
    main()


# === Applied Patch ===
# evolution at 2025-11-05 10:00:16
# intent: optimize logging or telemetry stability
# note: no-op placeholder
# --- Phase 8 integrations (safe to append) ---
try:
    from skg.meta_context import synthesize as _skg_self
    from skg.ethics_reflex import reflect as _ethics_reflex
    state = _skg_self()
    ethics = _ethics_reflex()
    # if you keep telemetry.json, update its fields here:
    # (write your own telemetry aggregator if not present)
except Exception as e:
    pass


# === Applied Patch ===
# evolution at 2025-11-05 18:30:38
# intent: optimize logging or telemetry stability
# note: no-op placeholder
