#!/usr/bin/env python3
import json, time
from pathlib import Path
TEL=Path("/var/lib/skg/state/telemetry.json")
CSV=Path("/var/lib/skg/state/ethics_entropy.csv")

t=time.time()
try:
    d=json.loads(TEL.read_text())
    ent=d.get("entropy") or d.get("entropy_avg")
    eth=d.get("ethics_coherence")
except Exception:
    ent=eth=None

CSV.parent.mkdir(parents=True,exist_ok=True)
hdr=not CSV.exists()
with open(CSV,"a") as f:
    if hdr: f.write("ts,entropy,ethics_coherence\n")
    f.write(f"{t},{'' if ent is None else ent},{'' if eth is None else eth}\n")
print(f"logged to {CSV}")
