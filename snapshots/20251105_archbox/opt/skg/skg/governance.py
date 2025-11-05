import os, json, time
AUDIT = "/var/lib/skg/memory/governance.audit.jsonl"
def append_event(evt):
    os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
    evt = dict(evt); evt.setdefault("ts", time.time())
    with open(AUDIT,"a") as f: f.write(json.dumps(evt)+"\n")
    return evt
