"""
tools.py  —  Extra power-user utilities for System Commander
  calc, randpass, uuid, timer/stopwatch, download, jsonformat,
  b64 encode/decode, serve (quick HTTP), convert (units)
"""

import os
import math
import uuid as _uuid_mod
import base64
import json
import threading
import time
import urllib.request
import urllib.error

# ─── Calculator ───────────────────────────────────────────────────────────────

def calc(expr: str):
    """Evaluate a math expression safely."""
    from colors import ok, err
    allowed = set("0123456789+-*/%.()**^ e")   # whitelist
    if any(c not in allowed for c in expr.replace(" ", "")):
        err("Invalid characters in expression.")
        return
    try:
        expr = expr.replace("^", "**")
        result = eval(expr, {"__builtins__": {}}, {
            "abs": abs, "round": round, "pow": pow,
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "ceil": math.ceil,
            "floor": math.floor,
        })
        ok(f"{expr} = {result}")
    except ZeroDivisionError:
        err("Division by zero.")
    except Exception as e:
        err(f"Calc error: {e}")


# ─── Random Password Generator ────────────────────────────────────────────────

def randpass(length: int = 16, symbols: bool = True):
    """Generate a cryptographically strong random password."""
    import secrets, string
    from colors import ok, info, CYAN, RESET
    chars = string.ascii_letters + string.digits
    if symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    pwd = "".join(secrets.choice(chars) for _ in range(length))

    # Copy to clipboard automatically
    try:
        import subprocess
        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{pwd}'"],
                       capture_output=True)
        info(f"Password ({length} chars) — copied to clipboard:")
    except Exception:
        info(f"Password ({length} chars):")
    print(f"  {CYAN}{pwd}{RESET}")


# ─── UUID Generator ───────────────────────────────────────────────────────────

def gen_uuid():
    from colors import ok, CYAN, RESET
    u = str(_uuid_mod.uuid4())
    try:
        import subprocess
        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{u}'"],
                       capture_output=True)
    except Exception:
        pass
    print(f"  {CYAN}{u}{RESET}")
    ok("UUID generated and copied to clipboard.")


# ─── Timer & Stopwatch ────────────────────────────────────────────────────────

def countdown(seconds: int, label: str = ""):
    """Blocking countdown timer — shows live ticking."""
    from colors import ok, YELLOW, RESET, BOLD, CYAN
    print(f"  Timer: {seconds}s  {label}")
    try:
        for remaining in range(seconds, 0, -1):
            bar_len = 30
            filled  = int(bar_len * (seconds - remaining) / seconds)
            bar     = "█" * filled + "░" * (bar_len - filled)
            print(f"\r  {CYAN}[{bar}]{RESET} {YELLOW}{remaining:4d}s{RESET}  ", end="", flush=True)
            time.sleep(1)
        print(f"\r  {BOLD}[{'█' * 30}]{RESET} {YELLOW}  0s{RESET}  ")
        ok(f"Timer done!  {label}")
        try:
            import subprocess
            subprocess.run(["powershell", "-Command",
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"[System.Windows.Forms.MessageBox]::Show('{label or 'Timer finished!'}', 'System Commander')"])
        except Exception:
            pass
    except KeyboardInterrupt:
        print()
        from colors import warn
        warn("Timer cancelled.")


def stopwatch():
    """Start a stopwatch — press Ctrl+C to stop."""
    from colors import ok, CYAN, RESET, warn
    print("  Stopwatch started — press Ctrl+C to stop.")
    start = time.time()
    try:
        while True:
            elapsed = time.time() - start
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            s = int(elapsed % 60)
            cs = int((elapsed - int(elapsed)) * 100)
            print(f"\r  {CYAN}{h:02d}:{m:02d}:{s:02d}.{cs:02d}{RESET}  ", end="", flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        elapsed = time.time() - start
        print()
        ok(f"Elapsed: {elapsed:.2f}s")


# ─── File Downloader ──────────────────────────────────────────────────────────

def download(url: str, filename: str = ""):
    """Download a file from a URL into D:\\."""
    from colors import ok, err, info
    if not filename:
        filename = url.split("/")[-1].split("?")[0] or "download"
    dest = os.path.join("D:\\", filename)
    info(f"Downloading  {url}")
    info(f"Saving to    {dest}")
    try:
        def _progress(count, block, total):
            if total > 0:
                pct = min(count * block / total * 100, 100)
                bar = "█" * int(pct / 3) + "░" * (33 - int(pct / 3))
                print(f"\r  [{bar}] {pct:5.1f}%  ", end="", flush=True)
        urllib.request.urlretrieve(url, dest, reporthook=_progress)
        print()
        ok(f"Saved: {dest}")
    except Exception as e:
        print()
        err(f"Download failed: {e}")


# ─── JSON Formatter ───────────────────────────────────────────────────────────

def jsonformat(filepath: str):
    """Pretty-print a JSON file in place."""
    from colors import ok, err
    BASE = "D:\\"
    path = filepath.lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        err("Access restricted to D: drive only.")
        return
    try:
        with open(full, "r", encoding="utf-8") as f:
            data = json.load(f)
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        with open(full, "w", encoding="utf-8") as f:
            f.write(pretty)
        ok(f"JSON formatted: {full}")
        print()
        # Preview first 10 lines
        for line in pretty.splitlines()[:10]:
            print(f"  {line}")
        if len(pretty.splitlines()) > 10:
            print(f"  ... ({len(pretty.splitlines())} lines total)")
    except json.JSONDecodeError as e:
        err(f"Invalid JSON: {e}")
    except Exception as e:
        err(f"JSON format error: {e}")


# ─── Base64 Encode / Decode ───────────────────────────────────────────────────

def b64_encode(text: str):
    from colors import ok, CYAN, RESET
    result = base64.b64encode(text.encode()).decode()
    print(f"  {CYAN}{result}{RESET}")
    try:
        import subprocess
        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{result}'"],
                       capture_output=True)
        ok("Encoded and copied to clipboard.")
    except Exception:
        ok("Encoded.")


