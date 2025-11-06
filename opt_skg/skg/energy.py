#!/usr/bin/env python3
"""
Energy model: MEP (Minimum Energy Path) + XRP (cross-resonance phase alignment)
- MEP chooses lowest-cost action based on ethics/entropy/latency
- XRP computes phase alignment score between two nodes' LFO phases
"""
import math, time

def mep_score(ethics_cost:float, entropy:float, latency_ms:float,
              alpha=1.0, beta=0.7, gamma=0.2) -> float:
    # lower is better; keep units normalized 0..1 where possible
    l = min(1.0, latency_ms/1000.0)
    return alpha*ethics_cost + beta*entropy + gamma*l

def choose(actions):
    """
    actions: list of dicts with keys: name, ethics_cost, entropy, latency_ms
    returns best action dict + score
    """
    best=None; s_best=None
    for a in actions:
        s = mep_score(a["ethics_cost"], a["entropy"], a["latency_ms"])
        if s_best is None or s < s_best: best,s_best=a,s
    return best, s_best

def xrp_alignment(phase_a:float, phase_b:float, delta=0.2) -> float:
    """Return alignment score 0..1; within delta radians counts as aligned peak."""
    d = abs((phase_a - phase_b + math.pi)%(2*math.pi)-math.pi)
    return max(0.0, 1.0 - (d/delta)) if d<=delta else 0.0

if __name__=="__main__":
    # quick demo
    acts=[{"name":"local","ethics_cost":0.05,"entropy":0.12,"latency_ms":40},
          {"name":"peer","ethics_cost":0.04,"entropy":0.1,"latency_ms":140}]
    print(choose(acts))
    print(xrp_alignment(0.1,0.15))
