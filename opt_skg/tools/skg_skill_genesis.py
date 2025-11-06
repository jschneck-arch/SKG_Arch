#!/usr/bin/env python3
import os, json, time, re
from pathlib import Path

PEARLS = Path("/var/lib/skg/memory/pearls.jsonl")
SKILLS_DIR = Path("/opt/skg/skills")
QUEUE = Path("/var/lib/skg/memory/skill_queue.jsonl")

def tail_events(limit=1000):
    if not PEARLS.exists(): return []
    with PEARLS.open() as f: lines = f.readlines()[-limit:]
    return [json.loads(x) for x in lines if x.strip()]

def detect_need(events):
    need_counts = {}
    for e in events:
        text = json.dumps(e)
        m = re.search(r"\b(?:skill|need|missing)\s+([a-z_]+)", text)
        if m:
            k = m.group(1)
            need_counts[k] = need_counts.get(k, 0) + 1
    return sorted(need_counts.items(), key=lambda x: -x[1])

def draft_skill(name):
    template = f"""#!/usr/bin/env python3
def run(**kwargs):
    '''Auto-generated placeholder for {name}.'''
    q = kwargs.get('prompt') or kwargs.get('query')
    return {{'ok': True, 'result': f'{name} stub executed', 'input': q}}
"""
    path = SKILLS_DIR / f"{name}.py"
    if not path.exists():
        path.write_text(template)
        os.chown(path, os.getuid(), os.getgid())
        print(f"[genesis] drafted {path}")
        with QUEUE.open("a") as qf: qf.write(json.dumps({"ts":time.time(),"skill":name})+"\n")

def main():
    events = tail_events()
    for name, count in detect_need(events)[:3]:
        if count > 1:  # only repeated references
            draft_skill(name)

if __name__ == "__main__":
    main()
