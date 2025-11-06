#!/usr/bin/env python3
"""
ethics_equilibrium: truth = equilibrium of information-as-energy

No gatekeeping. We *measure* balance using:
  - entropy balance from prediction pearls,
  - actor evenness in governance (no one actor dominates),
  - anchor coverage (pearls cite evidence "why"),
  - field energy from spherical waveform + gravity proxy,
Then publish indices into telemetry.ethics and append an auditable event.
"""
import os, json, math, time, collections
from skg.telemetry_bus import read as t_read, upsert as t_upsert
from skg.governance import append_event
from skg.physics_field import compose_information_energy
# graceful fallbacks if optional modules are absent
try:
    from skg.physics import gravity_score
except Exception:
    def gravity_score(tele, phase="Unified"): return 0.0

PEARLS = "/var/lib/skg/memory/pearls.jsonl"
AUDIT  = "/var/lib/skg/memory/governance.audit.jsonl"
PHASEF = "/var/lib/skg/memory/phase.current"
ADAPT  = "/var/lib/skg/memory/adaptive.state.json"

def _read_jsonl(path, max_lines=2000):
    if not os.path.exists(path): return []
    out=[]
    with open(path) as f:
        for line in f:
            if not line.strip(): continue
            out.append(json.loads(line))
    return out[-max_lines:]

def _avg_entropy(pearls):
    if not pearls: return 0.0
    vals=[p.get("entropy",0.0) for p in pearls if isinstance(p, dict)]
    return sum(vals)/len(vals) if vals else 0.0

def _anchor_coverage(pearls):
    if not pearls: return 0.0
    ok=0
    for p in pearls:
        anc=p.get("anchors",[])
        if isinstance(anc, list) and len(anc)>0: ok+=1
    return ok/len(pearls)

def _actor_evenness(audit):
    """
    Shannon evenness over actor distribution in governance.
    Evenness = H / Hmax ; H = -Σ p_i log p_i
    """
    if not audit: return 0.0
    cnt=collections.Counter([e.get("actor","?") for e in audit if isinstance(e,dict)])
    total=sum(cnt.values()) or 1
    ps=[c/total for c in cnt.values()]
    H = -sum(p*math.log(p+1e-12, 2) for p in ps)
    Hmax = math.log(len(ps)+1e-12, 2)
    return (H / Hmax) if Hmax>0 else 0.0

def _current_phase():
    try:
        return open(PHASEF).read().strip() or "Unified"
    except Exception:
        return "Unified"

def _adapt_state():
    try:
        return json.load(open(ADAPT))
    except Exception:
        return {"lfo_amp":0.55,"lfo_freq":0.0025,"entropy_avg":0.0}

def compute_equilibrium():
    pearls=_read_jsonl(PEARLS, 2000)
    audit =_read_jsonl(AUDIT , 2000)
    phase=_current_phase()
    adapt=_adapt_state()
    tele  =t_read()
    tele_core = tele.get("expressor", {})
    amp = float(adapt.get("lfo_amp", tele_core.get("amp", 0.55)))
    freq= float(adapt.get("lfo_freq", tele_core.get("freq",0.0025)))
    # gravity proxy from last-known telemetry snapshot
    last_tele = tele.get("last_telemetry", tele_core)
    grav = gravity_score({
        "cpu":          float(last_tele.get("cpu", 0.0) or 0.0),
        "port_variance":int(last_tele.get("port_variance", 0) or 0),
        "exfil":        bool(last_tele.get("exfil", False)),
    }, phase=phase)

    entropy_bal = _avg_entropy(pearls)                # 0..~1.6 normal range for 3 scenarios
    entropy_norm= min(1.0, entropy_bal / 1.6)         # normalize to [0..1]
    anchors     = _anchor_coverage(pearls)            # 0..1
    evenness    = _actor_evenness(audit)              # 0..1
    field_e     = compose_information_energy(amp,freq,grav,phase)  # 0..1

    # truth/equilibrium index = balanced blend
    eq = 0.30*entropy_norm + 0.25*evenness + 0.25*anchors + 0.20*field_e
    eq = max(0.0, min(1.0, eq))

    result = {
        "ts": time.time(),
        "phase": phase,
        "indices": {
            "entropy_norm": round(entropy_norm,4),
            "evenness":     round(evenness,4),
            "anchors":      round(anchors,4),
            "field_energy": round(field_e,4),
            "equilibrium":  round(eq,4),
        },
        "amp": amp, "freq": freq,
    }
    return result

def reflect_once():
    res = compute_equilibrium()
    # publish to telemetry.ethics and emit audit event
    t_upsert("ethics", res["indices"])
    append_event({
        "actor":"ethics.equilibrium",
        "type":"reflection",
        "phase":res["phase"],
        **res["indices"]
    })
    return res
