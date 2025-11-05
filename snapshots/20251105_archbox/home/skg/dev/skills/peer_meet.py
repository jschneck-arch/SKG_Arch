#!/usr/bin/env python3
from skg.peer import meet
from skg.ethics import check
def run(**params):
    src = params.get("source")
    if not src: return {"ok":False,"error":"source required (file path or https://...)"}
    check("peer","meet")                   # read-only behavior, consent is implicit via operator-provided src
    return {"ok":True,"understanding": meet(src)}
