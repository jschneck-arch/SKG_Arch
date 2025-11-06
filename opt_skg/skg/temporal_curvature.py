#!/usr/bin/env python3
"""
Temporal Curvature: biases recency/anticipation without morals — regulates cadence by physics of time.
"""
import math, time

def bias(now=None, horizon_s=600, curve=1.3):
    """Return a 0..1 weight favoring near-term activity; curve>1 increases near-term pull."""
    if now is None: now = time.time()
    return lambda t: 1.0 / (1.0 + ((max(0.0, (now - t))/horizon_s) ** curve))

def anticipate(freq_hz=0.002, phase=0.0):
    """Predictive sinusoid 0..1 for anticipatory scheduling (ties to waveform/LFO)."""
    def f(now=None):
        if now is None: now=time.time()
        return (math.sin(2*math.pi*freq_hz*now + phase)+1)/2
    return f
