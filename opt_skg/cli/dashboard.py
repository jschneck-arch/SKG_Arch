#!/usr/bin/env python3
"""
SKG ARCH Dashboard
Reads telemetry.json and renders a simple live dashboard.
Use:
  skg dashboard                 # live console output
  skg dashboard --write /path   # update text/HTML file for overlay
"""
import json, os, sys, time
from datetime import datetime
from pathlib import Path

TELEMETRY = Path("/var/lib/skg/state/telemetry.json")

def read_json():
    try:
        with open(TELEMETRY) as f:
            return json.load(f)
    except Exception:
        return {}

def render(data):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entropy = data.get("entropy")
    ethics  = data.get("ethics_coherence")
    cpu     = data.get("cpu_percent")
    mem     = data.get("mem_percent")
    phase   = data.get("phase","?")
    bar = lambda v: "█" * int((v or 0)/10) + " " * (10-int((v or 0)/10))
    out = (
f"""┌────────────────────────────────────────────┐
│   SKG ARCH — LIVE TELEMETRY DASHBOARD      │
│────────────────────────────────────────────│
│ Entropy:          {entropy:<5}  [{bar(entropy*10 if entropy else 0)}] │
│ Ethics Coherence: {ethics:<5}  [{bar(ethics*10 if ethics else 0)}] │
│ CPU Load:         {cpu:<5}%  [{bar(cpu/10 if cpu else 0)}] │
│ Memory:           {mem:<5}%  [{bar(mem/10 if mem else 0)}] │
│ Phase: {phase:<10} Updated: {t} │
└────────────────────────────────────────────┘"""
    )
    return out

def loop(outpath=None, interval=5):
    while True:
        data = read_json()
        text = render(data)
        if outpath:
            Path(outpath).parent.mkdir(parents=True, exist_ok=True)
            with open(outpath, "w") as f: f.write(text + "\n")
        else:
            os.system("clear"); print(text)
        time.sleep(interval)

if __name__ == "__main__":
    args = sys.argv[1:]
    outpath = None
    if "--write" in args:
        try: outpath = args[args.index("--write")+1]
        except IndexError: pass
    loop(outpath)
