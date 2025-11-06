#!/usr/bin/env python3
"""
Epistemic Tensor: attaches reliability weights to any reflection/prediction.
Not morals; purely measurable confidence/alignment/redundancy.
"""
import time

DEFAULT_WEIGHTS = {"confidence":0.5, "redundancy":0.2, "alignment":0.3}

def score(source:str, model:str, evidence_count:int, alignment:float) -> dict:
    # toy heuristics; plug in your metrics later
    base_conf = 0.75 if model.startswith(("gpt","o","llama","phi","mistral")) else 0.6
    conf = min(0.99, max(0.0, base_conf - 0.05*(source=="external")))
    red  = min(0.99, 0.2 + 0.1*max(0,evidence_count))
    ali  = min(0.99, max(0.0, alignment))
    # normalized mixture
    s = DEFAULT_WEIGHTS["confidence"]*conf + DEFAULT_WEIGHTS["redundancy"]*red + DEFAULT_WEIGHTS["alignment"]*ali
    return {"source":source, "model":model, "confidence":round(conf,3), "redundancy":round(red,3),
            "alignment":round(ali,3), "score":round(s,3), "ts":time.time()}
