#!/usr/bin/env python3
"""
SKG Auto-Heal Loop
Performs periodic integrity checks and proposes repairs when anomalies are detected.
"""
import os, json, time, hashlib, subprocess
from skg.coder import propose_change
from skg.governance import append_event

STATE_DIR="/var/lib/skg/memory"
HASH_FILE=f"{STATE_DIR}/integrity.hashes.json"

def sha256sum(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(8192),b''):
            h.update(chunk)
    return h.hexdigest()

def snapshot():
    """Record hashes of critical SKG files."""
    files=[]
    for base,_,names in os.walk("/opt/skg/skg"):
        for n in names:
            if n.endswith(".py"):
                files.append(os.path.join(base,n))
    hashes={f:sha256sum(f) for f in files}
    json.dump(hashes,open(HASH_FILE,"w"),indent=2)
    return hashes

def check_integrity():
    if not os.path.exists(HASH_FILE):
        append_event({"actor":"autoheal","type":"init_hashes"})
        return snapshot()
    old=json.load(open(HASH_FILE))
    current=snapshot()
    diffs=[f for f in current if old.get(f)!=current[f]]
    if diffs:
        patch="\n".join([f"# Detected diff in {f}" for f in diffs])
        propose_change("autoheal integrity repair", diffs[0], patch)
        append_event({"actor":"autoheal","type":"diff_detected","files":diffs})
    else:
        append_event({"actor":"autoheal","type":"ok"})
    return diffs

def run_loop(interval=900):
    while True:
        check_integrity()
        time.sleep(interval)

if __name__=="__main__":
    run_loop()
