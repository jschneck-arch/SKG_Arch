#!/usr/bin/env python3
import json, time
from pathlib import Path

W=Path("/opt/skg/www/dashboard.html")
TEL=Path("/var/lib/skg/state/telemetry.json")
CONS=Path("/var/lib/skg/state/rnt_consensus.json")
PEERS=Path("/var/lib/skg/state/rnt_peers.json")
CAPS=Path("/var/lib/skg/state/capabilities.jsonl")

def readj(p, d=None):
    try: return json.loads(Path(p).read_text())
    except: return d if d is not None else {}

def tail_caps(n=10):
    if not CAPS.exists(): return []
    lines=CAPS.read_text().strip().splitlines()[-n:]
    return [json.loads(x) for x in lines if x.strip()]

t=readj(TEL, {})
c=readj(CONS, {})
p=readj(PEERS, {"peers":{}}).get("peers",{})
caps=tail_caps()

html=f"""<!doctype html>
<meta charset="utf-8">
<title>SKG Dashboard</title>
<style>
body{{font-family:system-ui,Segoe UI,Roboto,Arial;margin:24px;}}
h1{{margin-top:0}} .card{{padding:16px;margin:12px 0;border:1px solid #ddd;border-radius:12px}}
pre{{white-space:pre-wrap;word-break:break-word}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}}
</style>
<h1>SKG Dashboard — {time.strftime('%Y-%m-%d %H:%M:%S')}</h1>
<div class="grid">
  <div class="card"><h2>Telemetry</h2><pre>{json.dumps(t,indent=2)}</pre></div>
  <div class="card"><h2>RNT Consensus</h2><pre>{json.dumps(c,indent=2)}</pre></div>
  <div class="card"><h2>RNT Peers</h2><pre>{json.dumps(p,indent=2)}</pre></div>
  <div class="card"><h2>Capabilities (last {len(caps)})</h2><pre>{json.dumps(caps,indent=2)}</pre></div>
</div>
"""
W.write_text(html)
print(f"Wrote {W}")
