#!/usr/bin/env python3
import os, json, importlib.util, inspect, time, glob
from skg.governance import append_event

SKILLS_DIR="/opt/skg/skills"
OUT="/opt/skg/skill_manifest.json"

def has_run(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    if not spec or not spec.loader: return False
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return callable(getattr(mod,"run",None))
    except Exception:
        return False

def build():
    items=[]
    for p in sorted(glob.glob(os.path.join(SKILLS_DIR,"*.py"))):
        name=os.path.splitext(os.path.basename(p))[0]
        items.append({"name":name, "path":p, "has_run": has_run(p)})
    out={"ts": time.time(), "skills": items}
    json.dump(out, open(OUT,"w"), indent=2)
    append_event({"actor":"tools.skill_manifest","type":"refresh","count":len(items)})
    return out

if __name__=="__main__":
    print(json.dumps(build(), indent=2))
