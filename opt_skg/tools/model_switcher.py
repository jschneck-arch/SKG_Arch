#!/usr/bin/env python3
"""
SKG Model Switcher (Homeostasis Edition)
Maintains cognitive equilibrium: chooses best backend by availability + system load.
- Prefers local small models when load is low
- Shifts to OpenAI when allowed and local is too slow/heavy
- Falls back to internal reflection under high load or no connectivity
- Hysteresis + dwell + cooldown to avoid flapping
Audits to /var/log/skg/model_switch.log
"""

import os, json, time, requests
from pathlib import Path

try:
    import psutil
except Exception:
    psutil = None

ENV_FILE = Path("/etc/skg/env")
LOG_FILE = Path("/var/log/skg/model_switch.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

OLLAMA_DEFAULT = "http://127.0.0.1:11434"
CHECK_INTERVAL = 60            # check once per minute
COOLDOWN_SEC   = 180           # don't switch more often than every 3 min
DWELL_SEC      = 600           # try to stay on a chosen backend for at least 10 min

# Load thresholds (tune for your box)
HI_CPU = 85.0      # if above, consider downshifting
HI_MEM = 85.0
LO_CPU = 55.0      # if below, consider upshifting
LO_MEM = 65.0

PREF_SMALL = ("tiny", "mini", "phi3", "tinyllama", "llama3:8b", "gemma:2b")

def log(msg, obj=None):
    s = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}"
    if obj is not None:
        s += " " + json.dumps(obj, ensure_ascii=False)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(s + "\n")
    print(s)

def read_env():
    data = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
    return data

def write_env_patch(patch):
    env = read_env()
    env.update(patch)
    lines = [f"{k}={v}" for k, v in env.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n")

def restart_core():
    os.system("sudo systemctl daemon-reload && sudo systemctl restart skg-core-v4.service")

def sense():
    if not psutil:
        return {"cpu": 0.0, "mem": 0.0, "load1": 0.0}
    load1, _, _ = psutil.getloadavg()
    cpu = psutil.cpu_percent(interval=0.05)
    mem = psutil.virtual_memory().percent
    return {"cpu": float(cpu), "mem": float(mem), "load1": float(load1)}

def detect_ollama_models(endpoint):
    try:
        r = requests.get(f"{endpoint.rstrip('/')}/api/tags", timeout=2.5)
        if r.ok:
            j = r.json()
            return [m.get("name","") for m in j.get("models", []) if isinstance(m, dict)]
    except Exception:
        pass
    return []

def detect_openai(api_key):
    if not api_key:
        return False
    try:
        r = requests.get("https://api.openai.com/v1/models",
                         headers={"Authorization": f"Bearer {api_key}"}, timeout=3)
        return r.ok
    except Exception:
        return False

def pick_smallest(models):
    if not models:
        return None
    # prefer “small” names; else first available
    for m in models:
        low = m.lower()
        if any(tag in low for tag in PREF_SMALL):
            return m
    return models[0]

def should_downshift(s):
    return (s["cpu"] >= HI_CPU) or (s["mem"] >= HI_MEM)

def should_upshift(s):
    return (s["cpu"] <= LO_CPU) and (s["mem"] <= LO_MEM)

def main():
    log("🧠 Model Switcher (homeostasis) started.")
    last_switch_ts = 0
    last_backend = None

    while True:
        try:
            env = read_env()
            endpoint = env.get("LLM_ENDPOINT", OLLAMA_DEFAULT)
            current_model = env.get("LLM_MODEL", "")
            openai_key = env.get("OPENAI_API_KEY","")
            s = sense()
            now = time.time()

            # Availability
            local_models = detect_ollama_models(endpoint) if endpoint else []
            have_openai  = detect_openai(openai_key)

            # Decide target backend
            target = {"LLM_MODEL": current_model, "LLM_ENDPOINT": env.get("LLM_ENDPOINT","")}
            backend = "keep"

            # If high load → prefer internal reflection (lowest energy)
            if should_downshift(s):
                if env.get("LLM_ENDPOINT") != "" or current_model != "internal":
                    target = {"LLM_MODEL":"internal", "LLM_ENDPOINT": ""}
                    backend = "internal"
            else:
                # load is not high; if very low and local has small model → choose local
                if local_models and should_upshift(s):
                    small = pick_smallest(local_models)
                    if small and (small != current_model or endpoint != OLLAMA_DEFAULT):
                        target = {"LLM_MODEL": small, "LLM_ENDPOINT": OLLAMA_DEFAULT}
                        backend = "ollama"
                # else, if no local models but OpenAI allowed → use OpenAI
                elif not local_models and have_openai and env.get("LLM_ENDPOINT") != "openai":
                    target = {"LLM_MODEL":"gpt-4o-mini", "LLM_ENDPOINT":"openai"}
                    backend = "openai"

            # Hysteresis: enforce dwell & cooldown unless we’re forced to drop to internal
            dwell_ok = (now - last_switch_ts) >= DWELL_SEC
            cooldown_ok = (now - last_switch_ts) >= COOLDOWN_SEC
            forced = (backend == "internal" and should_downshift(s))

            target_tuple = (target["LLM_MODEL"], target["LLM_ENDPOINT"])
            current_tuple = (current_model, env.get("LLM_ENDPOINT",""))

            if target_tuple != current_tuple:
                if forced or (dwell_ok and cooldown_ok):
                    write_env_patch(target)
                    restart_core()
                    last_switch_ts = now
                    last_backend = backend
                    log("switch", {"backend": backend, "target": target, "sense": s})
                else:
                    log("defer_switch", {"wanted": target, "since_last": now-last_switch_ts, "sense": s})
            else:
                log("steady", {"backend": last_backend or "current", "model": current_model, "sense": s})

        except Exception as e:
            log("error", {"error": str(e)})
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
