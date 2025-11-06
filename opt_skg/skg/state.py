#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
SKG Portable — State Management
Handles journal.json, sandbox.json, and pearl memory logging.
"""

import json, time
from pathlib import Path
from skg.paths import SKG_STATE_DIR, SKG_MEMORY_DIR, SKG_LOG_DIR

JOURNAL_PATH = Path(SKG_STATE_DIR) / "journal.json"
SANDBOX_PATH = Path(SKG_STATE_DIR) / "sandbox.json"
PEARLS_PATH  = Path(SKG_MEMORY_DIR) / "pearls.jsonl"

def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def append_pearl(entry: dict):
    PEARLS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry["timestamp"] = time.time()
    with PEARLS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def log_journal(message: str, kind="heartbeat"):
    journal = load_json(JOURNAL_PATH, [])
    entry = {
        "ts": time.time(),
        "kind": kind,
        "msg": message
    }
    journal.append(entry)
    save_json(JOURNAL_PATH, journal[-1000:])  # keep last 1000
    append_pearl(entry)

def update_sandbox(key, value):
    sandbox = load_json(SANDBOX_PATH, {})
    sandbox[key] = value
    sandbox["last_update"] = time.time()
    save_json(SANDBOX_PATH, sandbox)
