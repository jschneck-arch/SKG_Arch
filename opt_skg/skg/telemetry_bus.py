import os, json, time
PATH="/var/lib/skg/memory/telemetry.json"
def read():
    if os.path.exists(PATH):
        try: return json.load(open(PATH))
        except: return {}
    return {}
def write(d):
    os.makedirs(os.path.dirname(PATH),exist_ok=True)
    d.setdefault("_meta",{})["updated"]=time.time()
    json.dump(d,open(PATH,"w"),indent=2)
def upsert(ns,payload):
    t=read(); t.setdefault(ns,{})
    t[ns].update(payload); write(t); return t[ns]
