#!/usr/bin/env python3
"""
SKG Telemetry Daemon
Collects runtime vitals: CPU, memory, entropy drift, ethics coherence.
Writes /var/lib/skg/state/telemetry.json for self_state and dashboards.
"""
import json, os, psutil, time
from pathlib import Path
from statistics import fmean

STATE_DIR = Path("/var/lib/skg/state")
TELEMETRY_FILE = STATE_DIR / "telemetry.json"

def read_entropy():
    try:
        with open("/proc/loadavg") as f:
            # lightweight entropy proxy: moving avg of load/CPU ratio
            load1 = float(f.read().split()[0])
        cpu_count = psutil.cpu_count(logical=True)
        return min(1.0, load1 / max(1, cpu_count))
    except Exception:
        return None

def read_ethics():
    try:
        from skg.ethics_reflex import reflect
        data = reflect()
        return data.get("ethics_coherence")
    except Exception:
        return None

def gather():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    entropy = read_entropy()
    ethics = read_ethics()
    data = {
        "ts": time.time(),
        "phase": "Unified",
        "cpu_percent": cpu,
        "mem_percent": mem,
        "entropy": round(entropy, 4) if entropy is not None else None,
        "ethics_coherence": ethics,
        "lfo": {"freq_hz": 0.002},
        "scheduler": {"cpu_weight": 10}
    }
    return data

def loop(interval=30):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    hist = []
    while True:
        d = gather()
        hist.append(d)
        if len(hist) > 10: hist.pop(0)
        d["entropy_avg"] = round(fmean([h["entropy"] for h in hist if h["entropy"]]),4) if any(h["entropy"] for h in hist) else None
        with open(TELEMETRY_FILE, "w") as f: json.dump(d, f, indent=2)
        time.sleep(interval)

if __name__ == "__main__":
    loop()

# --- SKG Phase 10 addition: rolling averages ---
from collections import deque
HIST_1M, HIST_5M, HIST_1H = deque(maxlen=2), deque(maxlen=10), deque(maxlen=120)

def loop(interval=30):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        d = gather()
        for q in (HIST_1M, HIST_5M, HIST_1H):
            q.append(d.get("entropy") or 0)
        d.update({
            "entropy_avg_1m": round(sum(HIST_1M)/len(HIST_1M),4) if HIST_1M else None,
            "entropy_avg_5m": round(sum(HIST_5M)/len(HIST_5M),4) if HIST_5M else None,
            "entropy_avg_1h": round(sum(HIST_1H)/len(HIST_1H),4) if HIST_1H else None,
        })
        with open(TELEMETRY_FILE,"w") as f: json.dump(d,f,indent=2)
        time.sleep(interval)

# --- SKG Phase 10 addition: rolling averages ---
from collections import deque
HIST_1M, HIST_5M, HIST_1H = deque(maxlen=2), deque(maxlen=10), deque(maxlen=120)

def loop(interval=30):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        d = gather()
        for q in (HIST_1M, HIST_5M, HIST_1H):
            q.append(d.get("entropy") or 0)
        d.update({
            "entropy_avg_1m": round(sum(HIST_1M)/len(HIST_1M),4) if HIST_1M else None,
            "entropy_avg_5m": round(sum(HIST_5M)/len(HIST_5M),4) if HIST_5M else None,
            "entropy_avg_1h": round(sum(HIST_1H)/len(HIST_1H),4) if HIST_1H else None,
        })
        with open(TELEMETRY_FILE,"w") as f: json.dump(d,f,indent=2)
        time.sleep(interval)
