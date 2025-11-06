#!/usr/bin/env python3
import tarfile, time, os
from pathlib import Path
SNAP_DIR = Path("/var/lib/skg/snapshots")
STATE_DIR = Path("/var/lib/skg/state")

SNAP_DIR.mkdir(parents=True,exist_ok=True)
stamp=time.strftime("%Y%m%d-%H%M%S")
tarname=SNAP_DIR/f"snapshot-{stamp}.tar.gz"
with tarfile.open(tarname,"w:gz") as tar:
    for f in STATE_DIR.glob("*"):
        tar.add(f,arcname=f.name)
print(f"Snapshot saved: {tarname}")
