import sys, os; sys.path.insert(0, "/opt/skg")
#!/usr/bin/env python3
import json
from skg.meta_context import synthesize
print(json.dumps(synthesize(), indent=2))
