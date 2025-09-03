from __future__ import annotations

from typing import Tuple
import requests


def check_ollama(api_base: str, model: str, timeout: int = 5) -> Tuple[bool, str]:
    """Check Ollama availability and whether model is present locally.

    Returns (ok, message)
    """
    try:
        r = requests.get(api_base.rstrip("/") + "/tags", timeout=timeout)
        r.raise_for_status()
        data = r.json()
        models = [m.get("name", "") for m in data.get("models", [])]
        # Some installations may return names like "gemma:2b" or canonical names
        present = any(model in m or m in model for m in models)
        if present:
            return True, f"Ollama OK. Model available: {model}"
        return False, f"Ollama reachable but model not found: {model}. Run 'ollama pull {model}'."
    except Exception as e:
        return False, f"Failed to reach Ollama at {api_base}: {e}"

