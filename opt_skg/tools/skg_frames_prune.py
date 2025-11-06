#!/usr/bin/env python3
import time, shutil
from pathlib import Path

ROOT = Path("/opt/skg/telemetry/frames")
RETAIN_DAYS = 7

def main():
    if not ROOT.exists():
        return
    now = time.time()
    for daydir in ROOT.iterdir():
        if not daydir.is_dir():
            continue
        # delete directories older than RETAIN_DAYS
        try:
            # parse YYYYMMDD
            t = time.strptime(daydir.name, "%Y%m%d")
            age_days = (now - time.mktime(t)) / 86400.0
            if age_days > RETAIN_DAYS:
                shutil.rmtree(daydir, ignore_errors=True)
        except Exception:
            continue

if __name__ == "__main__":
    main()