def b64_decode(text: str):
    from colors import ok, err, CYAN, RESET
    try:
        result = base64.b64decode(text.encode()).decode()
        print(f"  {CYAN}{result}{RESET}")
        ok("Decoded.")
    except Exception as e:
        err(f"Base64 decode error: {e}")


# ─── Quick HTTP Server ────────────────────────────────────────────────────────

_server_thread = None
_server_instance = None

def serve(port: int = 8080):
    """Start a simple HTTP server serving D:\\ on the given port."""
    global _server_thread, _server_instance
    from colors import ok, warn, info, err, CYAN, RESET
    import http.server
    import socket

    if _server_instance:
        warn("Server already running.  Use 'serve stop' to stop it first.")
        return

    os.chdir("D:\\")

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass   # suppress per-request noise

    try:
        _server_instance = http.server.HTTPServer(("", port), _Handler)
    except OSError as e:
        err(f"Could not start server: {e}")
        return

    def _run():
        _server_instance.serve_forever()

    _server_thread = threading.Thread(target=_run, daemon=True)
    _server_thread.start()
    hostname = socket.gethostname()
    ip       = socket.gethostbyname(hostname)
    ok(f"HTTP server started on port {port}")
    info(f"Local  →  {CYAN}http://localhost:{port}{RESET}")
    info(f"LAN    →  {CYAN}http://{ip}:{port}{RESET}")
    info("Type  'serve stop'  to shut it down.")


def serve_stop():
    global _server_instance, _server_thread
    from colors import ok, warn
    if not _server_instance:
        warn("No server is running.")
        return
    _server_instance.shutdown()
    _server_instance = None
    _server_thread   = None
    ok("HTTP server stopped.")


# ─── Unit Converter ───────────────────────────────────────────────────────────

_CONVERSIONS = {
    # Temperature (handled specially below)
    # Length
    ("km",  "mi"):    lambda x: x * 0.621371,
    ("mi",  "km"):    lambda x: x * 1.60934,
    ("m",   "ft"):    lambda x: x * 3.28084,
    ("ft",  "m"):     lambda x: x * 0.3048,
    ("m",   "cm"):    lambda x: x * 100,
    ("cm",  "m"):     lambda x: x / 100,
    ("cm",  "in"):    lambda x: x * 0.393701,
    ("in",  "cm"):    lambda x: x * 2.54,
    # Weight
    ("kg",  "lb"):    lambda x: x * 2.20462,
    ("lb",  "kg"):    lambda x: x * 0.453592,
    ("g",   "oz"):    lambda x: x * 0.035274,
    ("oz",  "g"):     lambda x: x * 28.3495,
    # Data
    ("mb",  "gb"):    lambda x: x / 1024,
    ("gb",  "mb"):    lambda x: x * 1024,
    ("gb",  "tb"):    lambda x: x / 1024,
    ("tb",  "gb"):    lambda x: x * 1024,
    ("kb",  "mb"):    lambda x: x / 1024,
    ("mb",  "kb"):    lambda x: x * 1024,
    # Speed
    ("kmh", "mph"):   lambda x: x * 0.621371,
    ("mph", "kmh"):   lambda x: x * 1.60934,
    ("ms",  "kmh"):   lambda x: x * 3.6,
    ("kmh", "ms"):    lambda x: x / 3.6,
}

def convert(value_str: str, from_u: str, to_u: str):
    from colors import ok, err, CYAN, RESET
    try:
        value = float(value_str)
    except ValueError:
        err("Usage: convert <number> <from_unit> <to_unit>")
        return

    f = from_u.lower()
    t = to_u.lower()

    # Temperature special cases
    if f == "c" and t == "f":
        result = value * 9/5 + 32
    elif f == "f" and t == "c":
        result = (value - 32) * 5/9
    elif f == "c" and t == "k":
        result = value + 273.15
    elif f == "k" and t == "c":
        result = value - 273.15
    elif f == "f" and t == "k":
        result = (value - 32) * 5/9 + 273.15
    elif f == "k" and t == "f":
        result = (value - 273.15) * 9/5 + 32
    elif (f, t) in _CONVERSIONS:
        result = _CONVERSIONS[(f, t)](value)
    else:
        err(f"Unknown conversion: {from_u} → {to_u}")
        err("Supported: km↔mi, m↔ft, cm↔in, kg↔lb, g↔oz, mb↔gb, gb↔tb, kmh↔mph, ms↔kmh, C↔F↔K")
        return

    ok(f"{value} {from_u} = {CYAN}{result:.4f} {to_u}{RESET}")
