#!/usr/bin/env python3
"""
physics_api — consistent physics helpers used by SKG and moons.
Provides: snapshot(), score_delta(before,after), classify(dE,dC), audit(rec)
Moon processes should call record_moon_physics(moon, entropy, coherence).
All records are appended into /var/lib/skg/memory/physics.audit.jsonl
"""
import time, json
from pathlib import Path

TELEMETRY = Path("/var/lib/skg/state/telemetry.json")
AUDIT = Path("/var/lib/skg/memory/physics.audit.jsonl")
MOON_PHYS = Path("/var/lib/skg/memory/moon_physics.jsonl")
AUDIT.parent.mkdir(parents=True, exist_ok=True)
MOON_PHYS.parent.mkdir(parents=True, exist_ok=True)

def snapshot() -> dict:
    try:
        d = json.loads(TELEMETRY.read_text())
    except Exception:
        d = {}
    return {"ts": time.time(), "telemetry": d}

def score_delta(before:dict, after:dict) -> tuple:
    # delta entropy and delta coherence heuristics (fallbacks)
    b = before.get("telemetry", {}) if isinstance(before, dict) else {}
    a = after.get("telemetry", {}) if isinstance(after, dict) else {}
    bE = float(b.get("entropy") or b.get("entropy_avg") or 0.0)
    aE = float(a.get("entropy") or a.get("entropy_avg") or 0.0)
    bC = float(b.get("ethics_coherence") or b.get("coherence") or 0.0)
    aC = float(a.get("ethics_coherence") or a.get("coherence") or 0.0)
    dE = aE - bE
    dC = aC - bC
    return (round(dE,6), round(dC,6))

def classify(dE:float, dC:float) -> str:
    # simple thresholds — tweak as needed
    if dE > 0.2 or dC < -0.15:
        return "destabilizing"
    if dE > 0.05 or dC < -0.05:
        return "risky"
    return "stabilizing"

def audit(record:dict) -> dict:
    rec = {"ts": time.time(), **record}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\\n")
    return rec

def record_moon_physics(moon:str, entropy:float, coherence:float, meta:dict=None):
    rec = {"ts": time.time(), "moon": moon, "entropy": float(entropy), "coherence": float(coherence), "meta": meta or {}}
    with MOON_PHYS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\\n")
    return rec

def collect_moon_physics(window_s:int=600):
    now = time.time()
    res = []
    try:
        lines = MOON_PHYS.read_text().splitlines()
    except Exception:
        return res
    for L in lines[-1000:]:
        try:
            j = json.loads(L)
            if now - j.get("ts",0) <= window_s:
                res.append(j)
        except Exception:
            continue
    return res
