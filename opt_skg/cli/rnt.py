#!/usr/bin/env python3
import json, sys
from pathlib import Path
PEERS="/var/lib/skg/state/rnt_peers.json"
CONS = "/var/lib/skg/state/rnt_consensus.json"

cmd = sys.argv[1] if len(sys.argv)>1 else "status"
if cmd=="status":
    peers=json.load(open(PEERS)) if Path(PEERS).exists() else {"peers":{}}
    cons=json.load(open(CONS)) if Path(CONS).exists() else {}
    print(json.dumps({"peers":peers.get("peers",{}),"consensus":cons}, indent=2))
elif cmd=="peers":
    print(open(PEERS).read() if Path(PEERS).exists() else '{"peers":{}}')
else:
    print('usage: skg rnt {status|peers}')
