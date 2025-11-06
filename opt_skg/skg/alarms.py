#!/usr/bin/env python3
"""
SKG Alarms: watches telemetry and issues audit events when thresholds break.
"""
import json, time, os
from pathlib import Path
from time import time as _now

STATE = Path("/var/lib/skg/state")
TEL = STATE / "telemetry.json"
ALARM = STATE / "alarms.jsonl"

THRESH = {
    "entropy_avg_5m": 0.25,
    "ethics_coherence": 0.7,
    "cpu_percent": 90
}

def log_alarm(key,val):
    event={"ts":_now(),"metric":key,"value":val,"level":"warn"}
    with open(ALARM,"a") as f: f.write(json.dumps(event)+"\n")

def check():
    try:
        with open(TEL) as f: t=json.load(f)
    except: return
    for k,th in THRESH.items():
        v=t.get(k)
        if v is not None and v>th and k.startswith("entropy"):
            log_alarm(k,v)
        if k=="ethics_coherence" and (v is not None and v<th):
            log_alarm(k,v)
        if k=="cpu_percent" and v>th:
            log_alarm(k,v)

def loop(interval=60):
    while True:
        check(); time.sleep(interval)

if __name__=="__main__":
    loop()
