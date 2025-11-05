#!/usr/bin/env python3
"""
Skill: securitysense
Whole-system, read-only security posture snapshot for SKG.

What it does (safe):
- Summarizes SSH auth warnings from journalctl (default: last 1h)
- Summarizes open/listening ports via ss
- Summarizes fail2ban if installed
- Summarizes rkhunter status if log available (tries runner if permitted)
- Hashes key SKG runtime files for quick integrity glance (read-only)
- Appends compact counts to governance; full detail to learn_vault

Params (optional, via API body):
  {
    "hours": "1h",            # journalctl since window (e.g. "30m", "6h", "1day")
    "max_lines": 200,         # cap lines per log stream in vault record
    "watch_paths": ["/opt/skg/bin/skg", "/opt/skg/skg/autoheal.py"]  # extra files to hash
  }
"""

import os, json, time, hashlib, shutil, subprocess
from pathlib import Path
from skg.governance import append_event
from skg.learn_vault import append as vault_append

DEF_HOURS = "1h"
DEF_MAX   = 200
DEF_WATCH = [
    "/opt/skg/bin/skg",
    "/opt/skg/skg/autoheal.py",
    "/opt/skg/skg/adaptive.py",
    "/opt/skg/skg/predict.py",
    "/opt/skg/skg/governance.py",
    "/opt/skg/skg/learn.py",
]

def _which(name): return shutil.which(name) is not None

def _cap(lines, n):
    if n is None: return lines
    return lines[: max(0, int(n))]

def _run(cmd, timeout=8):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (p.returncode, p.stdout.strip(), p.stderr.strip())
    except Exception as e:
        return (-1, "", str(e))

def _sha256(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1<<20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"error:{e}"

def _auth_summary(hours, max_lines):
    # SSH auth warnings/errors in window
    # journalctl -p warning..alert -u sshd -S <since>
    code,out,err = _run(["journalctl","-u","sshd","-p","warning..alert","-S",hours,"--no-pager"])
    lines = out.splitlines() if out else []
    return {
        "ok": code==0,
        "lines": _cap(lines, max_lines),
        "count": len(lines),
        "error": err if code!=0 else ""
    }

def _ports_summary():
    # ss -tuln (tcp/udp listening); include ESTAB sample lines safely
    if not _which("ss"):
        return {"ok": False, "error": "ss not found", "listen": [], "estab": []}
    code,out,err = _run(["ss","-tuln"])
    listen = [l for l in (out.splitlines() if out else []) if "LISTEN" in l]
    # established (just count via ss -tn)
    c2,o2,e2 = _run(["ss","-tn"])
    estab = [l for l in (o2.splitlines() if o2 else []) if "ESTAB" in l]
    return {
        "ok": code==0 and c2==0,
        "listen_count": len(listen),
        "estab_count": len(estab),
        "listen_sample": listen[:10],
        "estab_sample": estab[:10],
        "error": err or e2
    }

def _fail2ban_summary():
    if not _which("fail2ban-client"):
        return {"ok": False, "installed": False}
    code,out,err = _run(["fail2ban-client","status"])
    jails=[]
    if code==0:
        for line in out.splitlines():
            if "Jail list" in line:
                jails=[j.strip() for j in line.split(":",1)[-1].split(",") if j.strip()]
                break
    # per-jail quick stats
    jail_stats=[]
    for j in jails[:10]:
        c,o,e = _run(["fail2ban-client","status",j])
        banned=None; currently=None
        if c==0:
            for ln in o.splitlines():
                if "Currently banned" in ln:
                    try: currently=int(ln.split(":")[-1].strip())
                    except: pass
                if "Total banned" in ln:
                    try: banned=int(ln.split(":")[-1].strip())
                    except: pass
        jail_stats.append({"jail": j, "currently_banned": currently, "total_banned": banned})
    return {"ok": True, "installed": True, "jails": jails, "jail_stats": jail_stats, "error": err if code!=0 else ""}

def _rkhunter_summary(max_lines):
    log = Path("/var/log/rkhunter.log")
    if log.exists():
        try:
            lines = log.read_text(errors="ignore").splitlines()
            # take last section
            tail = lines[-max_lines:]
            alerts = [l for l in tail if "Warning:" in l or "Found:" in l]
            return {"ok": True, "source":"log", "alerts": alerts[:100], "lines": len(lines)}
        except Exception as e:
            return {"ok": False, "source":"log", "error": str(e)}
    # try a safe check if binary exists
    if _which("rkhunter"):
        code,out,err = _run(["rkhunter","--versioncheck"], timeout=12)
        return {"ok": code==0, "source":"versioncheck", "note": out.splitlines()[-1] if out else "", "error": err if code!=0 else ""}
    return {"ok": False, "installed": False, "source":"none"}

def _hashes(paths):
    items=[]
    for p in paths:
        items.append({"file": p, "sha256": _sha256(p) if os.path.exists(p) else "missing"})
    return items

def run(**params):
    hours = params.get("hours", DEF_HOURS)
    max_lines = int(params.get("max_lines", DEF_MAX))
    watch_paths = params.get("watch_paths", DEF_WATCH)

    auth   = _auth_summary(hours, max_lines)
    ports  = _ports_summary()
    f2b    = _fail2ban_summary()
    rkh    = _rkhunter_summary(max_lines)
    hashes = _hashes(watch_paths)

    result = {
        "ts": time.time(),
        "window": hours,
        "auth": {"count": auth.get("count",0), "ok": auth.get("ok",False)},
        "ports": {"listen": ports.get("listen_count",0), "estab": ports.get("estab_count",0), "ok": ports.get("ok",False)},
        "fail2ban": {"installed": f2b.get("installed", False), "ok": f2b.get("ok", False), "jails": len(f2b.get("jails",[])) if f2b.get("installed") else 0},
        "rkhunter": {"ok": rkh.get("ok",False), "source": rkh.get("source","none")},
        "hashes": hashes
    }

    # Append compact event to governance
    append_event({
        "actor": "securitysense",
        "type": "posture",
        "window": hours,
        "auth_count": auth.get("count",0),
        "open_listen": ports.get("listen_count",0),
        "open_estab": ports.get("estab_count",0),
        "f2b_installed": f2b.get("installed", False),
        "rkh_source": rkh.get("source","none")
    })

    # Append full snapshot to vault
    full = {
        "actor": "securitysense",
        "window": hours,
        "auth": auth,
        "ports": ports,
        "fail2ban": f2b,
        "rkhunter": rkh,
        "hashes": hashes
    }
    vault_append(full)

    return {"ok": True, "summary": result}
