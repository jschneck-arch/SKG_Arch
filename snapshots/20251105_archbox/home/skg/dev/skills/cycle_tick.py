#!/usr/bin/env python3
import time
from skg.telemetry_bus import upsert
from skg.governance import append_event
# local calls
from skills.telemetry_seed import run as seed
from skills.pearl_sampler import run as sample
from skg.ethics_equilibrium import reflect_once
from skg.ethics_contract import evaluate_contract

def run(**params):
    n = int(params.get("n", 3))
    # seed telemetry (random if none provided)
    s = seed()
    # sample n pearls with varied telemetry
    p = sample(n=n)
    # reflect & evaluate
    eq = reflect_once()
    ct = evaluate_contract()
    append_event({"actor":"cycle.tick","type":"completed",
                  "seeded":True,"samples":n,
                  "eq":eq["indices"]["equilibrium"],
                  "ct":ct["indices"]["contract"]})
    return {"ok":True, "seeded":True, "samples":n,
            "equilibrium": eq["indices"]["equilibrium"],
            "contract": ct["indices"]["contract"],
            "ts": time.time()}
