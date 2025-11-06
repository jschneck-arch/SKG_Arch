#!/usr/bin/env python3
import os, time, json
from skg.physics_api import snapshot, record_moon_physics

def main():
    moon = os.environ.get("SKG_MOON_NAME","analysis")
    s = snapshot().get("telemetry",{})
    ent = float(s.get("entropy") or s.get("entropy_avg") or 0.0)
    coh = float(s.get("ethics_coherence") or 0.0)
    rec = record_moon_physics(moon, ent, coh, {"src":"pulse"})
    print(json.dumps(rec))

if __name__=="__main__":
    main()
