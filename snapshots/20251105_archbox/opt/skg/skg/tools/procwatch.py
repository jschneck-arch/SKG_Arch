#!/usr/bin/env python3
import time
try:
    import psutil
except Exception:
    psutil=None
def snapshot(limit=10):
    procs=[]
    if psutil:
        for p in psutil.process_iter(attrs=['name']):
            try: procs.append((p.pid, p.info.get('name')))
            except: pass
            if len(procs)>=limit: break
    return {"ts": time.time(), "processes": procs}
