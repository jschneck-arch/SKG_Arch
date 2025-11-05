import os, json
from skg.reflection import recall
from skg.physics import LFO
from skg.governance import append_event
from skg.expressor import publish_adaptive
STATE="/var/lib/skg/memory/adaptive.state.json"
def _load(): return json.load(open(STATE)) if os.path.exists(STATE) else {"entropy_avg":0,"lfo_amp":0.55,"lfo_freq":0.0025}
def _save(s): os.makedirs(os.path.dirname(STATE),exist_ok=True); json.dump(s,open(STATE,"w"),indent=2)
def adapt_once():
    st=_load(); recalled=recall("prediction",0.3,12)
    ent=sum(r.get("entropy",0) for r in recalled)/len(recalled) if recalled else 0
    d=ent-st["entropy_avg"]; amp=max(0.3,min(1,st["lfo_amp"]+0.2*d)); freq=max(0.001,min(0.005,st["lfo_freq"]+0.0005*d))
    st.update(entropy_avg=round(ent,4),lfo_amp=round(amp,3),lfo_freq=round(freq,4))
    _save(st); publish_adaptive(st["entropy_avg"],st["lfo_amp"],st["lfo_freq"])
    append_event({"actor":"adaptive.loop","type":"reflection_feedback",**st,"samples":len(recalled)})
    return LFO(amp=st["lfo_amp"],freq=st["lfo_freq"])
