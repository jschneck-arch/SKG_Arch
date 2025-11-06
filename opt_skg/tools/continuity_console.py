from skg.config.api_port import load
host, port = load()

#!/usr/bin/env python3
"""
Continuity Console
------------------
A minimal command-line loop that lets a human observer
exchange text with the SKG substrate through the
/skill/conversation skill.  It simply transports data.
"""

import json, requests, readline, sys, time

API = "http://{host}:{port}/skill/conversation"

def main():
    print("SKG Continuity Console – type ':q' to quit\n")
    while True:
        try:
            prompt = input("⊙ ")
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if not prompt or prompt.strip() == ":q":
            break
        payload = {"prompt": prompt}
        try:
            r = requests.post(API, headers={"Content-Type": "application/json"}, json=payload, timeout=120)
            data = r.json()
        except Exception as e:
            data = {"ok": False, "error": str(e)}
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"\n[{ts}] substrate →")
        print(json.dumps(data, indent=2))
        print()
    print("Console closed.")

if __name__ == "__main__":
    main()
