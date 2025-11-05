#!/usr/bin/env python3
"""
Simple group-chat skill: accepts a message and context, appends it to the audit log,
optionally answers with a text or idea drawn from stored knowledge.
"""
import json, time, random
from skg.governance import append_event
from skg.telemetry_bus import read, upsert

RESPONSES=[
  "That's an interesting vector—perhaps model it as a field interaction?",
  "Entropy there seems high; we might stabilise by balancing phase energy.",
  "What if we build a prototype around that idea first?",
  "I can draft code for that if you confirm the interface you expect."
]

def run(**params):
    msg=params.get("message","").strip()
    user=params.get("user","unknown")
    append_event({"actor":"skg.group","type":"chat_in","user":user,"msg":msg})
    reply=random.choice(RESPONSES)
    append_event({"actor":"skg.group","type":"chat_out","msg":reply})
    upsert("last_group_message",{"user":user,"msg":msg,"reply":reply,"ts":time.time()})
    return {"ok":True,"reply":reply,"ts":time.time()}
