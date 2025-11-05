#!/usr/bin/env python3
import json, os
from skg.governance import append_event
ALLOW="/opt/skg/tools/allowlist.json"
def run(**params):
    lst=params.get("bash",[])
    if not isinstance(lst,list): return {"ok":False,"error":"bash must be list"}
    cur=json.load(open(ALLOW)) if os.path.exists(ALLOW) else {"bash":[]}
    cur["bash"]=sorted(set(cur.get("bash",[]) + lst))
    json.dump(cur, open(ALLOW,"w"), indent=2)
    append_event({"actor":"allowlist","type":"update","count":len(cur['bash'])})
    return {"ok":True,"count":len(cur["bash"])}
