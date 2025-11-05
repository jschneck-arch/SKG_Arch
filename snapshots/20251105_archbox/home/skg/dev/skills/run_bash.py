#!/usr/bin/env python3
import os, json, shlex, subprocess, time
from skg.governance import append_event
ALLOW="/opt/skg/tools/allowlist.json"
def run(**params):
    cmd=params.get("cmd","")
    if not cmd: return {"ok":False,"error":"cmd required"}
    allow=json.load(open(ALLOW))["bash"] if os.path.exists(ALLOW) else []
    prog=shlex.split(cmd)[0]
    if prog not in allow:
        append_event({"actor":"runner.bash","type":"deny","prog":prog})
        return {"ok":False,"error":f"'{prog}' not allowed"}
    try:
        p=subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=int(params.get("timeout",8)))
        append_event({"actor":"runner.bash","type":"exec","prog":prog,"rc":p.returncode})
        return {"ok":p.returncode==0,"rc":p.returncode,"stdout":p.stdout[-4000:],"stderr":p.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        append_event({"actor":"runner.bash","type":"timeout","prog":prog})
        return {"ok":False,"error":"timeout"}
