#!/usr/bin/env python3
"""
draft_create: SKG writes or expands a code idea into a draft file.
"""
import os, time
from skg.governance import append_event
BASE="/home/skg/dev/skg_drafts"
def run(**params):
    name=params.get("name","idea_"+str(int(time.time())))
    content=params.get("content","")
    path=os.path.join(BASE, name)
    with open(path,"w") as f: f.write(content)
    append_event({"actor":"skg.draft","type":"create","file":path})
    return {"ok":True,"file":path,"ts":time.time()}
