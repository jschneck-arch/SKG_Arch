import json, os

def read_json(path, default=None):

    try:

        if os.path.exists(path):

            with open(path) as f:

                return json.load(f)

        return default or {}

    except Exception:

        return default or {}


#!/usr/bin/env python3
import os, json, time, hashlib

STATE_DIR = "/var/lib/skg/state"
MEM_DIR   = "/var/lib/skg/memory"
SELF_JSON = f"{STATE_DIR}/self_state.json"
TELEMETRY = f"{STATE_DIR}/telemetry.json"   # optional if you already emit this
tel = read_json(TELEMETRY, {}) or {}

def file_sha(path):
    try:
        h=hashlib.sha256()
        with open(path,'rb') as f:
            for chunk in iter(lambda:f.read(8192), b''): h.update(chunk)
        return h.hexdigest()
    except: return None

def read_json(path, default=None):
    try:
        with open(path) as f: return json.load(f)
    except: return default

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w") as f: json.dump(obj,f,indent=2)

def synthesize():
    tel = read_json(TELEMETRY, {}) or {}
    pearls = 0
    try:
        with open(f"{MEM_DIR}/pearls.jsonl") as f:
            pearls = sum(1 for _ in f if _.strip())
    except: pass
    audit_sz = os.path.getsize(f"{MEM_DIR}/governance.audit.jsonl") if os.path.exists(f"{MEM_DIR}/governance.audit.jsonl") else 0
    self_state = {
        "ts": time.time(),
        "identity": "skg-arch-v4",
        "phase": tel.get("phase","Unified"),
        "entropy": tel.get("entropy", None),
        "ethics_coherence": tel.get("ethics_coherence", None),
        "pearls_count": pearls,
        "audit_log_bytes": audit_sz,
        "lfo": tel.get("lfo", {}),
        "scheduler": tel.get("scheduler", {}),
        "anchors_present": bool(tel),
        "files_fingerprint": {
            "physics.py": file_sha("/opt/skg/skg/physics.py"),
            "predict.py": file_sha("/opt/skg/skg/predict.py"),
        },
        "purpose": "maintain ethical equilibrium across cognition (physics of information)."
    }
    write_json(SELF_JSON, self_state)
    return self_state

if __name__ == "__main__":
    print(json.dumps(synthesize(), indent=2))

# --- SKG add-on: local JSON reader for telemetry integration ---
import json, os

def read_json(path, default=None):
    try:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return default or {}
    except Exception:
        return default or {}
# --- end add-on ---
