r"""
env_loader.py  —  Minimal .env file parser (no external dependencies)
Reads D:\NEW\.env and exposes get(key) for the rest of the app.
"""

import os

_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
_cache: dict = {}
_loaded = False


def _load():
    global _loaded
    if _loaded:
        return
    _loaded = True
    if not os.path.exists(_ENV_FILE):
        return
    with open(_ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key   = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                _cache[key] = value


def get(key: str, default: str = "") -> str:
    """Return the value of a key from .env, or default if not found."""
    _load()
    return _cache.get(key, os.environ.get(key, default))


def set_value(key: str, value: str):
    """Write / update a key=value pair in .env (in-place)."""
    _load()
    _cache[key] = value

    lines = []
    if os.path.exists(_ENV_FILE):
        with open(_ENV_FILE, encoding="utf-8") as f:
            lines = f.readlines()

    # Update existing line or append
    found = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            continue
        k = stripped.partition("=")[0].strip()
        if k == key:
            lines[i] = f"{key}={value}\n"
            found = True
            break

    if not found:
        lines.append(f"{key}={value}\n")

    with open(_ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def list_keys():
    """Return all keys from .env (values masked for security)."""
    _load()
    return {k: ("*" * min(len(v), 8) + "..." if v and v != "your_groq_api_key_here" else "(not set)")
            for k, v in _cache.items()}
