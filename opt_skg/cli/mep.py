#!/usr/bin/env python3
import json, sys
from skg.energy import choose
actions = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else [
  {"name":"local","ethics_cost":0.06,"entropy":0.12,"latency_ms":40},
  {"name":"peer","ethics_cost":0.05,"entropy":0.11,"latency_ms":120}
]
best,score=choose(actions)
print(json.dumps({"best":best,"score":round(score,3)}, indent=2))
