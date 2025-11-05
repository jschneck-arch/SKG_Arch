#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
SKG Portable — Cognitive Growth Cycle
Reads reflection pearls and lightly adjusts configuration.
"""

import yaml, json, time
from datetime import datetime
from pathlib import Path
from skg.paths import SKG_MEMORY_DIR, SKG_CONFIG_DIR
from skg.state import append_pearl, log_journal

PEARLS_PATH = Path(SKG_MEMORY_DIR) / "pearls.jsonl"
CONFIG_PATH = Path(SKG_CONFIG_DIR) / "config.yml"

def load_recent_reflections(limit=20):
    reflections = []
    try:
        with PEARLS_PATH.open("r", encoding="utf-8") as f:
            for line in f.readlines()[-limit:]:
                item = json.loads(line)
                if item.get("type") == "reflection":
                    reflections.append(item)
    except Exception:
        pass
    return reflections

def suggest_adjustment(reflections):
    """Naïve heuristic: if reflection count high, slow heartbeat; if low, speed up."""
    count = len(reflections)
    if count == 0:
        return None
    avg_entries = sum(r["data"]["entry_count"] for r in reflections) / count
    if avg_entries > 100:
        return {"heartbeat_interval": 15}
    elif avg_entries < 30:
        return {"heartbeat_interval": 5}
    return None

def apply_adjustment(adjustment):
    if not adjustment:
        return None
    try:
        config = yaml.safe_load(CONFIG_PATH.read_text())
    except Exception:
        config = {}
    core = config.setdefault("core", {})
    core.update(adjustment)
    CONFIG_PATH.write_text(yaml.safe_dump(config, sort_keys=False))
    plan = {
        "timestamp": datetime.utcnow().isoformat(),
        "adjustment": adjustment,
        "message": f"Applied dynamic config change: {adjustment}"
    }
    append_pearl({"type": "growth", "data": plan})
    log_journal(plan["message"], kind="growth")
    return plan

def growth_cycle():
    refl = load_recent_reflections()
    adj = suggest_adjustment(refl)
    return apply_adjustment(adj)

if __name__ == "__main__":
    print(growth_cycle())
