#!/usr/bin/env python3
import json
from skg.ethics_equilibrium import reflect_once
if __name__=="__main__":
    print(json.dumps(reflect_once(), indent=2))
