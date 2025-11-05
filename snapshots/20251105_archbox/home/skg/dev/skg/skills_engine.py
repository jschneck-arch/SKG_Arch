#!/usr/bin/env python3
"""
Unified skills engine.
- Loads /opt/skg/skills/<name>.py
- Normalizes params so skills can just: def run(**params)
"""
import importlib.util, json
from pathlib import Path

SKILLS_DIR = Path("/opt/skg/skills")

def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if not spec or not spec.loader:
        raise FileNotFoundError(f"Cannot load: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def normalize_params(params: dict | None) -> dict:
    p = dict(params or {})
    # support top-level forms too: {"prompt": "..."} or {"query": "..."}
    # aliases collapse to "prompt"
    if "prompt" not in p:
        for k in ("query","text","input","q","message"):
            if k in p:
                p["prompt"] = p[k]
                break
    return p

def load_skill(name: str):
    path = SKILLS_DIR / f"{name}.py"
    if not path.exists():
        raise FileNotFoundError(f"Skill {name} not found: {path}")
    return _load_module(path)

def run_skill(name: str, **kwargs):
    mod = load_skill(name)
    params = normalize_params(kwargs.get("params", kwargs))
    if not hasattr(mod, "run"):
        raise AttributeError(f"Skill {name} has no run(**params)")
    return mod.run(**params)
