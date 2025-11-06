#!/usr/bin/env python3
"""
SKG Lifecycle Framework
Defines operational phases and manages transitions.
"""
import json, time, os
from pathlib import Path

STATE_FILE = Path("/var/lib/skg/state/lifecycle.json")
PHASES = ["genesis","awakening","reflection","synthesis","dormancy","regeneration"]
_state = {"phase":"awakening","ts":time.time(),"note":"boot"}

def save_state():
    STATE_FILE.parent.mkdir(parents=True,exist_ok=True)
    with open(STATE_FILE,"w") as f: json.dump(_state,f,indent=2)

def set_phase(p:str,note:str=""):
    if p not in PHASES: raise ValueError(f"unknown phase {p}")
    _state.update({"phase":p,"ts":time.time(),"note":note})
    save_state(); return _state

def current(): 
    if STATE_FILE.exists():
        return json.load(open(STATE_FILE))
    return _state

def advance(note="auto"):
    idx=PHASES.index(current().get("phase","awakening"))
    nxt=PHASES[(idx+1)%len(PHASES)]
    return set_phase(nxt,note)

if __name__=="__main__":
    import sys
    if len(sys.argv)>1: set_phase(sys.argv[1])
    else: print(json.dumps(current(),indent=2))
