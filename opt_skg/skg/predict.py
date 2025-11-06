import os, json, time, math
from skg.physics import gravity_score
from skg.governance import append_event

PEARLS="/var/lib/skg/memory/pearls.jsonl"
PHASEF="/var/lib/skg/memory/phase.current"

def _phase():
    try: return open(PHASEF).read().strip() or "Unified"
    except Exception: return "Unified"

def _log(p): os.makedirs(os.path.dirname(PEARLS),exist_ok=True); open(PEARLS,"a").write(json.dumps(p)+"\n")

def anticipatory_prediction(tele, phase=None):
    phase = phase or _phase()
    g=gravity_score(tele, phase)
    s_ben = max(0,min(1,0.7-0.3*tele.get("jitter",0)))
    s_scan= max(0,min(1,tele.get("port_variance",0)/300))
    s_ex  = max(0,min(1,0.2+0.6*(1 if tele.get('exfil') else 0)))
    scenarios=[
     {"label":"benign_spike",   "p":s_ben, "why":[f"cpu={tele.get('cpu')}","jitter={:.3f}".format(tele.get('jitter',0.0))]},
     {"label":"transient_scan","p":s_scan,"why":[f"port_variance={tele.get('port_variance')}"]},
     {"label":"exfil",         "p":s_ex,  "why":[f"exfil={bool(tele.get('exfil'))}"]}
    ]
    s=sum(x["p"] for x in scenarios) or 1
    for x in scenarios: x["p"]=round(x["p"]/s,3)
    ent=-sum(x["p"]*math.log(x["p"]+1e-12,2) for x in scenarios)
    pearl={"ts":time.time(),"type":"prediction.pearl","phase":phase,"gravity":round(g,3),
           "entropy":round(ent,4),"scenarios":scenarios,
           "anchors":[
             {"kind":"telemetry","keys":sorted(list(tele.keys())),"values":{k:tele[k] for k in tele}},
             {"kind":"phase","value":phase},
             {"kind":"gravity","value":round(g,3)}
           ]}
    _log(pearl)
    append_event({"actor":"predict","type":"pearl","phase":phase,"entropy":pearl["entropy"],"gravity":round(g,3)})
    return pearl
