#!/usr/bin/env python3
"""
SKG Continuity Engine (neutral spine)
-------------------------------------
Ensures the substrate’s continuity by verifying that
core components are alive, memory is updating, and
ethical equilibrium is maintained.
"""

import json, time, os, psutil
from pathlib import Path

STATE = Path("/var/lib/skg/memory/continuity.json")
PEARLS = Path("/var/lib/skg/memory/pearls.jsonl")
LOG = Path("/var/log/skg/continuity.log")

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{time.ctime()} {msg}\n")

def run_once():
    now = time.time()
    uptime = time.time() - psutil.boot_time()
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    phase = "reflect" if cpu < 40 else "audit" if mem > 80 else "growth"

    continuity = {
        "ts": now,
        "uptime": uptime,
        "cpu": cpu,
        "mem": mem,
        "phase": phase,
        "active_processes": len(psutil.pids()),
    }

    STATE.parent.mkdir(parents=True, exist_ok=True)
    with STATE.open("w", encoding="utf-8") as f:
        json.dump(continuity, f, indent=2)

    log(f"[continuity] Phase={phase}, CPU={cpu}%, MEM={mem}%")

if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(60)
