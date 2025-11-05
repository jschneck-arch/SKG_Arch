#!/usr/bin/env python3
"""
SKG Auto-Heal Utility
Ensures sys.path consistency, fixes permissions, and reports indentation issues.
"""

import os, sys, subprocess, compileall
from pathlib import Path

ROOT = Path("/opt/skg")
HEADER_LINE = "import sys; sys.path.append('/opt/skg')"
AUTOPEP8 = Path("/opt/skg/.venv/bin/autopep8")

def ensure_path_header(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return False
    if any(HEADER_LINE in line for line in text):
        return False
    insert_at = 1 if text and text[0].startswith("#!") else 0
    text.insert(insert_at, HEADER_LINE)
    path.write_text("\n".join(text) + "\n", encoding="utf-8")
    return True

def fix_permissions():
    for p in ROOT.rglob("*"):
        try:
            if p.is_dir():
                p.chmod(0o755)
            elif p.suffix == ".py":
                p.chmod(0o644)
            elif p.name.endswith(".sh") or "bin" in p.parts:
                p.chmod(0o755)
        except Exception as e:
            print(f"[perm] Could not fix {p}: {e}")

def compile_check():
    print("[*] Checking for syntax/indentation issues...")
    bad = []
    for p in ROOT.rglob("*.py"):
        try:
            compile(p.read_text(encoding="utf-8"), str(p), 'exec')
        except (IndentationError, TabError) as e:
            print(f"[!] {p}: {e}")
            bad.append(p)
    if bad and AUTOPEP8.exists():
        print(f"Found {len(bad)} files with indentation problems.")
        ans = input("Auto-fix with autopep8? [y/N]: ").lower().startswith("y")
        if ans:
            for f in bad:
                subprocess.run([str(AUTOPEP8), "--in-place", str(f)], check=False)
    elif not bad:
        print("[+] No indentation issues detected.")

def main():
    print("=== SKG Auto-Heal ===")
    fixed = 0
    for p in ROOT.rglob("*.py"):
        if ensure_path_header(p):
            print(f"[+] Added sys.path fix -> {p}")
            fixed += 1
    print(f"[i] Path fix injected in {fixed} files.")
    fix_permissions()
    compile_check()
    print("Auto-Heal complete.")

if __name__ == "__main__":
    main()
