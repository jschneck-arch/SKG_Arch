#!/usr/bin/env python3
"""
SKG Moon Launcher — start/stop/status auxiliary 'moons' as lightweight subprocesses.

Usage:
  python moon_launcher.py start [name]    # start one or ALL moons
  python moon_launcher.py stop  [name]    # stop one or ALL moons
  python moon_launcher.py status          # list pids per moon
"""

import subprocess, sys, json
from pathlib import Path

# Map moon names to the script they should run
MOONS = {
    "analysis":  "/opt/skg/skills/cognition.py",
    "governance":"/opt/skg/skg/audit_coder.py",
    "skillmaker":"/opt/skg/tools/skillmaker.py",
    "agent":     "/opt/skg/skills/agent.py",
}

LOGDIR = Path("/var/log/skg"); LOGDIR.mkdir(parents=True, exist_ok=True)
PY = "/opt/skg/.venv/bin/python"
ENV = {"PYTHONPATH": "/opt/skg"}

def start(name):
    target = MOONS[name]
    log = LOGDIR / f"moon_{name}.log"
    with log.open("a") as f:
        p = subprocess.Popen([PY, target], stdout=f, stderr=f, text=True, env={**ENV, **dict()})
    print(f"🌕 launched moon '{name}' pid={p.pid}")

def stop(name):
    target = MOONS[name]
    subprocess.run(f"pkill -f {target}", shell=True)
    print(f"🌘 stopped moon '{name}'")

def status():
    result = {}
    for name, path in MOONS.items():
        rc = subprocess.run(f"pgrep -af {path}", shell=True, capture_output=True, text=True)
        result[name] = rc.stdout.strip().splitlines()
    print(json.dumps(result, indent=2))

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage: moon_launcher.py start|stop|status [name]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "status":
        status()
    elif cmd in ("start","stop"):
        if len(sys.argv)==3 and sys.argv[2] in MOONS:
            locals()[cmd](sys.argv[2])
        else:
            for n in MOONS: locals()[cmd](n)
    else:
        print("unknown command")
        sys.exit(2)
