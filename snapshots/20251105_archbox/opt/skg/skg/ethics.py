#!/usr/bin/env python3
"""
Ethics as telemetry + reflection + audit.
We do not gate by names; we gate by behavior class and consent.
All actions must log an event; sensitive classes require explicit consent flags.
"""
from skg.governance import append_event

# Behavior classes: read-only, adaptive, sensitive
POLICY = {
    "read_only": set(["predict","adaptive.loop","securitysense","research_analyst","learn","reflection"]),
    "adaptive":  set(["autoheal.observe","coder.propose","sync","skillforge"]),
    "sensitive": set(["autoheal.apply","coder.apply"])  # require consent
}

def check(actor: str, action: str, consent: bool=False):
    # Determine class by actor prefix or exact match
    cls = ("read_only" if actor in POLICY["read_only"] else
           "adaptive"  if actor in POLICY["adaptive"]  else
           "sensitive" if actor in POLICY["sensitive"] else "unknown")
    evt = {"actor":"ethics","type":"check","subject":actor,"action":action,"class":cls}
    if cls == "sensitive" and not consent:
        evt["decision"]="deny"
        append_event(evt)
        raise PermissionError(f"{actor}:{action} requires explicit consent")
    evt["decision"]="allow"
    append_event(evt)
    return True
