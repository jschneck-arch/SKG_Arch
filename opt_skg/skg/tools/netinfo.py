#!/usr/bin/env python3
import time, socket
try:
    import psutil
except Exception:
    psutil=None
def snapshot():
    data = {"ts": time.time(), "interfaces": [], "active": []}
    if not psutil: return data
    stats = psutil.net_if_stats()
    data["interfaces"] = list(psutil.net_if_addrs().keys())
    data["active"] = [n for n,s in stats.items() if s.isup]
    return data
