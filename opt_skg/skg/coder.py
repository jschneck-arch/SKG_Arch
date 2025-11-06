#!/usr/bin/env python3
"""
SKG self-coding assistant.
Allows SKG to suggest or apply code with human co-sign, fully audited.
"""
import os, time, json, subprocess
from typing import Dict, Any
from skg.governance import audit_coder

CODER_QUEUE="/var/lib/skg/memory/coder.queue.jsonl"

def ensure_files():
    os.makedirs(os.path.dirname(CODER_QUEUE), exist_ok=True)
    open(CODER_QUEUE,"a").close()

def propose_change(desc: str, filename: str, patch: str) -> Dict[str,Any]:
    ensure_files()
    proposal={
        "ts": time.time(),
        "desc": desc,
        "filename": filename,
        "patch": patch,
        "status": "proposed"
    }
    with open(CODER_QUEUE,"a") as f:
        f.write(json.dumps(proposal)+"\n")
    audit_coder("propose", filename, "queued")
    return proposal

def apply_change(filename: str, patch: str) -> str:
    ensure_files()
    tmp=f"/tmp/skg_patch_{os.getpid()}.diff"
    open(tmp,"w").write(patch)
    try:
        subprocess.check_call(["patch",filename,tmp])
        audit_coder("apply", filename, "success")
        return "applied"
    except subprocess.CalledProcessError as e:
        audit_coder("apply", filename, f"failed:{e}")
        return "failed"
    finally:
        os.remove(tmp)
