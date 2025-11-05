#!/usr/bin/env python3
import os, time, subprocess, tempfile, shutil
from skg.governance import append_event
def run(**params):
    code = params.get("code","fn main(){println!(\"hello\");}")
    rustc=shutil.which("rustc")
    if not rustc:
        append_event({"actor":"runner.rust","type":"propose_install","detail":"rustup or rustc not found"})
        return {"ok":False,"error":"rustc not found; propose install via rustup"}
    with tempfile.TemporaryDirectory() as d:
        src=os.path.join(d,"skg.rs"); binp=os.path.join(d,"skg_bin")
        open(src,"w").write(code)
        c=subprocess.run([rustc,src,"-O","-o",binp],capture_output=True,text=True,timeout=20)
        if c.returncode!=0:
            append_event({"actor":"runner.rust","type":"compile_error","stderr":c.stderr[-4000:]})
            return {"ok":False,"error":"compile failed","stderr":c.stderr[-4000:]}
        r=subprocess.run([binp],capture_output=True,text=True,timeout=5)
        append_event({"actor":"runner.rust","type":"exec","rc":r.returncode})
        return {"ok":r.returncode==0,"rc":r.returncode,"stdout":r.stdout[-4000:],"stderr":r.stderr[-4000:]}
