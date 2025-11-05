#!/usr/bin/env python3
"""
Skill: heal_verify_skill
Triggered after AutoHeal drift or repair detection.
Performs quick integrity and import verification.
"""
import os, json, subprocess, time
from skg.governance import append_event

LOG = "/var/lib/skg/memory/heal_verify.log"
CHECK_PATHS = [
    "/opt/skg/skg/physics.py",
    "/opt/skg/skg/predict.py",
    "/opt/skg/skg/autoheal.py",
    "/opt/skg/run_skg.py"
]

def verify_python_imports():
    try:
        out = subprocess.run(
            ["/opt/skg/.venv/bin/python", "-c", "import skg; import skg.predict; import skg.physics"],
            capture_output=True, text=True, timeout=10
        )
        return out.returncode == 0, out.stderr.strip()
    except Exception as e:
        return False, str(e)

def verify_files():
    missing = [p for p in CHECK_PATHS if not os.path.exists(p)]
    return len(missing) == 0, missing

def run_skill(payload=None):
    t0 = time.time()
    results = {}

    ok_imports, err = verify_python_imports()
    ok_files, missing = verify_files()

    results["imports_ok"] = ok_imports
    results["import_error"] = err
    results["files_ok"] = ok_files
    results["missing"] = missing
    results["timestamp"] = time.time()
    results["status"] = "ok" if (ok_imports and ok_files) else "fail"

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(results) + "\n")

    append_event({
        "actor": "heal_verify_skill",
        "type": "verification",
        "imports_ok": ok_imports,
        "files_ok": ok_files,
        "missing": missing,
        "status": results["status"]
    })

    return results

if __name__ == "__main__":
    print(json.dumps(run_skill(), indent=2))
