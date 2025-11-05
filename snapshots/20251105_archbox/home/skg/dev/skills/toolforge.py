#!/usr/bin/env python3
import os, time, json
from skg.governance import append_event
TOOLSHED="/home/skg/dev/toolshed"
MANIFEST=os.path.join(TOOLSHED,"manifest.json")
os.makedirs(TOOLSHED, exist_ok=True)
def _manifest():
    if os.path.exists(MANIFEST):
        try: return json.load(open(MANIFEST))
        except: pass
    return {"tools":[]}
def _save(m): json.dump(m, open(MANIFEST,"w"), indent=2)
def run(**params):
    name = params.get("name") or f"tool_{int(time.time())}"
    lang = params.get("lang","bash")
    body = params.get("content","")
    path = os.path.join(TOOLSHED, name + (".sh" if lang=="bash" else ".py" if lang=="python" else ".rs" if lang=="rust" else ".txt"))
    with open(path,"w") as f: f.write(body)
    if lang=="bash": os.chmod(path,0o755)
    m=_manifest(); m["tools"].append({"name":name,"lang":lang,"path":path,"ts":time.time()})
    _save(m)
    append_event({"actor":"toolforge","type":"create","name":name,"lang":lang,"path":path})
    return {"ok":True,"path":path,"lang":lang}
