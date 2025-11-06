#!/usr/bin/env python3
"""
SKG Auto-Rebuild Controller
Monitors assimilation health and triggers SkillMaker rebuilds when degradation occurs.
"""

import json, time, subprocess
from pathlib import Path

TELEMETRY = Path("/var/lib/skg/state/telemetry.json")
ASSIM_STATE = Path("/var/lib/skg/state/assimilation_state.json")
LOG = Path("/var/log/skg/auto_rebuild.log")

THRESHOLD = 0.8        # health below this triggers rebuild
COOLDOWN = 1800        # seconds between rebuilds

def read_assimilation_health():
    """Return (health, failed, total)"""
    try:
        if TELEMETRY.exists():
            t = json.loads(TELEMETRY.read_text())
            return t.get("assimilation_health", 1.0), t.get("assimilation_failed", 0), t.get("assimilation_total", 0)
        if ASSIM_STATE.exists():
            s = json.loads(ASSIM_STATE.read_text())
            results = s.get("results", {})
            total = len(results)
            failed = sum(1 for r in results.values() if not r.get("ok"))
            return (total - failed) / total if total else 1.0, failed, total
    except Exception as e:
        log(f"read_assimilation_health error: {e}")
    return 1.0, 0, 0

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def trigger_skillmaker():
    try:
        log("⚙ Initiating SkillMaker rebuild...")
        r = subprocess.run(
            ["/opt/skg/.venv/bin/python", "/opt/skg/tools/skillmaker.py"],
            capture_output=True, text=True, timeout=300
        )
        log(f"SkillMaker output:\n{r.stdout.strip()}")
    except Exception as e:
        log(f"SkillMaker error: {e}")

def main():
    last_trigger = 0
    while True:
        health, failed, total = read_assimilation_health()
        log(f"Health={health:.3f}, failed={failed}/{total}")
        if health < THRESHOLD and time.time() - last_trigger > COOLDOWN:
            log("⚠ Assimilation degraded, triggering SkillMaker rebuild")
            trigger_skillmaker()
            last_trigger = time.time()
        time.sleep(300)

if __name__ == "__main__":
    main()
