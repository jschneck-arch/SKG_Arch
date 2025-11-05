#!/usr/bin/env python3
"""
SKG Brain – periodic cognition and evolution trigger.
Uses internal skills instead of cron.
"""

import json, time, requests

def call_skill(name, params):
    try:
        r = requests.post(f"http://127.0.0.1:5055/skill/{name}", json={"params": params}, timeout=30)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    while True:
        # every 10 min: self-audit
        call_skill("cognition", {"prompt": "self audit cycle"})
        # every 30 min: evolve proposal
        if int(time.time()) % 1800 < 60:
            call_skill("evolve", {"prompt": "optimize logging or telemetry stability"})
        time.sleep(600)

if __name__ == "__main__":
    main()
