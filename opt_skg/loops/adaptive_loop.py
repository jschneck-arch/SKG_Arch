#!/usr/bin/env python3
"""
SKG Adaptive Loop — integrates audit deltas and assimilation health into reflection pearls.
"""

from pathlib import Path
import json, time

AUDIT = Path("/var/lib/skg/memory/governance.audit.jsonl")
PEARL = Path("/var/lib/skg/memory/pearl_audit_reflect.jsonl")
ASSIM_STATE = Path("/var/lib/skg/state/assimilation_state.json")
TELEMETRY = Path("/var/lib/skg/state/telemetry.json")

def integrate_audit():
    try:
        lines = AUDIT.read_text().strip().splitlines()[-10:]
    except Exception:
        lines = []
    pearls = []
    for ln in lines:
        try:
            rec = json.loads(ln)
            pearls.append({
                "ts": rec["ts"],
                "entropy_delta": rec.get("entropy_delta"),
                "coherence_delta": rec.get("coherence_delta"),
                "target": rec.get("target")
            })
        except:
            pass
    if pearls:
        PEARL.parent.mkdir(parents=True, exist_ok=True)
        with PEARL.open("a", encoding="utf-8") as f:
            for p in pearls:
                f.write(json.dumps(p) + "\n")

def compute_assimilation_health():
    health_ratio = 1.0
    failed = 0
    total = 0
    if ASSIM_STATE.exists():
        try:
            data = json.loads(ASSIM_STATE.read_text())
            results = data.get("results", {})
            total = len(results)
            failed = sum(1 for r in results.values() if not r.get("ok"))
            if total > 0:
                health_ratio = (total - failed) / total
        except Exception as e:
            print(f"assimilation_health read error: {e}")
    return {
        "assimilation_health": round(health_ratio, 4),
        "assimilation_failed": failed,
        "assimilation_total": total
    }

def update_telemetry():
    tdata = {}
    if TELEMETRY.exists():
        try:
            tdata = json.loads(TELEMETRY.read_text())
        except Exception:
            pass
    tdata.update(compute_assimilation_health())
    tdata["ts"] = time.time()
    TELEMETRY.parent.mkdir(parents=True, exist_ok=True)
    TELEMETRY.write_text(json.dumps(tdata, indent=2))

def main():
    integrate_audit()
    update_telemetry()

if __name__ == "__main__":
    main()
