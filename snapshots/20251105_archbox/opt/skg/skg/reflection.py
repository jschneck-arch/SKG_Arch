import os, json, re
PEARL="/var/lib/skg/memory/pearls.jsonl"
AUD="/var/lib/skg/memory/governance.audit.jsonl"
def _read(p): return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
def recall(keyword=None,min_entropy=0.0,top=10):
    items=_read(PEARL)+_read(AUD); out=[]
    for r in items:
        if keyword and keyword.lower() not in json.dumps(r).lower(): continue
        if r.get("entropy",0)<min_entropy: continue
        out.append(r)
    out.sort(key=lambda x:x.get("entropy",0),reverse=True)
    return out[:top]
