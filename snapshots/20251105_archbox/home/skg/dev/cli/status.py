#!/usr/bin/env python3
import os, json
PE="/var/lib/skg/memory/pearls.jsonl"
AU="/var/lib/skg/memory/governance.audit.jsonl"
VA="/var/lib/skg/memory/learn_vault.jsonl"
TE="/var/lib/skg/memory/telemetry.json"
def count(p): 
    try:
        with open(p) as f: return sum(1 for _ in f if _.strip())
    except: return 0
def read_json(p):
    try: return json.load(open(p))
    except: return {}
if __name__=="__main__":
    te=read_json(TE)
    e=te.get("ethics",{}); c=te.get("ethics_contract",{})
    print(f"pearls:{count(PE)}  audit:{count(AU)}  vault:{count(VA)}")
    print(f"equilibrium:{e.get('equilibrium',0):.3f}  anchors:{e.get('anchors',0):.3f}  evenness:{e.get('evenness',0):.3f}")
    print(f"contract:{c.get('contract',0):.3f}  truth:{c.get('truth',0):.3f}  non_opp:{c.get('non_oppression',0):.3f}")
