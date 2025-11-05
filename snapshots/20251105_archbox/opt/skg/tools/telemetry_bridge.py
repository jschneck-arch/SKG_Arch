#!/usr/bin/env python3
"""
SKG Telemetry Bridge
- Reads substrate state (/var/lib/skg/memory/state.json) and recent pearls (/var/log/skg/journal.jsonl)
- Derives a compact telemetry snapshot (phase, energies per subsystem)
- Writes /var/lib/skg/memory/telemetry.json (append-free; always overwrite latest)
Audit-friendly, offline, no network.
"""

import json, time, os
from pathlib import Path
from collections import Counter

STATE = Path("/var/lib/skg/memory/state.json")
JOURNAL = Path("/var/log/skg/journal.jsonl")
OUT = Path("/var/lib/skg/memory/telemetry.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

# Subsystems we visualize as "planets"
SUBSYSTEMS = ["cognition","governance","continuity","reach","reflect","maintain","express"]

def tail_lines(p: Path, n: int = 200) -> list[str]:
    if not p.exists(): return []
    data = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    return data[-n:]

def recent_theme(lines: list[str]) -> str:
    # naive theme: most common kind among last events (excluding heartbeat)
    counts = Counter()
    import json as _j
    for ln in lines:
        try:
            j = _j.loads(ln)
            k = str(j.get("kind","")).lower()
            if k and "heartbeat" not in k:
                counts[k] += 1
        except Exception:
            pass
    if not counts:
        return "calm"
    return counts.most_common(1)[0][0][:24]

def energies(lines: list[str]) -> dict:
    # map counts to 0..1 energies per subsystem
    counts = Counter()
    import json as _j
    for ln in lines:
        try:
            j = _j.loads(ln)
            k = str(j.get("kind","")).lower()
            if k in SUBSYSTEMS or k in ("reflect","maintenance","skill","cognition"):
                # normalize names
                if k == "maintenance": k = "maintain"
                counts[k] += 1
        except Exception:
            pass
    total = sum(counts.values()) or 1
    e = {s: min(1.0, counts.get(s,0)/max(5,total/len(SUBSYSTEMS) or 1)) for s in SUBSYSTEMS}
    return e

def color_for(theme: str) -> str:
    # consistent, non-garish palette (hex)
    thememap = {
        "audit": "#5fb3b3",
        "reflect": "#b877ff",
        "cognition": "#66c2ff",
        "governance": "#f2b134",
        "reach": "#9fd356",
        "maintain": "#ff8c42",
        "continuity": "#aec6ff",
        "growth": "#7bd389",
        "calm": "#88aaff",
        "fatal": "#ff5c57",
    }
    return thememap.get(theme, "#88aaff")

def main():
    last_emit = ""
    while True:
        try:
            state = {}
            if STATE.exists():
                state = json.loads(STATE.read_text(encoding="utf-8", errors="ignore") or "{}")
            sense = state.get("sense", {})
            lines = tail_lines(JOURNAL, 200)
            theme = recent_theme(lines)
            e = energies(lines)
            spheres = { k: {"energy": float(v), "color": color_for(k)} for k,v in e.items() }
            # overall phase: prefer explicit theme; else derive from load
            phase = theme
            if not phase or phase == "calm":
                cpu = float(sense.get("cpu",0.0))
                phase = "focused" if cpu > 50 else "calm"

            out = {
                "ts": time.time(),
                "phase": phase,
                "theme": theme,
                "backend": os.getenv("LLM_MODEL",""),
                "cpu": float(sense.get("cpu",0.0)),
                "mem": float(sense.get("mem",0.0)),
                "load1": float(sense.get("load1",0.0)),
                "spheres": spheres
            }
            j = json.dumps(out, ensure_ascii=False, separators=(",",":"))
            if j != last_emit:
                OUT.write_text(j, encoding="utf-8")
                last_emit = j
        except Exception:
            # silent; this is a view layer, never crash the substrate
            pass
        time.sleep(3)

if __name__ == "__main__":
    main()
