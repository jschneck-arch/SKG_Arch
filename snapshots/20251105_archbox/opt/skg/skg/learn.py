import json, time, sys
from pathlib import Path
from skg.governance import append_event
from skg.learn_vault import append as vault_append
def reflect_module(path):
    p=Path(path)
    if not p.exists():
        e={"error":"not_found","file":str(p)}
        append_event({"actor":"learn","type":"reflection","error":"not_found","file":str(p)}); return e
    head="".join(p.open(errors="ignore").readlines()[:30])
    rec={"actor":"learn","type":"reflection","file":str(p),"chars":len(head),"ts":time.time()}
    append_event(rec); vault_append(rec); return rec
def environment_snapshot():
    snap={"time":time.time(),"note":"system snapshot seed"}
    append_event({"actor":"learn","type":"env_snapshot"}); vault_append(snap); return snap
if __name__=="__main__":
    if len(sys.argv)<2: print("usage: reflect_module <file>|environment_snapshot"); sys.exit(0)
    print(json.dumps(globals()[sys.argv[1]](*sys.argv[2:]),indent=2))
