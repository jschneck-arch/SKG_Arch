#!/usr/bin/env python3
"""
sync_runtime.py — merges dev tree into runtime safely
"""
import os, shutil, filecmp, time
from pathlib import Path

DEV = Path("/home/skg/dev")
RUNTIME = Path("/opt/skg")
SYNCED_DIRS = ["skg", "skills", "tools"]

def sync(src, dst):
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            target.mkdir(exist_ok=True)
            sync(item, target)
        else:
            if not target.exists() or not filecmp.cmp(item, target, shallow=False):
                shutil.copy2(item, target)
                print(f"[+] synced {item.relative_to(DEV)}")

def main():
    print(f"[SKG Sync] {time.ctime()}")
    for d in SYNCED_DIRS:
        src = DEV / d
        dst = RUNTIME / d
        if src.exists():
            sync(src, dst)
    print("[done]")

if __name__ == "__main__":
    main()
