#!/usr/bin/env python3
import os, time
from skg.coder import propose_change
from skg.governance import append_event
SKILL_DIR="/home/skg/dev/skills"
def run(**params):
    name=params.get("name"); content=params.get("content","")
    if not name: return {"ok":False,"error":"name required"}
    path=f"{SKILL_DIR}/{name}.py"
    propose_change(f"skillforge: {name}", path, content)
    append_event({"actor":"skillforge","type":"skill_change","skill":name})
    return {"ok":True,"status":"queued","skill":name,"path":path}
