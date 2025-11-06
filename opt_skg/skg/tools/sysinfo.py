#!/usr/bin/env python3
import platform, time
try:
    import psutil
except Exception:
    psutil=None
def snapshot():
    data = {
        "ts": time.time(),
        "hostname": platform.node(),
        "kernel": platform.release(),
        "uptime": None,
        "cpu_percent": None,
        "mem_percent": None,
        "disk_percent": None,
    }
    if psutil:
        data["uptime"] = time.time() - psutil.boot_time()
        data["cpu_percent"] = psutil.cpu_percent(interval=0.2)
        data["mem_percent"] = psutil.virtual_memory().percent
        data["disk_percent"] = psutil.disk_usage("/").percent
    return data
