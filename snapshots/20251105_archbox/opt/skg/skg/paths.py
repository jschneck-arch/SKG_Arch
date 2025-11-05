#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
SKG Portable — Path Definitions
Reads environment variables and provides consistent
directories for config, state, logs, and memory.
"""

import os
from pathlib import Path

# Base directories (fall back to defaults if not set)
SKG_HOME        = Path(os.getenv("SKG_HOME", "/opt/skg"))
SKG_CONFIG_DIR  = Path(os.getenv("SKG_CONFIG_DIR", "/etc/skg"))
SKG_STATE_DIR   = Path(os.getenv("SKG_STATE_DIR", "/var/lib/skg"))
SKG_LOG_DIR     = Path(os.getenv("SKG_LOG_DIR", "/var/log/skg"))
SKG_MEMORY_DIR  = Path(os.getenv("SKG_MEMORY_DIR", str(SKG_STATE_DIR / "memory")))

# Ensure directories exist
for d in (SKG_CONFIG_DIR, SKG_STATE_DIR, SKG_LOG_DIR, SKG_MEMORY_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Optional: expose as dict for quick iteration
ALL_PATHS = {
    "home": SKG_HOME,
    "config": SKG_CONFIG_DIR,
    "state": SKG_STATE_DIR,
    "log": SKG_LOG_DIR,
    "memory": SKG_MEMORY_DIR,
}

if __name__ == "__main__":
    # Debug output if run manually
    import json
    print(json.dumps({k: str(v) for k, v in ALL_PATHS.items()}, indent=2))
