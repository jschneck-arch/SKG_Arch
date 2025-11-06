import sys, os; sys.path.insert(0, "/opt/skg")
#!/usr/bin/env python3
import sys,json
from skg.reflection import recall
if len(sys.argv)<2:
    print("usage: skg reflect <keyword> [min_entropy]")
    sys.exit(2)
kw=sys.argv[1]; me=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
print(json.dumps(recall(kw,me),indent=2))
