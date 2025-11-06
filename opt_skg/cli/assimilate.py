import sys, os; sys.path.insert(0, "/opt/skg")
#!/usr/bin/env python3
import json, time, pathlib
from skg.tools import auto_assimilator as aa  # will import via PYTHONPATH if present

# run one pass
for d in aa.discover():
    aa.audit("manual_scan", d.name)
print(json.dumps({"ok":True,"candidates":[p.name for p in aa.discover()],"ts":time.time()}, indent=2))
