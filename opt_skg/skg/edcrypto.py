#!/usr/bin/env python3
"""
edcrypto — Ed25519 signing and verification for SKG moons/XRP.
"""
import json
from pathlib import Path
from nacl import signing, exceptions

KEY_DIR = Path("/etc/skg/keys")

def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":")).encode()

def sign(obj:dict, moon:str) -> str:
    keyf = KEY_DIR / f"{moon}.priv"
    sk = signing.SigningKey(keyf.read_bytes())
    return sk.sign(_canon(obj)).signature.hex()

def verify(obj:dict, sig_hex:str, moon:str) -> bool:
    keyf = KEY_DIR / f"{moon}.pub"
    vk = signing.VerifyKey(keyf.read_bytes())
    try:
        vk.verify(_canon(obj), bytes.fromhex(sig_hex))
        return True
    except exceptions.BadSignatureError:
        return False
