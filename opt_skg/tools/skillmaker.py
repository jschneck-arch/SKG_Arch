import sys, os; sys.path.insert(0, "/opt/skg")
import sys, os; sys.path.insert(0, "/opt/skg")
#!/usr/bin/env python3
"""
SKG SkillMaker — Ollama-only, with QA hooks and audit.
Generates candidate skill code, validates it, and stages to overlay.
"""
import os, json, subprocess, time, tempfile, requests
from pathlib import Path
from skg.audit_coder import record as audit_coder

STATE  = Path("/var/lib/skg/state")
SKILLS = Path("/home/skg/.skg_overlay/patches")
CAPS   = STATE / "capabilities.jsonl"
MODEL  = os.environ.get("SKG_SKILL_MODEL","tinyllama:latest")

SYSTEM = (
 "You generate a single, safe Python file containing a function callable as `run(**kwargs)`.\n"
 "No network calls. No destructive operations. Use only stdlib.\n"
 "Return only the code block, nothing else."
)

def _run(cmd, timeout=12):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def _ollama(prompt:str, timeout=60):
    url = "http://127.0.0.1:11434/api/generate?stream=false"
    data = {"model": MODEL, "prompt": prompt}
    try:
        r = requests.post(url, json=data, timeout=timeout)
        j = r.json()
        return (j.get("response") or "").strip()
    except Exception as e:
        return f"# ollama_error: {e}"

def _static_ok(code:str)->(bool,str):
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as f:
        f.write(code); tmp=f.name
    # basic compile + simple bans
    bans = ["os.system(", "subprocess.Popen(", "exec(", "eval("]
    if any(b in code for b in bans):
        return False, "banned_call"
    rc, _, err = _run(f"python3 -m py_compile {tmp}")
    return (rc==0, "compiled" if rc==0 else f"compile_error: {err[:160]}")

def _runtime_ok(code:str)->(bool,str):
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td)/"candidate.py"; fp.write_text(code)
        rc, out, err = _run(f"python3 {fp}", timeout=8)
        if rc!=0 or "Traceback" in (out+err):
            return False, (out+err)[:200]
        return True, "ran"

def _record_cap(name:str, src:str, score:float, physics:dict):
    CAPS.parent.mkdir(parents=True, exist_ok=True)
    evt={"ts":time.time(),"name":name,"source":src,"score":score,"physics":physics}
    with open(CAPS,"a") as f: f.write(json.dumps(evt)+"\n")

def main():
    prompt = os.environ.get("SKG_SKILL_PROMPT", "Write a Python script that prints 'SKG heartbeat'. Ensure it defines run(**kwargs).")
    before = {}
    code = _ollama(SYSTEM + "\n\n" + prompt, timeout=90)
    audit_coder("proposal","skillmaker","candidate",code,{"model":MODEL})

    s_ok, s_why = _static_ok(code)
    if not s_ok:
        # fallback minimal safe stub
        code = "def run(**kwargs):\n    print('SKG resilience active')\n"
        audit_coder("rejected","skillmaker","candidate",code,{"reason":s_why})

    r_ok, r_why = _runtime_ok(code)
    SKILLS.mkdir(parents=True, exist_ok=True)
    name = f"skill_{int(time.time())}.py"
    (SKILLS/name).write_text(code)

    # record + audit
    after = {}
    _record_cap(name, "ollama" if s_ok and r_ok else "fallback", 0.9 if (s_ok and r_ok) else 0.5, {"before":before,"after":after})
    audit_coder("staged", "skillmaker", f"/home/skg/.skg_overlay/patches/{name}", code, {"static_ok":s_ok,"runtime_ok":r_ok,"s_why":s_why,"r_why":r_why})
    print(("✅ skill staged: " if (s_ok and r_ok) else "⚙ fallback skill created: ") + name)

if __name__=="__main__":
    main()
