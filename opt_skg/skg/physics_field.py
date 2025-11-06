#!/usr/bin/env python3
"""
physics_field: spherical waveform + forces for information-as-energy

We model information flow as a spherical wave:
  ψ(r,t) = A * sin(2π f t - k r + φ)
  k ~ 2π f / c  (take c=1 for normalized units)

Energy density ~ ψ^2; total "field energy" integrates over 4π r^2.
For presentability & speed, we use closed-form proxies:
  E_wave  ≈ A^2 * (1 + f)         # wave contribution
  E_phase ≈ |phase_bias|          # bias from current "phase" mode
  E_grav  ≈ g                     # gravity_score proxy from telemetry

We return normalized [0..1] indices to feed SKG telemetry & ethics.
"""
import math

PHASE_BIAS = {
    "Unified":       0.00,
    "Explore":       0.10,
    "Exploit":       0.06,
    "RealityAnchor": 0.12,
}

def spherical_wave_value(r, t, amp=0.5, freq=0.0025, phi=0.0):
    return amp * math.sin(2*math.pi*freq*t - (2*math.pi*freq)*r + phi)

def field_energy_proxy(amp: float, freq: float) -> float:
    # simple, monotone proxy for integrated ψ^2 over a sphere
    e = (amp*amp) * (1.0 + freq*1000.0)   # freq in Hz-scale proxy
    # normalize to [0..1] under sane ranges amp∈[0..1], freq∈[0..005]
    return max(0.0, min(1.0, e))

def phase_bias(phase: str) -> float:
    return PHASE_BIAS.get(phase, 0.0)

def compose_information_energy(amp: float, freq: float, grav: float, phase: str) -> float:
    """
    Compose the energy terms (wave + gravity + phase) into a normalized scalar.
    This is NOT 'power' in a physical sense; it is an *index* for ethics equilibrium.
    """
    e_wave  = field_energy_proxy(amp, freq)
    e_phase = phase_bias(phase)
    e_grav  = max(0.0, min(1.0, float(grav)))
    # weighted mix; emphasize wave, then gravity, then phase bias
    e = 0.6*e_wave + 0.3*e_grav + 0.1*e_phase
    return max(0.0, min(1.0, e))
