#!/usr/bin/env python3
import os, json, subprocess, time
from skg.governance import append_event
CHECK = [
  "/opt/skg/skg/physics.py",
  "/opt/skg/skg/predict.py",
  "/opt/skg/skg/autoheal.py",
  "/opt/skg/run_skg.py"
]
def verify_python():
    try:
        out = subprocess.run(
            ["/opt/skg/.venv/bin/python","-c","import skg; import skg.predict; import skg.physics"],
            capture_output=True, text=True, timeout=10
        )
        return out.returncode == 0, out.stderr.strip()
    except Exception as e:
        return False, str(e)
def verify_files():
    miss=[p for p in CHECK if not os.path.exists(p)]
    return len(miss)==0, miss
def run(**params):
    ok_imp, err = verify_python()
    ok_files, miss = verify_files()
    res={"imports_ok":ok_imp,"files_ok":ok_files,"missing":miss,"status":"ok" if (ok_imp and ok_files) else "fail","ts":time.time()}
    append_event({"actor":"heal_verify","type":"verification","imports_ok":ok_imp,"files_ok":ok_files,"missing":miss,"status":res["status"]})
    return res
