from skg.config.api_port import load
host, port = load()

#!/usr/bin/env python3
"""
SKG API — unified interface for skill invocation, telemetry, and cognition.
Runs under uvicorn on {host}:{port}
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
import json, time, os, importlib, traceback
from pathlib import Path

app = FastAPI(title="SKG API")

from pathlib import Path
SKILLS = Path("/home/skg/dev/skills")


STATE = Path("/var/lib/skg/state")
TELEMETRY = STATE / "telemetry.json"
SKILLS = Path("/home/skg/dev/skills")

class SkillRequest(BaseModel):
    params: dict | None = None

class AskRequest(BaseModel):
    text: str
    allow: list[str] | None = None

@app.get("/health")
def health():
    return {"ok": True, "ts": time.time()}

@app.get("/telemetry")
def get_telemetry():
    try:
        return json.loads(TELEMETRY.read_text())
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/skill/{name}")
def run_skill(name: str, req: SkillRequest):
    """Dynamically import and execute a skill file."""
    path = SKILLS / f"{name}.py"
    if not path.exists():
        return {"ok": False, "error": f"skill not found: {path}"}
    try:
        spec = importlib.util.spec_from_file_location(name, str(path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.run(**(req.params or {}))
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": traceback.format_exc()}

@app.post("/ask")
def ask(req: AskRequest):
    """
    High-level agent query. Dispatches to cognition or reflection internally.
    """
    try:
        from skg.skills.cognition import run as cognition_run
        response = cognition_run(prompt=req.text)
        return {"ok": True, "response": response}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/reflect")
def reflect(req: AskRequest):
    """
    Integrates field physics & recent audit data for meta reflection.
    """
    try:
        physics = json.loads(TELEMETRY.read_text())
        return {"ok": True, "physics": physics}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/update_field_strength")
def update_field_strength(data: dict):
    """
    API hook for physics loops to push updates into telemetry.json.
    """
    try:
        tele = json.loads(TELEMETRY.read_text()) if TELEMETRY.exists() else {}
        tele.update({"field_strength": data.get("field_strength", 0.0), "ts": time.time()})
        TELEMETRY.write_text(json.dumps(tele))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Response-Time"] = f"{(time.time()-start):.3f}s"
    return response

from pydantic import BaseModel

class AskRequest(BaseModel):
    text: str

@app.post("/ask")
def ask(req: AskRequest):
    # call the file /home/skg/dev/skills/skill_cognition.py
    import importlib.util, json, time
    path = SKILLS / "skill_cognition.py"
    if not path.exists():
        return {"ok": False, "error": f"missing: {path}"}
    try:
        spec = importlib.util.spec_from_file_location("skill_cognition", str(path))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        result = mod.run(prompt=req.text)
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}
