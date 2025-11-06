#!/usr/bin/env python3
import hmac, hashlib, json
from pathlib import Path
KEY_PATH = Path("/etc/skg/moon.key")

def _key()->bytes:
    return KEY_PATH.read_bytes().strip()

def canonical(obj)->str:
    return json.dumps(obj, sort_keys=True, separators=(",",":"))

def sign(obj:dict)->str:
    data = canonical(obj).encode()
    return hmac.new(_key(), data, hashlib.sha256).hexdigest()

def verify(obj:dict, sig:str)->bool:
    try:
        data = canonical(obj).encode()
        mac = hmac.new(_key(), data, hashlib.sha256).hexdigest()
        return hmac.compare_digest(mac, sig)
    except Exception:
        return False
