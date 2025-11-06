#!/usr/bin/env python3
import sys
from pathlib import Path
if str(Path("/opt/skg")) not in sys.path:
    sys.path.insert(0, str(Path("/opt/skg")))

"""
SKG Core Daemon v4
Unified reflective architecture with continuity, autoheal, and self-reflection.
"""

import os, sys, time, json, logging, subprocess, traceback
from pathlib import Path

# === Path Bootstrapping ===
sys.path.append("/opt/skg")

from skg.paths import SKG_LOG_DIR
from skg.state import log_journal

LOG_PATH = Path(SKG_LOG_DIR) / "skg-core.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
logger = logging.getLogger("skg-core")

# === Parameters ===
HEARTBEAT_INTERVAL = 10          # seconds
REFLECTION_INTERVAL = 60         # seconds
MAINTENANCE_INTERVAL = 300       # seconds
AUTOHEAL_PATH = Path("/opt/skg/tools/skg_autoheal.py")

# === Subprocess helpers ===
def safe_run(cmd: list, label: str):
    try:
        start = time.time()
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=240)
        logger.info(f"[{label}] OK in {time.time() - start:.1f}s")
        return output
    except subprocess.CalledProcessError as e:
        logger.warning(f"[{label}] failed ({e.returncode}): {e.output.strip()[:200]}")
    except Exception as e:
        logger.warning(f"[{label}] exception: {e}")
    return None

# === Core reflection ===
def self_reflect():
    """Analyze recent continuity for thematic reflection."""
    idx_path = Path("/var/lib/skg/continuity_index.jsonl")
    if not idx_path.exists():
        logger.info("[reflect] No continuity index found.")
        return
    texts = []
    try:
        with idx_path.open("r", encoding="utf-8") as f:
            for line in f.readlines()[-500:]:
                try:
                    j = json.loads(line)
                    texts.append(j.get("text", "").lower())
                except Exception:
                    continue
    except Exception as e:
        logger.warning(f"[reflect] Read error: {e}")
        return
    corpus = " ".join(texts)
    themes = ["energy", "gravity", "phase", "sphere", "audit", "growth", "council", "reflection"]
    counts = {k: corpus.count(k) for k in themes}
    dominant = max(counts, key=counts.get, default="none")
    summary = {"dominant": dominant, "counts": counts}
    log_journal(f"[self_reflect] {json.dumps(summary)}")
    logger.info(f"[reflect] Dominant theme: {dominant}")
    return summary

# === Continuity ingestion ===
def ingest_continuity():
    logger.info("[continuity] Fetching + ingesting + indexing...")
    cmds = [
        ["/opt/skg/.venv/bin/python", "-m", "skg.continuity_fetch"],
        ["/opt/skg/.venv/bin/python", "-m", "skg.continuity"],
        ["/opt/skg/.venv/bin/python", "-m", "skg.continuity_index"],
    ]
    for c in cmds:
        safe_run(c, f"continuity:{c[-1]}")

# === Autoheal ===
def run_autoheal():
    if AUTOHEAL_PATH.exists():
        safe_run(["/opt/skg/.venv/bin/python", str(AUTOHEAL_PATH)], "autoheal")
    else:
        logger.info("[autoheal] Script not found, skipping.")

# === Main loop ===
def main():
    logger.info("🧠 SKG Core v4 starting up...")
    last_reflect = last_maint = last_continuity = 0
    counter = 0
    try:
        while True:
            now = time.time()
            logger.info(f"[heartbeat] Cycle {counter}")
            log_journal(f"[heartbeat] SKG alive cycle {counter}")
            counter += 1

            # reflection loop
            if now - last_reflect >= REFLECTION_INTERVAL:
                self_reflect()
                last_reflect = now

            # continuity ingestion
            if now - last_continuity >= (REFLECTION_INTERVAL * 3):
                ingest_continuity()
                last_continuity = now

            # maintenance / autoheal
            if now - last_maint >= MAINTENANCE_INTERVAL:
                run_autoheal()
                last_maint = now

            time.sleep(HEARTBEAT_INTERVAL)

    except KeyboardInterrupt:
        logger.info("🧠 SKG Core stopping (KeyboardInterrupt).")
    except Exception as e:
        logger.error(f"Exception in main loop: {e}")
        traceback.print_exc()
    finally:
        logger.info("🧠 SKG Core stopped cleanly.")
        log_journal("🧠 SKG Core stopped cleanly.")

if __name__ == "__main__":
    main()
# --- SKG physics + anticipatory prediction integration ---
from skg.physics import GravityFactors, gravity_score, LFO, Phase, can_transition, next_cadence_seconds
from skg.predict import anticipatory_prediction

LFO_REFLECT=LFO(amp=0.55,freq=0.0025,phi=0.0)

def scheduler_tick(state):
    base=60 if state.get("phase") in (Phase.KERNEL,Phase.UNIFIED) else 90
    next_reflect=next_cadence_seconds(base,LFO_REFLECT)
    state.setdefault("telemetry",{})["lfo"]={"amp":LFO_REFLECT.amp,"freq":LFO_REFLECT.freq,"phi":LFO_REFLECT.phi}
    state["telemetry"]["next_reflect_in_s"]=next_reflect
    return next_reflect

def reflect_cycle(state,memory,telemetry):
    now=time.time()
    for item in memory.get("candidates",[]):
        rec=max(0.0,1.0-(now-item.get("ts_s",now))/3600)
        ev=item.get("evidence_ratio",0.0)
        eth=item.get("ethics_cost",0.0)
        it=item.get("intent",0.0)
        item["g"]=gravity_score(GravityFactors(rec,ev,eth,it))
    memory["candidates"].sort(key=lambda x:x.get("g",0.0),reverse=True)
    pred=anticipatory_prediction(telemetry)
    return {"gravity_top":memory["candidates"][:3],"prediction":pred}
# --- Governance integration ---
from skg.governance import audit_prediction, audit_phase_change

def reflect_cycle(state, memory, telemetry):
    now=time.time()
    for item in memory.get("candidates",[]):
        rec=max(0.0,1.0-(now-item.get("ts_s",now))/3600)
        ev=item.get("evidence_ratio",0.0)
        eth=item.get("ethics_cost",0.0)
        it=item.get("intent",0.0)
        item["g"]=gravity_score(GravityFactors(rec,ev,eth,it))
    memory["candidates"].sort(key=lambda x:x.get("g",0.0),reverse=True)
    pred=anticipatory_prediction(telemetry)
    audit_prediction(pred)   # <-- new audit entry
    return {"gravity_top":memory["candidates"][:3],"prediction":pred}
# --- Reflection ↔ Anticipation integration ---
from skg.adaptive import adapt_from_reflection

def adaptive_tick(state):
    """Adjust waveform and telemetry based on reflection entropy."""
    lfo = adapt_from_reflection()
    state.setdefault("telemetry",{})["adaptive_lfo"]={"amp":lfo.amp,"freq":lfo.freq}
    return lfo
