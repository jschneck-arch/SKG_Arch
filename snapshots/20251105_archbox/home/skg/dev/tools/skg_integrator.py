#!/usr/bin/env python3
"""
SKG Integrator - Core Equilibrium Monitor
Ensures the SKG substrate maintains stability and self-healing cycles.
"""

import os, time, json, psutil, subprocess, gzip
from pathlib import Path

LOG_PATH = Path("/var/log/skg/integrator.log")
TELEMETRY_PATH = Path("/var/lib/skg/memory/telemetry.json")
SERVICES = ["skg-core-v4", "skg-api", "skg-field"]
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB rotation

def log(msg):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")

def rotate_logs():
    if LOG_PATH.exists() and LOG_PATH.stat().st_size > MAX_LOG_SIZE:
        gz_path = LOG_PATH.with_suffix(".log.gz")
        with open(LOG_PATH, "rb") as src, gzip.open(gz_path, "wb") as dst:
            dst.writelines(src)
        LOG_PATH.unlink()
        log("[rotation] integrator log rotated")

def service_active(name):
    result = subprocess.run(["systemctl", "is-active", name], capture_output=True, text=True)
    return result.stdout.strip() == "active"

def restart_service(name):
    log(f"[heal] Restarting {name}")
    subprocess.run(["systemctl", "restart", name])

def check_services():
    for svc in SERVICES:
        if not service_active(svc):
            log(f"[alert] {svc} inactive")
            restart_service(svc)

def check_telemetry():
    if not TELEMETRY_PATH.exists():
        log("[warn] missing telemetry file")
        restart_service("skg-field")
        return
    try:
        data = json.loads(TELEMETRY_PATH.read_text())
        ts = data.get("ts", 0)
        if time.time() - ts > 180:
            log("[warn] telemetry stale; refreshing field")
            restart_service("skg-field")
    except Exception as e:
        log(f"[error] telemetry check failed: {e}")

def check_resources():
    usage = psutil.virtual_memory()
    if usage.percent > 90:
        log(f"[critical] memory pressure {usage.percent}% - throttling core")
        subprocess.run(["systemctl", "restart", "skg-core-v4"])

def main():
    log("[init] SKG Integrator starting up")
    while True:
        rotate_logs()
        check_services()
        check_telemetry()
        check_resources()
        time.sleep(60)

if __name__ == "__main__":
    main()
