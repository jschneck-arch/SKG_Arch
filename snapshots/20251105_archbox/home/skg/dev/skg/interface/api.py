#!/usr/bin/env python3
import sys, json, time
sys.path.append("/opt/skg")
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from skg.skills_engine import run_skill

app = FastAPI()

class SkillRequest(BaseModel):
    params: dict | None = None

class ProposeRequest(BaseModel):
    target_hint: str
    patch_code: str
    proposer: str | None = "api"

@app.get("/state")
def state():
    p = Path("/var/lib/skg/memory/telemetry.json")
    d = json.loads(p.read_text()) if p.exists() else {}
    return {"ok": bool(d), "telemetry": d, "ts": time.time()}

@app.post("/skill/{name}")
def call_skill(name: str, req: SkillRequest):
    try:
        return {"ok": True, "result": run_skill(name, **(req.params or {}))}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/skill/propose")
def propose_patch(req: ProposeRequest):
    patch_dir = Path("/opt/skg/patches"); patch_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    pf = patch_dir / f"{req.target_hint}_patch_{ts}.py"
    try: compile(req.patch_code, "<proposal>", "exec")
    except Exception as e: raise HTTPException(status_code=400, detail=f"syntax_error: {e}")
    pf.write_text(req.patch_code)
    return {"ok": True, "patch": str(pf), "proposer": req.proposer}
