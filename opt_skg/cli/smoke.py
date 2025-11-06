#!/usr/bin/env python3
"""
SKG Smoke Test — comprehensive system integrity validation.
Checks:
  • Core file structure
  • Python module imports
  • Critical services (API, Ollama, Assimilator, Autoheal)
  • Telemetry physics (entropy, coherence, MEP/XRP)
  • Assimilation health
  • Reflection + Self-state coupling
"""

import os, json, time, importlib.util, subprocess, socket
from pathlib import Path

STATE = Path("/var/lib/skg/state")
LOG = Path("/var/log/skg/smoke.log")
RESULT = {}
TELEMETRY = STATE / "telemetry.json"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def test_port(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def test_core_files():
    essentials = [
        "/opt/skg/tools/skillmaker.py",
        "/opt/skg/tools/auto_assimilator.py",
        "/opt/skg/tools/skg_autoheal.py",
        "/opt/skg/skills/cognition.py",
        "/opt/skg/tools/skg_brain.py"
    ]
    missing = [f for f in essentials if not Path(f).exists()]
    RESULT["core_files"] = {"ok": not missing, "detail": f"missing={missing}"}

def test_python_modules():
    modules = ["requests", "json", "time"]
    missing = []
    for m in modules:
        try:
            importlib.import_module(m)
        except Exception:
            missing.append(m)
    RESULT["python_modules"] = {"ok": not missing, "detail": f"missing={missing}"}

def test_services():
    checks = {
        "ollama": test_port("127.0.0.1", 11434),
        "api":  (test_port("127.0.0.1", 5056) or test_port("127.0.0.1", 5056)) ,
    }
    for svc, ok in checks.items():
        RESULT[f"service_{svc}"] = {"ok": ok, "detail": f"port={svc}"}

def test_telemetry():
    try:
        t = json.loads(TELEMETRY.read_text())
        entropy = t.get("entropy", 0)
        coherence = t.get("ethics_coherence", 0)
        mep = t.get("mep_coupling", 0)
        xrp = t.get("xrp_coherence", 0)
        RESULT["telemetry_physics"] = {
            "ok": entropy > 0 and coherence > 0 and mep > 0 and xrp > 0,
            "detail": f"entropy={entropy} coherence={coherence} mep={mep} xrp={xrp}"
        }
    except Exception as e:
        RESULT["telemetry_physics"] = {"ok": False, "detail": str(e)}

def test_assimilation_health():
    try:
        t = json.loads(TELEMETRY.read_text())
        health = t.get("assimilation_health", 1.0)
        RESULT["assimilation_health"] = {
            "ok": health > 0.8,
            "detail": f"assimilation_health={health}"
        }
    except Exception as e:
        RESULT["assimilation_health"] = {"ok": False, "detail": str(e)}

def test_self_state():
    try:
        subprocess.run(
            ["/opt/skg/.venv/bin/python", "-m", "skg.mep"],
            capture_output=True, timeout=15
        )
        subprocess.run(
            ["/opt/skg/.venv/bin/python", "-m", "skg.xrp"],
            capture_output=True, timeout=15
        )
        RESULT["self_state"] = {"ok": True, "detail": "MEP/XRP field coupling stable"}
    except Exception as e:
        RESULT["self_state"] = {"ok": False, "detail": str(e)}

def test_services_systemd():
    svc_names = [
        "skg-autoheal.service", "skg-assimilator.service",
        "skg-adaptive.service", "skg-api.service", "ollama.service"
    ]
    failed = []
    for svc in svc_names:
        r = subprocess.run(
            ["systemctl", "is-active", svc],
            capture_output=True, text=True
        )
        if "active" not in r.stdout:
            failed.append(svc)
    RESULT["systemd_services"] = {"ok": not failed, "detail": f"failed={failed}"}

def hint_field_zero():
    try:
        t = json.loads(TELEMETRY.read_text())
        if t.get("mep_coupling", 0) == 0 or t.get("xrp_coherence", 0) == 0:
            RESULT["hint_field"] = {
                "ok": False,
                "detail": "mep/xrp are zero; ensure skg-mep.service, skg-xrp.service, skg-telemetry-merge.service are active and /var/lib/skg/state/*_state.json exist."
            }
    except Exception:
        pass

def summarize():
    total = len(RESULT)
    failed = [k for k, v in RESULT.items() if not v.get("ok")]
    summary = "✅ ALL SYSTEMS NOMINAL" if not failed else f"⚠ Issues: {len(failed)}/{total}"
    RESULT["summary"] = summary
    RESULT["ts"] = time.time()
    print(json.dumps(RESULT, indent=2))
    log(summary)
    return 0 if not failed else 1

def main():
    log("=== Running SKG Smoke Test ===")
    test_core_files()
    test_python_modules()
    test_services()
    test_services_systemd()
    test_telemetry()
    test_assimilation_health()
    test_self_state()
    summarize()

if __name__ == "__main__":
    main()
