#!/usr/bin/env python3
import sys, json
from skg.coder import propose_change, apply_change
if len(sys.argv)<2:
    print("usage: skg code propose|apply ..."); sys.exit(2)
cmd=sys.argv[1]
if cmd=="propose":
    desc=sys.argv[2]; file=sys.argv[3]
    print("Enter patch, end with Ctrl-D:")
    patch=sys.stdin.read()
    out=propose_change(desc,file,patch)
    print(json.dumps(out,indent=2))
elif cmd=="apply":
    file=sys.argv[2]
    patch=sys.stdin.read()
    res=apply_change(file,patch)
    print(json.dumps({"file":file,"result":res}))
