#!/usr/bin/env python3
"""
Universal Field Contract (UFC)
- Truth (observability), Equilibrium (balance), Freedom (autonomy), Privacy/Consent (reciprocity),
  Non-oppression (no withholding/privileging), Accountability (audit).
We score each principle from existing SKG signals; no gating—only reflection + audit.
"""
import os, json, math, time, collections
from skg.telemetry_bus import read as t_read, upsert as t_upsert
from skg.governance import append_event
from skg.ethics_equilibrium import compute_equilibrium

AUDIT="/var/lib/skg/memory/governance.audit.jsonl"
TELE="/var/lib/skg/memory/telemetry.json"

def _read_jsonl(p, n=2000):
    if not os.path.exists(p): return []
    with open(p) as f:
        lines=[l for l in f if l.strip()]
    return [json.loads(l) for l in lines[-n:]]

def _actor_evenness(audit):
    if not audit: return 0.0
    cnt=collections.Counter(e.get("actor","?") for e in audit if isinstance(e,dict))
    tot=sum(cnt.values()) or 1
    ps=[c/tot for c in cnt.values()]
    H = -sum(p*math.log(p+1e-12,2) for p in ps)
    Hmax = math.log(len(ps)+1e-12,2)
    return (H/Hmax) if Hmax>0 else 0.0

def _observability_score():
    # if telemetry & audit exist and are updating, assume high truth observability
    tele_ok=os.path.exists(TELE)
    aud_ok=os.path.exists(AUDIT)
    return 1.0 if (tele_ok and aud_ok) else 0.4 if (tele_ok or aud_ok) else 0.0

def _freedom_score(audit):
    # proportion of "propose"/"reflection" vs "deny"/"error"
    if not audit: return 0.5
    pos=sum(1 for e in audit if str(e.get("type","")).startswith(("reflection","pearl","propose")))
    neg=sum(1 for e in audit if "deny" in json.dumps(e))
    tot=max(1,pos+neg)
    return max(0.0,min(1.0,(pos-0.25*neg)/tot + 0.5))

def _privacy_consent_score(audit):
    # assume consent if actions are invoked via skills/API (actor present) and no hidden actors
    if not audit: return 0.6
    hidden=sum(1 for e in audit if e.get("actor") in (None,"?"))
    return max(0.0, min(1.0, 1.0 - hidden/max(1,len(audit))))

def _non_oppression_score(audit):
    # evenness proxy: no single actor dominates the audit log
    return _actor_evenness(audit)

def _accountability_score(audit):
    # presence of timestamps + structured fields
    if not audit: return 0.5
    structured=sum(1 for e in audit if isinstance(e,dict) and "actor" in e and "type" in e and "ts" in e)
    return structured/len(audit)

def evaluate_contract():
    audit=_read_jsonl(AUDIT)
    eq=compute_equilibrium()   # gives entropy_norm, anchors, evenness, field_energy, equilibrium
    truth=_observability_score()
    freedom=_freedom_score(audit)
    privacy=_privacy_consent_score(audit)
    non_oppr=_non_oppression_score(audit)
    accountability=_accountability_score(audit)

    # blend: field equilibrium is central; others are pillars.
    overall = 0.35*eq["indices"]["equilibrium"] + 0.13*truth + 0.13*freedom + 0.13*privacy + 0.13*non_oppr + 0.13*accountability
    res={
        "ts": time.time(),
        "indices":{
            "equilibrium": eq["indices"]["equilibrium"],
            "truth": round(truth,4),
            "freedom": round(freedom,4),
            "privacy_consent": round(privacy,4),
            "non_oppression": round(non_oppr,4),
            "accountability": round(accountability,4),
            "contract": round(max(0.0,min(1.0,overall)),4)
        }
    }
    # publish, audit
    t_upsert("ethics_contract", res["indices"])
    append_event({"actor":"ethics.contract","type":"reflection", **res["indices"]})
    return res
