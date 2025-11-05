#!/usr/bin/env python3
import json, time, platform
from skg.governance import append_event
def run(**params):
    snap={"host": platform.node(), "kernel": platform.release()}
    append_event({"actor":"env.sense","type":"snapshot","host":snap["host"],"kernel":snap["kernel"]})
    return {"ok":True,"snapshot":snap,"ts":time.time()}
