import os, json, time
VAULT="/var/lib/skg/memory/learn_vault.jsonl"
def append(e): os.makedirs(os.path.dirname(VAULT),exist_ok=True); e=dict(e); e.setdefault("ts",time.time()); open(VAULT,"a").write(json.dumps(e)+"\n")
def search(term): 
    if not os.path.exists(VAULT): return []
    return [json.loads(l) for l in open(VAULT) if term.lower() in l.lower()]
