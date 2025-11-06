#!/usr/bin/env python3
# Canonical registry exposing SKG skills as "tools" with JSON schemas.
# Extend REGISTRY to add more tools; the agent reads this to plan actions.
REGISTRY = {
  "cognition": {
    "description": "General reasoning / text generation via local LLM",
    "parameters": {"type":"object","properties":{"prompt":{"type":"string"}}, "required":["prompt"]}
  },
  "run_python": {
    "description": "Execute short Python in a sandbox; returns stdout/stderr",
    "parameters": {"type":"object","properties":{"code":{"type":"string"}}, "required":["code"]}
  },
  "run_bash": {
    "description": "Execute simple shell commands (no network); returns stdout/stderr",
    "parameters": {"type":"object","properties":{"cmd":{"type":"string"}}, "required":["cmd"]}
  },
  "reflect": {
    "description": "Record a reflection entry to stabilize equilibrium",
    "parameters": {"type":"object","properties":{"prompt":{"type":"string"}}, "required":["prompt"]}
  },
  "rag_query": {
    "description": "Local retrieval: search SKG code & memory; returns top snippets",
    "parameters": {"type":"object","properties":{"query":{"type":"string"}, "k":{"type":"integer"}}, "required":["query"]}
  },
  "telemetry_query": {
    "description": "Return current telemetry snapshot (entropy, ethics_coherence, etc.)",
    "parameters": {"type":"object","properties":{}}
  }
}

def list_tools():
    tools=[]
    for name, meta in REGISTRY.items():
        tools.append({
          "type":"function",
          "function":{
            "name": name,
            "description": meta["description"],
            "parameters": meta["parameters"]
          }
        })
    return tools

def get_signature(name): return REGISTRY.get(name)
