#!/usr/bin/env python3
import subprocess, json, time, os
from skg.governance import append_event
DEV="/home/skg/dev"; LIVE="/opt/skg"
def run(**params):
    t=time.time()
    # sync code and skills
    r1 = subprocess.run(["rsync","-a","--delete",f"{DEV}/",f"{LIVE}/"], capture_output=True, text=True)
    # ensure /opt/skg/skills is the dev skills (symlink or fresh rsync)
    if not os.path.islink("/opt/skg/skills"):
        subprocess.run(["rm","-rf","/opt/skg/skills"])
        subprocess.run(["ln","-s","/home/skg/dev/skills","/opt/skg/skills"])
    status="ok" if r1.returncode==0 else "error"
    out={"from":DEV,"to":LIVE,"status":status,"duration":round(time.time()-t,2),"stderr":r1.stderr[-200:]}
    append_event({"actor":"sync_skill","type":"deployment","status":status})
    return out
