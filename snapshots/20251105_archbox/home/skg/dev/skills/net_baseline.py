#!/usr/bin/env python3
"""Skill: net_baseline - observe local network topology"""
import subprocess, json, time
from skg.governance import append_event

def run(**params):
    try:
        # Use ss for open ports
        out = subprocess.run(["ss","-tuln"], capture_output=True, text=True, timeout=5).stdout
        lines = [l for l in out.splitlines() if "LISTEN" in l or "ESTAB" in l]
        res = {"count": len(lines), "sample": lines[:5], "ts": time.time()}
        append_event({"actor":"net_baseline","type":"snapshot","ports":len(lines)})
        return res
    except Exception as e:
        return {"error": str(e)}
