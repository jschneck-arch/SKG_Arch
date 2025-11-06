#!/usr/bin/env python3
import json, time
from pathlib import Path

STATE = Path("/var/lib/skg/state/telemetry.json")
LOG = Path("/var/lib/skg/memory/api_watchdog.jsonl")

def read_json(p, default): 
    try: return json.loads(p.read_text())
    except: return default

def write_json(p, data): 
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def main():
    while True:
        t = read_json(STATE, {})
        restarts = t.get("api_restart_count", 0)
        last = t.get("last_api_restart", 0)
        record = {"ts": time.time(), "api_restart_count": restarts, "last_api_restart": last}
        with LOG.open("a") as f: f.write(json.dumps(record) + "\n")
        time.sleep(300)  # every 5 minutes

if __name__ == "__main__":
    main()
