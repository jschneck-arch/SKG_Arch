#!/usr/bin/env python3
"""
Entropic Exchange Field: computes entropy delta per tick and a simple energy cost proxy.
Ethics here = maintaining bounded entropy and sustainable energy use.
"""
import time

class Exchange:
    def __init__(self):
        self.prev = {"t": None, "entropy": None, "cpu": None}

    def step(self, entropy: float, cpu_load: float) -> dict:
        now = time.time()
        prev_t = self.prev["t"]
        dH = None; dE = None
        if self.prev["entropy"] is not None and prev_t is not None:
            dt = max(1e-6, now - prev_t)
            dH = (entropy - self.prev["entropy"]) / dt
            dE = cpu_load * (abs(dH) if dH is not None else 0.0)
        self.prev.update({"t":now,"entropy":entropy,"cpu":cpu_load})
        return {"ts": now, "entropy": entropy, "cpu": cpu_load,
                "entropy_delta_per_s": None if dH is None else round(dH,6),
                "energy_cost_proxy": None if dE is None else round(dE,6)}
