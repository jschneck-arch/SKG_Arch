#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
SKG Portable — Configuration Loader
Reads /etc/skg/config.yml and exposes settings as Python dicts.
"""

import yaml
from pathlib import Path
from skg.paths import SKG_CONFIG_DIR

CONFIG_PATH = Path(SKG_CONFIG_DIR) / "config.yml"

def load_config():
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

CONFIG = load_config()

if __name__ == "__main__":
    import json
    print(json.dumps(CONFIG, indent=2))
