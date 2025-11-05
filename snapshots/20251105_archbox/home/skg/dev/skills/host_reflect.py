#!/usr/bin/env python3
import os, time, json
from skg.telemetry_bus import upsert
from skg.governance import append_event
def _cpu_percent():
    try:
        import psutil
        return psutil.cpu_percent(interval=0.2)
    except Exception:
        return None
def run(**params):
    metrics={
        "load": os.getloadavg() if hasattr(os, "getloadavg") else (0,0,0),
        "cpu": _cpu_percent(),
        "ts": time.time()
    }
    upsert("host_metrics",metrics)
    append_event({"actor":"host.reflect","type":"metrics","cpu":metrics["cpu"],"load":metrics["load"]})
    return {"ok":True,"metrics":metrics}
