#!/usr/bin/env python3
"""
SKG Utility Helpers — safe file I/O, JSON ops, and entropy-safe logging.
"""

import json, os, time
from pathlib import Path

def safe_read_json(path: str | Path, fallback=None):
    """Read JSON safely, returning fallback on error."""
    try:
        p = Path(path)
        if not p.exists():
            return fallback
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback

def safe_write_json(path: str | Path, data):
    """Write JSON atomically to prevent partial writes."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(p)

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
