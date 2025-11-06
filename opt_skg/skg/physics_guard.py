#!/usr/bin/env python3
import json, time
from pathlib import Path

TEL = Path("/var/lib/skg/state/telemetry.json")
AUD = Path("/var/lib/skg/memory/agent.audit.jsonl")

def _read_json(p: Path, default=None):
    try: return json.loads(p.read_text())
    except: return default

def telemetry():
    return _read_json(TEL, {}) or {}

def audit(entry: dict):
    AUD.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": time.time(), **entry}
    with AUD.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def snapshot():
    t = telemetry()
    return {
        "entropy": t.get("entropy", t.get("entropy_avg")),
        "ethics_coherence": t.get("ethics_coherence"),
    }

def score_delta(before: dict, after: dict):
    bE = before.get("entropy"); aE = after.get("entropy")
    bC = before.get("ethics_coherence"); aC = after.get("ethics_coherence")
    dE = (aE - bE) if (aE is not None and bE is not None) else None
    dC = (aC - bC) if (aC is not None and bC is not None) else None
    return dE, dC

def classify(dE, dC, entropy_tolerance=0.06):
    """
    Stabilizing if coherence increases or entropy rise is small.
    Destabilizing if coherence drops and entropy jump is large.
    Neutral otherwise.
    """
    if dC is not None and dC >= 0:
        return "stabilizing"
    if dE is not None and dE <= entropy_tolerance and (dC is None or dC > -0.01):
        return "stabilizing"
    if (dC is not None and dC < 0) and (dE is not None and dE > entropy_tolerance):
        return "destabilizing"
    return "neutral"

def should_delay(intent:str, now:dict, low_coherence=0.55):
    """
    No allowlists. Only physics:
    If coherence is already low, heavy/irreversible intents may be delayed.
    You can set low_coherence=None to disable.
    """
    if low_coherence is None: return False
    c = now.get("ethics_coherence")
    if c is None: return False
    heavy = intent in ("run_python", "run_bash")
    return heavy and c < low_coherence
