import os, json, time
AUDIT = "/var/lib/skg/memory/governance.audit.jsonl"
def append_event(evt):
    os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
    evt = dict(evt); evt.setdefault("ts", time.time())
    with open(AUDIT,"a") as f: f.write(json.dumps(evt)+"\n")
    return evt

# --- SKG add-on: audit_coder shim (ethics = measurable coherence; no morals) ---
# Provides a stable interface for skg.coder and autoheal to write audited events.

import os, json
from time import time as _now

_AUDIT_PATH = "/var/lib/skg/memory/governance.audit.jsonl"

def _ensure_audit_dir():
    os.makedirs(os.path.dirname(_AUDIT_PATH), exist_ok=True)

# If append_event is missing, define a minimal one.
try:
    append_event  # type: ignore  # noqa: F821
except NameError:  # append_event not defined in this file yet
    def append_event(event: dict):
        _ensure_audit_dir()
        with open(_AUDIT_PATH, "a") as f:
            f.write(json.dumps(event) + "\n")

def audit_coder(action: str, **fields):
    """
    Minimal audit hook used by skg.coder and autoheal.
    Records coder/autoheal actions to the unified governance audit log.
    """
    evt = {"ts": _now(), "actor": "coder", "event": action}
    if fields:
        evt.update(fields)
    append_event(evt)
    return evt
# --- end add-on ---

# --- audit_coder passthrough for backward-compat ---
try:
    from skg.audit_coder import record as audit_coder
except Exception as _e:
    def audit_coder(*args, **kwargs):
        # fallback no-op if audit module not available
        return {"ok": False, "error": str(_e)}

# === Moon quorum aggregation (votes) ===
import json, time
from pathlib import Path

_VOTE_DIR = Path("/var/lib/skg/memory/moon_votes")
_VOTE_DIR.mkdir(parents=True, exist_ok=True)

def quorum(votes:list[dict], threshold:float=0.70, min_ok:int=1)->bool:
    ok_votes = [v for v in votes if v.get("ok")]
    if len(ok_votes) < min_ok:
        return False
    scores = [float(v.get("score",0.0)) for v in ok_votes]
    avg = sum(scores)/len(scores) if scores else 0.0
    return avg >= threshold

def evaluate_with_moons(task:str, threshold:float=0.70)->dict:
    votes = collect_moon_votes(task)
    passed = quorum(votes, threshold=threshold, min_ok=1)
    avg = (sum([v.get("score",0.0) for v in votes])/max(1,len(votes))) if votes else 0.0
    return {"task":task,"passed":passed,"average_score":avg,"votes":votes}
# --- augment evaluate_with_moons with physics snapshot summary ---
from skg.physics_api import collect_moon_physics

def evaluate_with_moons(task:str, threshold:float=0.70)->dict:
    votes = collect_moon_votes(task)
    passed = quorum(votes, threshold=threshold, min_ok=1)
    avg = (sum([v.get("score",0.0) for v in votes])/max(1,len(votes))) if votes else 0.0
    physics = collect_moon_physics()
    # produce small aggregation
    phys_summary = {}
    if physics:
        entropies = [p.get("entropy",0.0) for p in physics]
        coherences = [p.get("coherence",0.0) for p in physics]
        phys_summary = {
            "samples": len(physics),
            "entropy_avg": sum(entropies)/len(entropies) if entropies else 0.0,
            "coherence_avg": sum(coherences)/len(coherences) if coherences else 0.0
        }
    return {"task":task,"passed":passed,"average_score":avg,"votes":votes,"physics": phys_summary}
from skg.crypto_utils import verify
from skg.edcrypto import verify
import time, json
from pathlib import Path

def collect_moon_votes(task:str, window_s:int=600)->list[dict]:
    now=time.time()
    votes=[]
    for p in Path("/var/lib/skg/memory/moon_votes").glob("*.jsonl"):
        for L in p.read_text().splitlines()[-50:]:
            try:
                rec=json.loads(L); base=rec["data"]; sig=rec["sig"]; moon=base["moon"]
                if base.get("task")==task and (now-base["ts"])<=window_s:
                    if verify(base, sig, moon):
                        votes.append(base)
            except Exception:
                continue
    return votes
