#!/usr/bin/env python3
"""
Information Manifest: what SKG is (by information), not who.
Collects high-level counts + recent themes (terms) from pearls/audit/vault.
"""
import os, json, re, collections
from pathlib import Path

PEARLS="/var/lib/skg/memory/pearls.jsonl"
AUDIT ="/var/lib/skg/memory/governance.audit.jsonl"
VAULT ="/var/lib/skg/memory/learn_vault.jsonl"

def _read_jsonl(path, max_lines=800):
    if not os.path.exists(path): return []
    out=[]; 
    with open(path) as f:
        for i, line in enumerate(f):
            if not line.strip(): continue
            out.append(json.loads(line))
    return out[-max_lines:]

_TOKEN=re.compile(r"[A-Za-z0-9_.:-]{3,}")
_STOP=set(("the","and","for","with","that","this","from","into","about","skill","actor","type","json","http"))

def _terms(objs, max_terms=32):
    cnt=collections.Counter()
    for o in objs:
        txt=json.dumps(o, sort_keys=True)
        for t in _TOKEN.findall(txt.lower()):
            if t in _STOP: continue
            cnt[t]+=1
    return [w for w,_ in cnt.most_common(max_terms)]

def build_manifest():
    pearls=_read_jsonl(PEARLS)
    audit=_read_jsonl(AUDIT)
    vault=_read_jsonl(VAULT)
    themes=_terms(pearls+audit+vault, max_terms=48)
    return {
        "schema":"skg.manifest/v1",
        "counts": {
            "pearls": len(pearls),
            "audit": len(audit),
            "vault": len(vault)
        },
        "themes": themes[:48]   # top information tokens
    }
