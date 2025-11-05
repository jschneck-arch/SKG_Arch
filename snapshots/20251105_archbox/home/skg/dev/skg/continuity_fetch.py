#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
import requests, time
from pathlib import Path

GITHUB_USER = "jschneck-arch"
REPO = "SKG_Portable"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO}/{BRANCH}"
LIST_URL = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents"
DEST_DIR = Path("/opt/skg/skg_docs")
DEST_DIR.mkdir(parents=True, exist_ok=True)

def list_remote_chat_files():
    r = requests.get(LIST_URL, timeout=15)
    if r.status_code != 200:
        return []
    return sorted([it["name"] for it in r.json()
                   if it["name"].startswith("chat_full_restore_") and it["name"].endswith(".txt")])

def fetch_new():
    existing = {p.name for p in DEST_DIR.glob("chat_full_restore_*.txt")}
    fetched = []
    for fname in list_remote_chat_files():
        if fname in existing: 
            continue
        url = f"{RAW_BASE}/{fname}"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            (DEST_DIR / fname).write_bytes(r.content)
            fetched.append(fname)
    return fetched

if __name__ == "__main__":
    print("Fetched:", fetch_new())
