#!/usr/bin/env python3
import subprocess

def run(scope: str = "/opt/skg", **_):
    # call your existing tool if present; otherwise noop
    try:
        out = subprocess.run(["/opt/skg/tools/skg_autoheal.py", scope], capture_output=True, text=True, timeout=120)
        return {"ok": (out.returncode == 0), "stdout": out.stdout[-2000:], "stderr": out.stderr[-2000:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
