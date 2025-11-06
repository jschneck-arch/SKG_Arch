#!/usr/bin/env python3
"""
XRP — Cross Resonance Protocol
Quantifies harmonic alignment between SKG nodes (based on RNT + MEP data).
"""

import json, math, time
from pathlib import Path
from skg.utils import safe_read_json, safe_write_json

STATE = Path("/var/lib/skg/state/xrp_state.json")
AUDIT = Path("/var/lib/skg/memory/xrp.audit.jsonl")

def resonance_score(local_freq: float, peers: list[dict]) -> dict:
    """Compute harmonic resonance coherence among peers."""
    ts = time.time()
    peer_freqs = [p.get("freq_hz", 0.0) for p in peers]
    if not peer_freqs:
        return {"ts": ts, "coherence": 1.0, "phase_error": 0.0}

    diffs = [abs(local_freq - f) for f in peer_freqs]
    phase_error = sum(diffs) / max(1, len(diffs))
    coherence = max(0.0, 1.0 - phase_error * 10)  # arbitrary scaling factor

    state = {"ts": ts, "coherence": coherence, "phase_error": phase_error}
    safe_write_json(STATE, state)
    with AUDIT.open("a") as f:
        f.write(json.dumps(state) + "\n")

    return state


def integrate_with_mep(mep_state: dict, rnt_snapshot: dict) -> dict:
    """Combine MEP coupling with RNT frequency data for overall resonance."""
    lfo = rnt_snapshot.get("lfo", {"freq_hz": 0.002})
    peers = rnt_snapshot.get("peers", [])
    base = resonance_score(lfo.get("freq_hz", 0.002), peers)
    base["coupling"] = mep_state.get("coupling", 1.0)
    base["field_strength"] = (base["coherence"] * base["coupling"])
    return base


if __name__ == "__main__":
    demo_mep = {"coupling": 0.91}
    demo_rnt = {"lfo": {"freq_hz": 0.0021}, "peers": [{"freq_hz": 0.0022}, {"freq_hz": 0.0019}]}
    print(json.dumps(integrate_with_mep(demo_mep, demo_rnt), indent=2))
