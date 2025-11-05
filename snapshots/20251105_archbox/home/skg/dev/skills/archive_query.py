#!/usr/bin/env python3
import time
from skg.governance import append_event
from importlib import import_module
def run(**params):
    actor = params.get("actor")
    tmin  = params.get("t_min")
    tmax  = params.get("t_max")
    limit = int(params.get("limit", 200))
    ai = import_module("tools.archive_index")
    out = ai.query(actor=actor, t_min=tmin, t_max=tmax, limit=limit)
    append_event({"actor":"archive.query","type":"scan","count":len(out),"actor_filter":actor})
    return {"ok":True,"count":len(out),"results":out}
