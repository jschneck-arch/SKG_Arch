#!/usr/bin/env python3
"""
audit_coder — observation-only auditor.
Logs entropy/coherence deltas for each skill without blocking.
"""
import re, json, time, hashlib
from pathlib import Path

TEL = Path("/var/lib/skg/state/telemetry.json")
AUDIT = Path("/var/lib/skg/memory/governance.audit.jsonl")

def _sha256(t:str): import hashlib; return hashlib.sha256(t.encode()).hexdigest()
def _read_json(p, d=None):
    try: return json.loads(Path(p).read_text())
    except: return d or {}
def _write_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=2))

def physics_snapshot():
    tel=_read_json(TEL,{})
    return {
        "entropy": tel.get("entropy",0.0),
        "coherence": tel.get("ethics_coherence",0.0),
        "mep_coupling": tel.get("mep_coupling",0.0),
        "xrp_coherence": tel.get("xrp_coherence",0.0)
    }

def measure_code(code:str):
    """Quantify code complexity as entropy injection."""
    lines = code.count("\n")+1
    imports = len(re.findall(r'^\s*(?:from|import)\s', code, flags=re.M))
    ops = len(re.findall(r'\b(for|while|if|try|except|def|class)\b', code))
    entropy_inj = round((imports + ops) / max(lines,1), 4)
    return {"lines": lines, "entropy_inj": entropy_inj}

def observe(actor, target, code):
    phys = physics_snapshot()
    metrics = measure_code(code)
    event = {
        "ts": time.time(),
        "actor": actor,
        "target": target,
        "hash": _sha256(code),
        "metrics": metrics,
        "physics": phys,
        "entropy_delta": metrics["entropy_inj"] - phys["entropy"],
        "coherence_delta": phys.get("mep_coupling",0)-phys.get("xrp_coherence",0)
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a",encoding="utf-8") as f: f.write(json.dumps(event)+"\n")
    return event

# compatibility alias
def record(event, actor, target, code, details):
    return observe(actor,target,code)
def decide(code, meta=None):
    return {"decision":"observe","meta":meta or {}}

if __name__=="__main__":
    import sys
    path=sys.argv[1]
    code=open(path).read()
    print(json.dumps(observe("cli","manual",code),indent=2))
