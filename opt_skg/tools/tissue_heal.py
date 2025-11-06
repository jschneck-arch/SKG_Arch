#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
import requests, json, time

def active(unit):
    return subprocess.run(["systemctl","is-active","--quiet",unit]).returncode==0

def restart(u): subprocess.run(["systemctl","restart",u])

# quick pings
def port_up(port):
    import socket
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1",port))==0

issues=[]

if not port_up(11434): issues.append(("ollama.service","port 11434 down"))
if not port_up(5055): issues.append(("skg-api.service","port 5055 down"))
if not active("skg-assimilator.service"): issues.append(("skg-assimilator.service","inactive"))
if not active("skg-autoheal.service"): issues.append(("skg-autoheal.service","inactive"))

# skillmaker heuristic: a skill file OR unit active
patch_dir=Path("/home/skg/.skg_overlay/patches"); patch_dir.mkdir(parents=True,exist_ok=True)
if not list(patch_dir.glob("*.py")) and not active("skg-skillmaker.service"):
    issues.append(("skg-skillmaker.service","no skills + inactive"))

for unit, why in issues:
    restart(unit)

print(json.dumps({"ts":time.time(),"restarts":[u for u,_ in issues]}, indent=2))
