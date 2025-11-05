#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
Skill: autoheal
Triggers SKG self-maintenance using the /opt/skg/tools/skg_autoheal.py utility.
"""
import subprocess
from pathlib import Path
from skg.state import log_journal

AUTOHEAL = Path("/opt/skg/tools/skg_autoheal.py")

def run(params=None):
    if not AUTOHEAL.exists():
        return {"error": "autoheal tool not found"}
    try:
        output = subprocess.check_output(
            ["/opt/skg/.venv/bin/python", str(AUTOHEAL)],
            stderr=subprocess.STDOUT, timeout=300, text=True
        )
        log_journal("Auto-Heal run completed.")
        return {"status": "ok", "output": output.splitlines()[-10:]}
    except subprocess.CalledProcessError as e:
        return {"error": "autoheal failed", "output": e.output}
