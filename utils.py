import os
import json
import datetime
import urllib.request

# ─── Paths ────────────────────────────────────────────────────────────────────
ALIASES_FILE = "D:\\sc_aliases.json"
LOG_FILE     = "D:\\sc_log.txt"

# ─── Logging ──────────────────────────────────────────────────────────────────

import threading as _threading
_log_lock = _threading.Lock()

def log_command(cmd: str):
    """Append every executed command with a timestamp to the log file."""
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with _log_lock:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {cmd}\n")
    except Exception:
        pass   # silent — logging must never crash the app



def show_log(n: int = 20):
    """Print last N log entries."""
    from colors import info, warn
    if not os.path.exists(LOG_FILE):
        warn("No log file found yet.")
        return
    lines = open(LOG_FILE, encoding="utf-8").readlines()
    entries = lines[-n:] if len(lines) >= n else lines
    if not entries:
        warn("Log is empty.")
        return
    info(f"Last {len(entries)} log entries  ({LOG_FILE})")
    for line in entries:
        print(f"  {line}", end="")
    print()


def clear_log():
    from colors import ok, warn
    if not os.path.exists(LOG_FILE):
        warn("No log file to clear.")
        return
    open(LOG_FILE, "w").close()
    ok("Log cleared.")


# ─── Alias System ─────────────────────────────────────────────────────────────

def _load_aliases() -> dict:
    if os.path.exists(ALIASES_FILE):
        try:
            return json.loads(open(ALIASES_FILE, encoding="utf-8").read())
        except Exception:
            pass
    return {}


def _save_aliases(aliases: dict):
    with open(ALIASES_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(aliases, indent=2))


def expand_alias(cmd: str) -> str:
    """If the first word matches a saved alias, expand it."""
    parts = cmd.strip().split(None, 1)
    if not parts:
        return cmd
    aliases = _load_aliases()
    if parts[0] in aliases:
        rest = parts[1] if len(parts) > 1 else ""
        return (aliases[parts[0]] + " " + rest).strip()
    return cmd


def alias_add(name: str, command: str):
    from colors import ok, err
    if not name or not command:
        err("Usage: alias add <name> <command>")
        return
    aliases = _load_aliases()
    aliases[name] = command
    _save_aliases(aliases)
    ok(f"Alias '{name}' → '{command}' saved.")


def alias_list():
    from colors import info, warn, CYAN, RESET, BOLD
    aliases = _load_aliases()
    if not aliases:
        warn("No aliases defined yet.  Use: alias add <name> <command>")
        return
    info(f"Saved aliases  ({ALIASES_FILE})")
    for name, cmd in aliases.items():
        print(f"  {BOLD}{CYAN}{name:<15}{RESET}  {cmd}")


def alias_remove(name: str):
    from colors import ok, err
    aliases = _load_aliases()
    if name not in aliases:
        err(f"Alias '{name}' not found.")
        return
    del aliases[name]
    _save_aliases(aliases)
    ok(f"Alias '{name}' removed.")


# ─── Weather ──────────────────────────────────────────────────────────────────

def weather(city: str = ""):
    from colors import err, info, warn
    city = city.strip().replace(" ", "+") or "auto"
    url  = f"https://wttr.in/{city}?format=4"      # one-liner format
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = resp.read().decode("utf-8").strip()
        info(f"Weather  [{city.replace('+', ' ')}]")
        print(f"  {data}")
    except urllib.error.URLError:
        err("Could not reach wttr.in — check your internet connection.")
    except Exception as e:
        err(f"Weather error: {e}")


# ─── Clipboard History ────────────────────────────────────────────────────────

CLIP_HISTORY_FILE = "D:\\sc_clip_history.json"
CLIP_HISTORY_MAX  = 20


def _load_clip_history() -> list:
    if os.path.exists(CLIP_HISTORY_FILE):
        try:
            return json.loads(open(CLIP_HISTORY_FILE, encoding="utf-8").read())
        except Exception:
            pass
    return []


def _save_clip_history(history: list):
    with open(CLIP_HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(history[-CLIP_HISTORY_MAX:], indent=2))


def clip_history_add(text: str):
    """Call this every time something is copied."""
    h = _load_clip_history()
    if text and (not h or h[-1] != text):   # avoid duplicates
        h.append(text)
    _save_clip_history(h)


def clip_history_show():
    from colors import info, warn
    h = _load_clip_history()
    if not h:
        warn("Clipboard history is empty.")
        return
    info(f"Clipboard history  (last {len(h)} items)")
    for i, item in enumerate(reversed(h), 1):
        preview = item[:80].replace("\n", "↵")
        print(f"  {i:2}. {preview}")


def clip_history_clear():
    from colors import ok
    _save_clip_history([])
    ok("Clipboard history cleared.")
