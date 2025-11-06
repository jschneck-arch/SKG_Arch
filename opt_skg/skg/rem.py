#!/usr/bin/env python3
"""
Reflexive Equilibrium Mechanism
Balances entropy, ethics, and load to regulate SKG activity cadence.
"""
import json, time, os, psutil
from pathlib import Path

TEL = Path("/var/lib/skg/state/telemetry.json")
LIFE = Path("/var/lib/skg/state/lifecycle.json")
REM = Path("/var/lib/skg/state/rem.json")

TARGET = {"entropy":0.25,"ethics":0.8}
INTERVAL = 30  # base seconds

def read(path):
    try:
        with open(path) as f: return json.load(f)
    except: return {}

def regulate():
    tel = read(TEL)
    life = read(LIFE)
    phase = life.get("phase","reflection")
    ent = tel.get("entropy_avg_5m") or tel.get("entropy") or 0
    eth = tel.get("ethics_coherence") or 0
    load = psutil.cpu_percent()
    delta = (ent - TARGET["entropy"]) - (eth - TARGET["ethics"])
    # adjust frequency: higher entropy or low ethics => slower cycle
    adj = max(5, INTERVAL + delta*60)
    state = {
        "ts": time.time(),
        "phase": phase,
        "entropy": round(ent,3),
        "ethics": round(eth,3),
        "cpu": load,
        "sleep_interval": round(adj,1),
        "recommendation": "cool-down" if adj>INTERVAL else "accelerate"
    }
    with open(REM,"w") as f: json.dump(state,f,indent=2)
    return state

def loop():
    while True:
        state = regulate()
        time.sleep(state["sleep_interval"])

if __name__=="__main__":
    loop()
