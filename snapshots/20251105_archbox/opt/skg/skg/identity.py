#!/usr/bin/env python3
"""
Anonymous identity derived from information, not names.
We compute content hashes of SKG's public state: governance stats, vault stats, code module digests.
This yields a stable, non-reversible "info-fingerprint".
"""
import hashlib, json, os, glob

AUDIT = "/var/lib/skg/memory/governance.audit.jsonl"
VAULT = "/var/lib/skg/memory/learn_vault.jsonl"

def _sha256_bytes(b: bytes)->str:
    return hashlib.sha256(b).hexdigest()

def _file_tail(path, max_lines=200):
    if not os.path.exists(path): return []
    with open(path, "rb") as f:
        data = f.readlines()[-max_lines:]
    try: return [x.decode("utf-8","ignore").strip() for x in data if x.strip()]
    except: return []

def _code_digests(root="/opt/skg/skg"):
    dig = {}
    for p in sorted(glob.glob(os.path.join(root, "*.py"))):
        try:
            with open(p,"rb") as f: dig[os.path.basename(p)] = _sha256_bytes(f.read())
        except: pass
    return dig

def info_fingerprint():
    # summarize recent observable state
    tail_audit = _file_tail(AUDIT, 300)
    tail_vault = _file_tail(VAULT, 300)
    code = _code_digests()
    summary = {
        "audit_count": len(tail_audit),
        "vault_count": len(tail_vault),
        "code_mods": code,  # file -> sha256
    }
    # anonymized fingerprint of the summary (not reversible)
    raw = json.dumps(summary, sort_keys=True).encode()
    return {
        "fingerprint": _sha256_bytes(raw),
        "features": {
            "audit_nonempty": bool(tail_audit),
            "vault_nonempty": bool(tail_vault),
            "code_files": len(code)
        }
    }
