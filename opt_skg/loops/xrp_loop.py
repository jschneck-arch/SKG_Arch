#!/usr/bin/env python3
import json, time
from pathlib import Path

STATE = Path("/var/lib/skg/state/xrp_state.json")
while True:
    data = {
        "ts": time.time(),
        "coherence": 0.995,
        "phase_error": 0.0001,
        "coupling": 0.91
    }
    STATE.write_text(json.dumps(data))
    time.sleep(30)
