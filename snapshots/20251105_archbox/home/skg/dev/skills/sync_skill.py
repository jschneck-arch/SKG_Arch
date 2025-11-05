#!/usr/bin/env python3
"""
SKG Skill: sync_skill
Synchronize the development tree to the live runtime tree.
"""

import os, subprocess, json, time

DEV = "/home/skg/dev"
LIVE = "/opt/skg"
LOG = "/var/lib/skg/memory/sync.log"

def run_skill(payload=None):
    t0 = time.time()
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    subprocess.run(["rsync","-a","--delete","/home/skg/dev/skills/","/opt/skg/skills/"])
    cmd = ["rsync", "-a", "--delete", f"{DEV}/", LIVE + "/"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    status = "ok" if result.returncode == 0 else "error"
    summary = {
        "skill": "sync_skill",
        "from": DEV,
        "to": LIVE,
        "status": status,
        "stdout": result.stdout[-300:],
        "stderr": result.stderr[-300:],
        "ts": t0,
        "duration": round(time.time() - t0, 2)
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(summary) + "\n")
    return summary

if __name__ == "__main__":
    print(json.dumps(run_skill(), indent=2))
