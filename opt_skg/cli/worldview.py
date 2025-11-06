import sys, os; sys.path.insert(0, "/opt/skg")
#!/usr/bin/env python3
import json
from skg.telemetry_bus import read
def bar(v,w=28):
    n=int(max(0,min(1.0,v))*w); return "█"*n+"."*(w-n)
if __name__=="__main__":
    t=read()
    e=t.get("ethics",{}); c=t.get("ethics_contract",{})
    print(f"EQ {e.get('equilibrium',0):.2f} |{bar(e.get('equilibrium',0))}|  ANCH:{e.get('anchors',0):.2f}  EVEN:{e.get('evenness',0):.2f}")
    print(f"CT {c.get('contract',0):.2f} |{bar(c.get('contract',0))}|  TR:{c.get('truth',0):.2f}  FR:{c.get('freedom',0):.2f}  NP:{c.get('non_oppression',0):.2f}")
