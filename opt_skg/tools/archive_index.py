#!/usr/bin/env python3
import os, json, gzip, time

BASE   = "/var/lib/skg/memory"
ARCH   = os.path.join(BASE, "compact")
INDEX  = os.path.join(BASE, "archive_index.json")

def _ls_archives():
    return sorted([os.path.join(ARCH,f) for f in os.listdir(ARCH) if f.endswith(".gz")])

def _first_last_ts(path):
    # read first & last JSON lines' ts without expanding entire file
    first = last = None
    with gzip.open(path, "rt", errors="ignore") as f:
        for line in f:
            if line.strip():
                try:
                    first = json.loads(line).get("ts", None)
                    break
                except: break
    # for tail, read blocks
    try:
        with gzip.open(path, "rb") as f:
            data = f.read()[-65536:]  # last 64KB window
        for line in data.decode("utf-8","ignore").splitlines()[::-1]:
            if line.strip():
                try:
                    last = json.loads(line).get("ts", None); break
                except: pass
    except: pass
    return first, last

def build_index():
    items=[]
    for gz in _ls_archives():
        try:
            first, last = _first_last_ts(gz)
            items.append({"file": os.path.basename(gz), "path": gz, "ts_range": [first, last]})
        except Exception as e:
            items.append({"file": os.path.basename(gz), "path": gz, "error": str(e)})
    snap={"ts": time.time(), "archives": items}
    json.dump(snap, open(INDEX,"w"), indent=2)
    return snap

def query(actor=None, t_min=None, t_max=None, limit=500):
    # scan live rolling logs first
    scanned = 0
    def _scan_file(path):
        nonlocal scanned
        out=[]
        if not os.path.exists(path): return out
        with open(path) as f:
            for line in f:
                if not line.strip(): continue
                try:
                    e=json.loads(line)
                    ts=e.get("ts",None)
                    if t_min and (ts is None or ts < t_min): continue
                    if t_max and (ts is None or ts > t_max): continue
                    if actor and e.get("actor")!=actor: continue
                    out.append(e); scanned+=1
                    if len(out)>=limit: break
                except: pass
        return out

    results = []
    # rolling files
    for name in ("governance.audit.jsonl","pearls.jsonl","learn_vault.jsonl"):
        results.extend(_scan_file(os.path.join(BASE, name)))
        if len(results)>=limit: return results[:limit]

    # archived files by index
    idx = json.load(open(INDEX)) if os.path.exists(INDEX) else {"archives":[]}
    for ent in idx.get("archives",[]):
        a0,a1 = ent.get("ts_range",[None,None])
        if t_min and a1 and a1 < t_min: continue
        if t_max and a0 and a0 > t_max: continue
        try:
            with gzip.open(ent["path"], "rt", errors="ignore") as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        e=json.loads(line)
                        ts=e.get("ts",None)
                        if t_min and (ts is None or ts < t_min): continue
                        if t_max and (ts is None or ts > t_max): continue
                        if actor and e.get("actor")!=actor: continue
                        results.append(e)
                        if len(results)>=limit: return results[:limit]
                    except: pass
        except: pass
    return results[:limit]

if __name__=="__main__":
    import sys, json
    if len(sys.argv)>1 and sys.argv[1]=="build":
        print(json.dumps(build_index(), indent=2))
    else:
        print(json.dumps({"usage":"archive_index.py build | (used by skills)"}))
