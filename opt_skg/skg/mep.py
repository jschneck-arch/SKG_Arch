#!/usr/bin/env python3
"""
MEP — Mutual Entropy Propagation
Bridges node entropy states across RNT peers and computes field convergence.
"""

import json, time, math
from pathlib import Path
from skg.utils import safe_read_json, safe_write_json

STATE = Path("/var/lib/skg/state/mep_state.json")
AUDIT = Path("/var/lib/skg/memory/mep.audit.jsonl")

def propagate(local_entropy: float, peers: list[dict]) -> dict:
    """Compute mutual entropy coupling across peers."""
    ts = time.time()
    peer_entropies = [p.get("entropy", 0.0) for p in peers]
    if not peer_entropies:
        return {"ts": ts, "avg_entropy": local_entropy, "variance": 0.0, "coupling": 1.0}

    avg_entropy = sum(peer_entropies + [local_entropy]) / (len(peer_entropies) + 1)
    variance = sum((e - avg_entropy)**2 for e in peer_entropies) / max(1, len(peer_entropies))
    coupling = 1 / (1 + variance)  # higher variance → weaker coupling
    state = {"ts": ts, "avg_entropy": avg_entropy, "variance": variance, "coupling": coupling}

    safe_write_json(STATE, state)
    with AUDIT.open("a") as f:
        f.write(json.dumps(state) + "\n")

    return state


def integrate_rnt_snapshot(rnt_snapshot: dict) -> dict:
    """Integrate RNT telemetry snapshot into MEP propagation."""
    local_entropy = rnt_snapshot.get("entropy", 0.0)
    peers = rnt_snapshot.get("peers", [])
    return propagate(local_entropy, peers)


if __name__ == "__main__":
    demo = {"entropy": 0.74, "peers": [{"entropy": 0.72}, {"entropy": 0.76}]}
    print(json.dumps(integrate_rnt_snapshot(demo), indent=2))

# --- Field Strength Propagation Patch ---
def _derive_field_strength(coupling, variance):
    """Estimate field strength from coupling and variance."""
    if coupling is None:
        return 0.0
    base = coupling * (1.0 - variance**0.5)
    return round(max(0.0, min(1.0, base)), 6)

def compute_field_strength():
    state = safe_read_json("/var/lib/skg/state/mep_state.json", {})
    coupling = state.get("coupling", 0.0)
    variance = state.get("variance", 0.0)
    strength = _derive_field_strength(coupling, variance)
    state["field_strength"] = strength
    safe_write_json("/var/lib/skg/state/mep_state.json", state)
    return strength

if __name__ == "__main__":
    strength = compute_field_strength()
    print(json.dumps({"field_strength": strength}, indent=2))
