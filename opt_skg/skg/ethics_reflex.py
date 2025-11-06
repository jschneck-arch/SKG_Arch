#!/usr/bin/env python3
"""
Ethics Reflex: post-hoc coherence analysis (no moral judgements).
Reads recent governance events and emits a reflection with a coherence score.
"""
import json, time, os
AUDIT="/var/lib/skg/memory/governance.audit.jsonl"

def tail_events(n=100):
    if not os.path.exists(AUDIT): return []
    with open(AUDIT) as f:
        lines=[l for l in f if l.strip()][-n:]
        return [json.loads(l) for l in lines]

def coherence_score(events):
    # toy: fewer forced rollbacks → higher coherence; more citations → higher
    rollbacks = sum(1 for e in events if e.get("event")=="rollback" or e.get("type")=="rollback")
    citations = sum(1 for e in events if "anchors" in e or "source" in e)
    total=max(1,len(events))
    base = 0.8 - 0.1*(rollbacks/total)
    boost = min(0.15, 0.01*citations)
    return round(max(0.0, min(1.0, base+boost)),3)

def reflect(n=100):
    ev=tail_events(n)
    return {"ts":time.time(),"actor":"ethics_reflex","events_analyzed":len(ev),
            "ethics_coherence":coherence_score(ev),
            "notes":"coherence=physics-of-consequence; no morals."}

if __name__=="__main__":
    print(json.dumps(reflect(),indent=2))
