#!/usr/bin/env python3
import json, time, subprocess
from pathlib import Path

STATE = Path("/var/lib/skg/state/telemetry.json")
LAST = Path("/var/lib/skg/state/.api_restart_last.txt")

def read_json(p, default):
    try: return json.loads(p.read_text())
    except: return default

def write_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def get_active_enter_ts():
    try:
        out = subprocess.check_output(
            ["systemctl", "show", "skg-api.service", "--property=ActiveEnterTimestampMonotonic", "--value"],
            text=True
        ).strip()
        return int(out) if out.isdigit() else 0
    except Exception:
        return 0

def main():
    last = LAST.read_text().strip() if LAST.exists() else ""
    while True:
        ts = str(get_active_enter_ts())
        if ts and ts != last:
            t = read_json(STATE, {})
            t["api_restart_count"] = int(t.get("api_restart_count") or 0) + 1
            t["last_api_restart"]  = int(time.time())
            write_json(STATE, t)
            LAST.parent.mkdir(parents=True, exist_ok=True)
            LAST.write_text(ts)
        time.sleep(5)

if __name__ == "__main__":
    main()
