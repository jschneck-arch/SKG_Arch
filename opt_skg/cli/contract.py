import sys, os; sys.path.insert(0, "/opt/skg")
#!/usr/bin/env python3
import json
from skg.ethics_contract import evaluate_contract
if __name__=="__main__":
    print(json.dumps(evaluate_contract(), indent=2))
