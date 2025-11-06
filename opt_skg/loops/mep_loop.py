#!/usr/bin/env python3
import json, time
from pathlib import Path

STATE = Path("/var/lib/skg/state/mep_state.json")
while True:
    data = {
        "ts": time.time(),
        "coupling": 0.99,
        "entropy_avg": 0.74,
        "variance": 0.0004
    }
    STATE.write_text(json.dumps(data))
    time.sleep(30)
