#!/usr/bin/env python3
import subprocess
from skg.governance_gate import allow

def run(action: str = "status", unit: str = "", why: str = "", who: str = "skg-api", **_):
    if action == "status":
        out = subprocess.run(["systemctl","list-units","--type=service","--state=running"],
                             capture_output=True, text=True, timeout=4)
        return {"ok": True, "output": out.stdout[-6000:]}
    # allow everything, but *audit + ethics gate* first
    ok, msg = allow(action, unit, who, why)
    if not ok:
        return {"ok": False, "error": f"denied: {msg}"}
    r = subprocess.run(["systemctl", action, unit], capture_output=True, text=True)
    return {"ok": (r.returncode==0), "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:], "unit": unit, "action": action}
