#!/usr/bin/env python3
"""
Field Renderer (ASCII)
Displays SKG entropy/amplitude/frequency heartbeat from telemetry.json
"""
import json, os, time, math

PATH = "/var/lib/skg/memory/telemetry.json"

def load_state():
    if not os.path.exists(PATH):
        return {"expressor": {"entropy_avg": 0.0, "amp": 0.5, "freq": 0.0025}}
    try:
        return json.load(open(PATH))
    except Exception:
        return {"expressor": {"entropy_avg": 0.0, "amp": 0.5, "freq": 0.0025}}

def render_loop():
    print("SKG Field Renderer — Ctrl-C to stop\n")
    t0 = time.time()
    while True:
        s = load_state().get("expressor", {})
        amp = s.get("amp", 0.5)
        ent = s.get("entropy_avg", 0.0)
        freq = s.get("freq", 0.0025)
        # generate wave
        t = time.time() - t0
        val = math.sin(2 * math.pi * freq * t) * amp
        bar = int((val + 1) * 20)
        print(f"\rEntropy:{ent:0.3f}  Amp:{amp:0.3f}  Freq:{freq:0.4f}  |{'#'*bar}{' '*(40-bar)}|", end='', flush=True)
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        render_loop()
    except KeyboardInterrupt:
        print("\nExiting renderer.")
