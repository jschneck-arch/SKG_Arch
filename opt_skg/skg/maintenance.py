#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
SKG Portable — Maintenance & Log Governance
Performs log pruning, pearl rotation, and sanity checks to prevent runaway storage use.
"""

import os, json, time
from pathlib import Path
from skg.paths import SKG_LOG_DIR, SKG_MEMORY_DIR, SKG_STATE_DIR
from skg.state import JOURNAL_PATH, PEARLS_PATH

MAX_LOG_SIZE_MB = 10          # rotate when log >10 MB
MAX_JOURNAL_ENTRIES = 1000    # keep last N entries
MAX_PEARLS = 2000             # keep last N pearls

def rotate_log():
    log_path = Path(SKG_LOG_DIR) / "skg.log"
    if log_path.exists() and log_path.stat().st_size > MAX_LOG_SIZE_MB * 1024 * 1024:
        ts = int(time.time())
        backup = log_path.with_suffix(f".log.{ts}")
        log_path.rename(backup)
        open(log_path, "w").close()
        return f"Rotated log → {backup.name}"
    return None

def prune_json_file(path: Path, limit: int):
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if isinstance(data, list) and len(data) > limit:
            data = data[-limit:]
            path.write_text(json.dumps(data, indent=2))
            return f"Pruned {path.name} to {limit} entries"
    except Exception as e:
        return f"Error pruning {path.name}: {e}"
    return None

def prune_pearl_file(limit=MAX_PEARLS):
    if not PEARLS_PATH.exists():
        return None
    with PEARLS_PATH.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) > limit:
        lines = lines[-limit:]
        PEARLS_PATH.write_text("".join(lines))
        return f"Pruned pearls to {limit} lines"
    return None

def run_maintenance():
    actions = []
    for fn in (rotate_log, 
               lambda: prune_json_file(JOURNAL_PATH, MAX_JOURNAL_ENTRIES),
               prune_pearl_file):
        res = fn()
        if res:
            actions.append(res)
    return actions

if __name__ == "__main__":
    print(run_maintenance())
