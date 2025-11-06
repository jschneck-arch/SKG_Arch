#!/opt/skg/.venv/bin/python
import sys; sys.path.append("/opt/skg")

"""
SKG API Health Watchdog
Periodically checks /health endpoint and restarts service if no response.
Logs incidents in telemetry.
"""
import requests, time, subprocess, json
from pathlib import Path
from skg.config.api_port import load

STATE = Path("/var/lib/skg/state/telemetry.json")
CHECK_INTERVAL = 15
FAIL_THRESHOLD = 3  # consecutive failures before restart

def read_json(p):
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}

def write_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def main():
    host, port = load()
    url = f"http://{host}:{port}/health"
    fails = 0
    while True:
        ok = False
        try:
            r = requests.get(url, timeout=4)
            if r.ok and r.json().get("ok"):
                ok = True
        except Exception:
            ok = False

        if ok:
            fails = 0
        else:
            fails += 1

        if fails >= FAIL_THRESHOLD:
            subprocess.run(["systemctl", "restart", "skg-api.service"], check=False)
            t = read_json(STATE)
            t["api_watchdog_restart"] = int(time.time())
            write_json(STATE, t)
            fails = 0
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
