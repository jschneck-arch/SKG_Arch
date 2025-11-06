#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
Topology Encoder (append-only)
- encode_new(): scan pearls.jsonl from last pointer and append coordinates to topology_index.jsonl
- encode_text(s): helper -> small fixed-length vector (normalized token frequencies)
"""
import json, math, time, re
from pathlib import Path
from collections import Counter
from datetime import datetime
from skg.paths import SKG_MEMORY_DIR, SKG_STATE_DIR

PEARLS_PATH   = Path(SKG_MEMORY_DIR) / "pearls.jsonl"
TOPO_INDEX    = Path(SKG_MEMORY_DIR) / "topology_index.jsonl"
VECTOR_DIR    = Path(SKG_STATE_DIR)  / "vectors"
VECTOR_DIR.mkdir(parents=True, exist_ok=True)
STATE_VECTOR  = VECTOR_DIR / "state_vector.json"
POINTER_PATH  = VECTOR_DIR / "encoder_pointer.json"

WORD_RE = re.compile(r"[A-Za-z0-9_]+")

def _tokenize(msg: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(msg or "")]

def encode_text(text: str, top_n: int = 8):
    toks = _tokenize(text or "")
    counts = Counter(toks)
    tops = [t for t,_ in counts.most_common(top_n)]
    tot = sum(counts[t] for t in tops) or 1
    return [counts[t]/tot for t in tops] + [0.0]*(top_n-len(tops))

def _phase_from_ts(ts: float) -> float:
    return (ts % 60.0) / 60.0 * (2*math.pi)

def _energy_from_counts(counts: Counter) -> float:
    k = 8
    vals = [c for _, c in counts.most_common(k)]
    return math.sqrt(sum(v*v for v in vals)) if vals else 0.0

def load_pointer():
    if POINTER_PATH.exists():
        return json.loads(POINTER_PATH.read_text())
    return {"offset": 0}

def save_pointer(ptr):
    POINTER_PATH.write_text(json.dumps(ptr, indent=2))

def append_topology_row(row: dict):
    TOPO_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with TOPO_INDEX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def snapshot_vector(vector: dict):
    versions = []
    if STATE_VECTOR.exists():
        try:
            prev = json.loads(STATE_VECTOR.read_text())
            versions = prev.get("versions", [])
        except Exception:
            pass
    vector["timestamp"] = time.time()
    versions.append(vector)
    STATE_VECTOR.write_text(json.dumps({"versions": versions[-50:]}, indent=2))

def encode_new():
    pointer = load_pointer()
    offset = pointer.get("offset", 0)
    if not PEARLS_PATH.exists():
        return {"processed": 0, "note": "no pearls"}

    processed = 0
    token_counts = Counter()
    kind_counts  = Counter()

    with PEARLS_PATH.open("r", encoding="utf-8") as f:
        f.seek(offset)
        for line in f:
            pos = f.tell()
            try:
                pearl = json.loads(line)
            except Exception:
                continue

            ts = pearl.get("timestamp") or pearl.get("ts") or time.time()
            kind = pearl.get("type") or pearl.get("kind") or "unknown"
            msg  = pearl.get("data", {}).get("insight") or pearl.get("msg") or pearl.get("text") or ""
            toks = _tokenize(msg)
            token_counts.update(toks)
            kind_counts.update([kind])

            phase  = _phase_from_ts(ts)
            energy = _energy_from_counts(token_counts)

            # tiny normalized vector from current token counts (top 8)
            top_tokens = [t for t,_ in token_counts.most_common(8)]
            tot = sum(token_counts[t] for t in top_tokens) or 1
            vec = [(token_counts[t]/tot) for t in top_tokens]

            topo_row = {
                "ts": ts,
                "kind": kind,
                "phase": phase,
                "energy": energy,
                "top_tokens": top_tokens,
                "vec": vec,
            }
            append_topology_row(topo_row)
            processed += 1
        pointer["offset"] = f.tell()

    dom_kind = max(kind_counts, key=kind_counts.get) if kind_counts else None
    state_vec = {
        "dominant_kind": dom_kind,
        "token_count": sum(token_counts.values()),
        "distinct_tokens": len(token_counts),
        "energy": _energy_from_counts(token_counts),
    }
    snapshot_vector(state_vec)
    save_pointer(pointer)
    return {"processed": processed, "dominant_kind": dom_kind, "energy": state_vec["energy"]}

if __name__ == "__main__":
    print(encode_new())
