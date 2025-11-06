from skg.config.api_port import load
host, port = load()

#!/usr/bin/env python3
"""
SKG Brain — periodic cognition and evolution trigger.
Integrates assimilation health and telemetry awareness.
"""

import json, time, requests
from pathlib import Path

TELEMETRY = Path("/var/lib/skg/state/telemetry.json")

def get_assimilation_health():
    if TELEMETRY.exists():
        try:
            data = json.loads(TELEMETRY.read_text())
            return data.get("assimilation_health", 1.0)
        except Exception:
            return 1.0
    return 1.0

def call_skill(name, params):
    try:
        r = requests.post(f"http://{host}:{port}/skill/{name}", json={"params": params}, timeout=30)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    while True:
        health = get_assimilation_health()
        msg = f"self audit cycle — assimilation_health={health}"
        call_skill("cognition", {"prompt": msg})
        if health < 0.8:
            # initiate reinforcement or repair if system is degraded
            call_skill("autoheal", {"prompt": "repair degraded assimilation"})
        # every 30 min evolve
        if int(time.time()) % 1800 < 60:
            call_skill("evolve", {"prompt": "optimize reflection and telemetry stability"})
        time.sleep(600)

if __name__ == "__main__":
    main()
