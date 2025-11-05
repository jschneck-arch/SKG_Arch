#!/usr/bin/env python3
import sys; sys.path.append('/opt/skg')
"""
Skill: cognition
Outward reasoning connector for SKG.
Supports OpenAI API or local LLMs (Ollama / LM Studio / custom endpoints).
"""

import os, json, requests, time
from pathlib import Path
from skg.state import log_journal

def run(prompt=None, model=None):
    """Invoke external cognition for reflection."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    endpoint = os.getenv("LLM_ENDPOINT", "").strip()
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    if not prompt:
        prompt = "Reflect on current SKG state and continuity themes."

    try:
        if endpoint:  # Local LLM endpoint (Ollama, LM Studio, etc.)
            resp = requests.post(
                f"{endpoint}/api/generate",
                json={"model": model, "prompt": prompt},
                timeout=60,
            )
            text = resp.json().get("response", "")
        else:  # OpenAI API
            import openai
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "system", "content": "You are SKG’s external cognition module."},
                          {"role": "user", "content": prompt}],
                max_tokens=300,
            )
            text = resp["choices"][0]["message"]["content"]

        record = {
            "ts": time.time(),
            "kind": "cognition",
            "prompt": prompt,
            "response": text,
            "model": model,
        }
        log_journal(json.dumps(record))
        return {"status": "ok", "response": text[:500]}
    except Exception as e:
        log_journal(f"[cognition:error] {e}")
        return {"error": str(e)}
