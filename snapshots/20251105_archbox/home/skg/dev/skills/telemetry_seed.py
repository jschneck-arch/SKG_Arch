#!/usr/bin/env python3
import time, random
from skg.telemetry_bus import upsert
from skg.governance import append_event
def run(**params):
    tele=params.get("tele") or {
        "cpu": round(random.random(),3),
        "port_variance": int(random.random()*100),
        "exfil": False,
        "jitter": round(random.random()/10,3)
    }
    upsert("last_telemetry", tele)
    append_event({"actor":"telemetry.seed","type":"upsert","keys":list(tele.keys())})
    return {"ok":True,"tele":tele,"ts":time.time()}
