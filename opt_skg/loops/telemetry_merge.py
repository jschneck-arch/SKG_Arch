#!/usr/bin/env python3
import json, time
from pathlib import Path

STATE = Path("/var/lib/skg/state")
telemetry = STATE / "telemetry.json"
mep_state = STATE / "mep_state.json"
xrp_state = STATE / "xrp_state.json"

def safe_load(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

while True:
    tele = safe_load(telemetry)
    mep = safe_load(mep_state)
    xrp = safe_load(xrp_state)
    if mep and xrp:
        field_strength = round(((mep.get("coupling", 0) + xrp.get("coherence", 0)) / 2), 3)
        tele.update({
            "mep_coupling": mep.get("coupling"),
            "xrp_coherence": xrp.get("coherence"),
            "field_strength": field_strength,
            "ts": time.time()
        })
        telemetry.write_text(json.dumps(tele))
    time.sleep(30)
