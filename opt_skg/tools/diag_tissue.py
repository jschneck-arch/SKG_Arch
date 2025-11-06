#!/usr/bin/env python3
import sys, os, json, time, socket
sys.path.insert(0, "/opt/skg")
from skg import utils

print("=== SKG Tissue Diagnostic ===\n")

results = {}

# Check Ollama
try:
    s = socket.create_connection(("127.0.0.1", 11434), 2)
    s.close()
    results["ollama_port"] = {"ok": True}
except Exception:
    results["ollama_port"] = {"ok": False}

# Check API
try:
    s = socket.create_connection(("127.0.0.1", 5055), 2)
    s.close()
    results["api_port"] = {"ok": True}
except Exception:
    results["api_port"] = {"ok": False}

# Check service state files
for name in ["cognition", "assimilator", "autoheal", "skillmaker"]:
    results[name] = {"ok": os.system(f"systemctl is-active --quiet skg-{name}.service")==0}

# Optional MEP/XRP readings
mep_state = utils.safe_read_json("/var/lib/skg/state/mep_state.json", {})
xrp_state = utils.safe_read_json("/var/lib/skg/state/xrp_state.json", {})

if mep_state:
    results["mep_field"] = {"ok": True, "detail": f"coupling={mep_state.get('coupling')}"}
else:
    results["mep_field"] = {"ok": False}

if xrp_state:
    results["xrp_resonance"] = {"ok": True, "detail": f"coherence={xrp_state.get('coherence')}"}
else:
    results["xrp_resonance"] = {"ok": False}

# Summary
all_ok = all(r["ok"] for r in results.values())
print("\nResults:")
for k,v in results.items():
    icon = "🟢" if v["ok"] else "🔴"
    print(f"  {k:15}: {icon}")
print(f"\nSummary: {'🟢 ALL SYSTEMS NOMINAL' if all_ok else '⚠ Issues detected'}")
print("Timestamp:", time.time())

# === Assimilation Health Diagnostic ===
try:
    from pathlib import Path
    assim_state = Path("/var/lib/skg/state/assimilation_state.json")
    health = 0.0
    detail = ""
    if assim_state.exists():
        data = json.loads(assim_state.read_text())
        results = data.get("results", {})
        total = len(results)
        failed = sum(1 for r in results.values() if not r.get("ok"))
        health = (total - failed) / total if total else 0.0
        detail = f"healthy={total - failed}/{total} ({health:.2%})"
    results["assimilation_health"] = {
        "ok": health > 0.8,
        "detail": detail
    }
except Exception as e:
    results["assimilation_health"] = {"ok": False, "detail": str(e)}
