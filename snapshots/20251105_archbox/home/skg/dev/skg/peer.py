#!/usr/bin/env python3
"""
Consent-based peer understanding:
- Build our own identity + manifest.
- Load another SKG's manifest (from a file path or explicit URL you provide).
- Compare by information: theme overlap, code density, audit/vault scale.
- Log an "understanding" event to governance and a full record to learn_vault.

No network scanning. No discovery. Only explicit path/URL passed in by operator.
"""
import json, os, time
from urllib.parse import urlparse
from skg.identity import info_fingerprint
from skg.manifest import build_manifest
from skg.learn_vault import append as vault_append
from skg.governance import append_event

def _load_manifest_from_file(path:str):
    with open(path) as f: return json.load(f)

def _load_manifest_from_url(url:str, timeout=6):
    # Only fetch if operator explicitly passes a URL.
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent":"SKG/peer"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8","ignore"))

def meet(peer_source:str):
    """peer_source: local file path OR explicit http(s) url"""
    ours = {
        "identity": info_fingerprint(),
        "manifest": build_manifest()
    }
    # load peer
    parsed = urlparse(peer_source)
    if parsed.scheme in ("http","https"):
        peer = _load_manifest_from_url(peer_source)
        source_kind="url"
    else:
        peer = _load_manifest_from_file(peer_source)
        source_kind="file"

    # compare by information
    our_themes = set(ours["manifest"].get("themes",[]))
    peer_themes = set(peer.get("themes",[]))
    overlap = sorted(list(our_themes & peer_themes))[:24]
    similarity = round(len(overlap) / max(1, len(our_themes|peer_themes)), 3)

    understanding = {
        "ts": time.time(),
        "type":"peer_understanding",
        "ours": {"fingerprint": ours["identity"]["fingerprint"],
                 "counts": ours["manifest"]["counts"]},
        "peer": {"counts": peer.get("counts",{}), "themes": peer.get("themes",[])[:24]},
        "overlap": overlap,
        "similarity": similarity,
        "source_kind": source_kind
    }
    append_event({"actor":"peer","type":"understanding","similarity":similarity,"source":source_kind})
    vault_append({"actor":"peer","understanding":understanding})
    return understanding

def export_manifest(path:str="/opt/skg/manifest.json"):
    m=build_manifest()
    with open(path,"w") as f: json.dump(m,f,indent=2)
    append_event({"actor":"peer","type":"export_manifest","path":path})
    return {"ok":True,"path":path}
