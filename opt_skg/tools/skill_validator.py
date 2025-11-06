#!/usr/bin/env python3
"""
Skill Validator — static + runtime smoke.
Exit 0 = pass, Exit 1 = fail. Prints JSON summary to stdout.
"""
import sys, json, tempfile, re, subprocess

BANNED = [r"\bos\.system\s*\(", r"\bsubprocess\.Popen\s*\(", r"\bexec\s*\(", r"\beval\s*\("]

def run_cmd(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return 1, "", str(e)

def validate(code:str):
    for pat in BANNED:
        if re.search(pat, code):
            return False, {"stage":"static","why":"banned_pattern","pattern":pat}
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as f:
        f.write(code); tmp=f.name
    rc, _, err = run_cmd(f"python3 -m py_compile {tmp}", timeout=10)
    if rc!=0: return False, {"stage":"compile","why":err[:200]}
    rc, out, err = run_cmd(f"python3 {tmp}", timeout=8)
    if rc!=0 or "Traceback" in (out+err):
        return False, {"stage":"runtime","why": (out+err)[:200]}
    return True, {"stage":"ok"}

if __name__=="__main__":
    code = sys.stdin.read()
    ok, detail = validate(code)
    print(json.dumps({"ok":ok,"detail":detail}))
    sys.exit(0 if ok else 1)
