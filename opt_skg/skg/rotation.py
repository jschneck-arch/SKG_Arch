#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
SKG Portable — Safe Gzip Rotation
Rotates large append-only JSONL or log files into timestamped .gz archives.
Never deletes; always append-only.
"""

import gzip, shutil, time
from pathlib import Path

def rotate_file(path: Path, max_mb: int = 20):
    if not path.exists():
        return None
    size_mb = path.stat().st_size / (1024*1024)
    if size_mb < max_mb:
        return None
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = path.with_suffix(path.suffix + f".{ts}.gz")
    with open(path, "rb") as src, gzip.open(dest, "wb", compresslevel=9) as dst:
        shutil.copyfileobj(src, dst)
    # truncate active file for continued appending
    open(path, "w").close()
    return f"Rotated {path.name} → {dest.name} ({size_mb:.1f} MB)"
