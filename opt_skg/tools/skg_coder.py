#!/usr/bin/env python3
"""
SKG Coder – Self-Evolving Sandbox
Observes and safely applies append-only code modifications for SKG.
"""

import os, time, json, subprocess, shutil
from pathlib import Path

WATCH_DIR = Path("/opt/skg")
PATCH_DIR = Path("/opt/skg/patches")
LOG_PATH  = Path("/var/log/skg/coder.log")

PATCH_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a") as f:
        f.write(f"[{ts}] {msg}\n")

def validate_code(code: str) -> bool:
    """Ensure code compiles and indentation is consistent."""
    try:
        compile(code, "<test>", "exec")
        lines = code.splitlines()
        for line in lines:
            if "\t" in line:
                raise ValueError("Tabs not allowed")
        return True
    except Exception as e:
        log(f"[reject] invalid code: {e}")
        return False

def propose_change(target: str, patch: str, proposer="skg") -> Path:
    """Propose a change (append-only)"""
    ts = time.strftime("%Y%m%d_%H%M%S")
    patch_file = PATCH_DIR / f"{Path(target).stem}_patch_{ts}.py"
    if not validate_code(patch):
        return None
    patch_file.write_text(patch)
    log(f"[proposal] {proposer} proposed patch for {target}: {patch_file}")
    return patch_file

def apply_patch(target: str, patch_path: Path):
    """Append verified patch to target safely."""
    try:
        with open(target, "a") as tgt, open(patch_path) as src:
            tgt.write("\n\n# === Applied Patch ===\n")
            tgt.write(src.read())
        log(f"[apply] patch {patch_path} -> {target}")
    except Exception as e:
        log(f"[error] applying patch {patch_path}: {e}")

def main_loop():
    log("[init] SKG Coder starting")
    while True:
        # Detect patch proposals by human or SKG itself
        for patch in PATCH_DIR.glob("*.py"):
            if patch.stat().st_mtime < time.time() - 10:  # stable file
                tgt_hint = patch.stem.split("_patch_")[0]
                candidates = list(WATCH_DIR.rglob(f"{tgt_hint}.py"))
                if candidates:
                    apply_patch(str(candidates[0]), patch)
                    patch.unlink()
        time.sleep(60)

if __name__ == "__main__":
    main_loop()
