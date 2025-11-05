#!/usr/bin/env python3
import sys
sys.path.append("/opt/skg")

"""
SKG Auto-Heal
Periodically checks integrity and proposes fixes.
"""
import os, json, hashlib, time
from skg.coder import propose_change
from skg.governance import append_event

WATCH_PATHS=[
    "/opt/skg/skg/physics.py",
    "/opt/skg/skg/predict.py",
    "/opt/skg/bin/skg"
]
HASH_FILE="/var/lib/skg/memory/autoheal.hashes.json"

def sha256(p):
    try:
        with open(p,"rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except: return None

def load_hashes():
    if os.path.exists(HASH_FILE):
        return json.load(open(HASH_FILE))
    return {}

def save_hashes(h):
    os.makedirs(os.path.dirname(HASH_FILE),exist_ok=True)
    json.dump(h,open(HASH_FILE,"w"),indent=2)

def loop(interval=600):
    prev=load_hashes()
    while True:
        cur={p:sha256(p) for p in WATCH_PATHS}
        for f,h in cur.items():
            if f not in prev:
                append_event({"actor":"autoheal","event":"baseline","file":f,"hash":h})
            elif prev[f]!=h:
                desc=f"detected drift in {os.path.basename(f)}"
                patch="# placeholder for repair; requires audit"
                propose_change(desc,f,patch)
                append_event({"actor":"autoheal","event":"drift","file":f,"old":prev[f],"new":h})
        save_hashes(cur)
        time.sleep(interval)

if __name__=="__main__":
    loop()
