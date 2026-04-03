"""
dev_tools.py  —  Developer & power-user additions for System Commander
  http, str, portscan, replace, extstats, regex, csv view, color, env
"""

import os
import re
import socket
import urllib.request
import urllib.error
import urllib.parse


BASE = "D:\\"


def _safe(path):
    path = os.path.splitdrive(path)[1].lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        raise PermissionError("Access restricted to D: drive only.")
    return full


# ─── HTTP Request Tool (mini-curl) ────────────────────────────────────────────

def http_request(method: str, url: str, data: str = ""):
    """Perform a quick HTTP request and display the response."""
    from colors import ok, err, info, warn, CYAN, RESET, BOLD, YELLOW

    if not url.startswith("http"):
        url = "https://" + url

    info(f"{method.upper()}  {url}")
    try:
        body = data.encode() if data else None
        headers = {"User-Agent": "SystemCommander/2.0", "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=body, headers=headers, method=method.upper())

        with urllib.request.urlopen(req, timeout=10) as resp:
            status  = resp.status
            content = resp.read().decode("utf-8", errors="replace")
            ct      = resp.headers.get("Content-Type", "")

        color = GREEN if 200 <= status < 300 else YELLOW
        print(f"  Status  : {color}{status}{RESET}")
        print(f"  Type    : {ct}")
        print(f"  Length  : {len(content)} bytes")
        print()

        # Pretty-print JSON if possible
        import json
        try:
            parsed  = json.loads(content)
            preview = json.dumps(parsed, indent=2)[:800]
        except Exception:
            preview = content[:800]

        for line in preview.splitlines()[:25]:
            print(f"  {line}")
        if len(content) > 800:
            print(f"  {YELLOW}... (truncated){RESET}")

    except urllib.error.HTTPError as e:
        err(f"HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        err(f"Request failed: {e.reason}")
    except Exception as e:
        err(f"HTTP error: {e}")


# ─── String Tools ─────────────────────────────────────────────────────────────

def str_tool(action: str, text: str):
    from colors import ok, err, info, CYAN, RESET

    actions = {
        "upper":   lambda t: t.upper(),
        "lower":   lambda t: t.lower(),
        "title":   lambda t: t.title(),
        "reverse": lambda t: t[::-1],
        "len":     lambda t: str(len(t)),
        "count":   lambda t: f"{len(t.split())} words, {len(t)} chars",
        "snake":   lambda t: t.lower().replace(" ", "_"),
        "camel":   lambda t: t[0].lower() + t.title().replace(" ", "")[1:],
        "pascal":  lambda t: t.title().replace(" ", ""),
        "trim":    lambda t: t.strip(),
        "repeat":  lambda t: None,  # placeholder
    }

    if action not in actions:
        err(f"Unknown action '{action}'.  Available: {', '.join(actions)}")
        return

    result = actions[action](text)
    print(f"  {CYAN}{result}{RESET}")

    # auto-copy to clipboard
    try:
        import subprocess
        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{result}'"],
                       capture_output=True)
        ok("Result copied to clipboard.")
    except Exception:
        ok("Done.")


# ─── Port Scanner ─────────────────────────────────────────────────────────────

def portscan(host: str, start: int = 1, end: int = 1024):
    from colors import ok, err, info, warn, CYAN, GREEN, RESET
    import threading

    info(f"Scanning {host}  ports {start}–{end} ...")
    open_ports = []
    lock = threading.Lock()

    def check(port):
        try:
            with socket.create_connection((host, port), timeout=0.5):
                with lock:
                    open_ports.append(port)
        except Exception:
            pass

    threads = [threading.Thread(target=check, args=(p,)) for p in range(start, end + 1)]
    for t in threads:
        t.daemon = True
        t.start()
    for t in threads:
        t.join()

    if open_ports:
        ok(f"Open ports on {host}:")
        for p in sorted(open_ports):
            # common port labels
            labels = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",
                      80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",
                      3306:"MySQL",5432:"PostgreSQL",6379:"Redis",
                      27017:"MongoDB",8080:"HTTP-Alt",8443:"HTTPS-Alt"}
            label = labels.get(p, "")
            print(f"  {GREEN}{p:6}{RESET}  {label}")
    else:
        warn(f"No open ports found on {host} in range {start}–{end}.")


# ─── Find & Replace in File ───────────────────────────────────────────────────

def file_replace(filepath: str, old: str, new: str):
    from colors import ok, err, info, warn
    try:
        path = _safe(filepath)
        content = open(path, "r", encoding="utf-8", errors="ignore").read()
        count = content.count(old)
        if count == 0:
            warn(f"'{old}' not found in {filepath}")
            return
        updated = content.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
        ok(f"Replaced {count} occurrence(s) of '{old}' → '{new}' in {path}")
    except Exception as e:
        err(f"Replace error: {e}")


# ─── File Extension Stats ─────────────────────────────────────────────────────

def extstats(path: str = "."):
    from colors import info, warn, CYAN, RESET, BOLD
    from collections import Counter
    try:
        p = _safe(path)
        counts = Counter()
        sizes = Counter()
        for root, _, files in os.walk(p):
            for f in files:
                ext = os.path.splitext(f)[1].lower() or "(no ext)"
                counts[ext] += 1
                try:
                    sizes[ext] += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
        if not counts:
            warn("No files found.")
            return
        info(f"File types in {p}")
        print(f"  {'EXT':<12} {'COUNT':>6}  {'SIZE':>12}")
        print(f"  {'-'*12} {'-'*6}  {'-'*12}")
        for ext, cnt in counts.most_common():
            sz = sizes[ext]
            sz_str = (f"{sz/1024**2:.1f} MB" if sz > 1024**2 else
                      f"{sz/1024:.1f} KB" if sz > 1024 else f"{sz} B")
            print(f"  {CYAN}{ext:<12}{RESET} {cnt:>6}  {sz_str:>12}")
    except Exception as e:
        from colors import err
        err(f"extstats error: {e}")


# ─── Regex Tester ─────────────────────────────────────────────────────────────

def regex_test(pattern: str, text: str):
    from colors import ok, err, warn, info, GREEN, CYAN, RESET
    try:
        matches = list(re.finditer(pattern, text))
        if not matches:
            warn(f"No matches for pattern: {pattern}")
            return
        ok(f"{len(matches)} match(es) found:")
        for i, m in enumerate(matches, 1):
            print(f"  [{i}]  '{GREEN}{m.group()}{RESET}'  span=({m.start()},{m.end()})")
            if m.groups():
                for j, g in enumerate(m.groups(), 1):
                    print(f"       group {j}: '{CYAN}{g}{RESET}'")
    except re.error as e:
        err(f"Invalid regex: {e}")


# ─── CSV Viewer ───────────────────────────────────────────────────────────────

def csv_view(filepath: str, rows: int = 20):
    import csv
    from colors import err, info, CYAN, RESET, BOLD
    try:
        path = _safe(filepath)
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            all_rows = list(reader)

        if not all_rows:
            from colors import warn
            warn("CSV file is empty.")
            return

        headers = all_rows[0]
        data    = all_rows[1:rows + 1]

        # Calculate column widths
        col_w = [len(h) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                if i < len(col_w):
                    col_w[i] = max(col_w[i], min(len(cell), 30))

        info(f"{filepath}  ({len(all_rows)-1} rows × {len(headers)} cols)")
        print()

        # Header
        header_line = "  " + "  ".join(f"{BOLD}{CYAN}{h:<{col_w[i]}}{RESET}" for i, h in enumerate(headers))
        print(header_line)
        print("  " + "  ".join("-" * col_w[i] for i in range(len(headers))))

        # Rows
        for row in data:
            cells = []
            for i, h in enumerate(headers):
                cell = row[i] if i < len(row) else ""
                cells.append(f"{cell[:30]:<{col_w[i]}}")
            print("  " + "  ".join(cells))

        if len(all_rows) - 1 > rows:
            from colors import YELLOW
            print(f"\n  {YELLOW}... ({len(all_rows)-1 - rows} more rows){RESET}")

    except Exception as e:
        from colors import err
        err(f"CSV error: {e}")


# ─── Color Converter ──────────────────────────────────────────────────────────

def color_convert(action: str, value: str):
    from colors import ok, err, info, CYAN, RESET

    # Strip angle brackets < > that users might copy from help text
    value = value.strip().strip("<>").strip()

    if action == "hex2rgb":
        # Accept both "#FF5733" and "FF5733"
        hex_val = value.lstrip("#").strip("<>").strip()
        if not all(c in "0123456789abcdefABCDEF" for c in hex_val) or len(hex_val) not in (3, 6):
            err("Usage: color hex2rgb #RRGGBB   e.g.  color hex2rgb #FF5733")
            return
        if len(hex_val) == 3:
            hex_val = "".join(c * 2 for c in hex_val)
        r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
        ok(f"#{hex_val.upper()} → rgb({r}, {g}, {b})")
        swatch = f"\033[48;2;{r};{g};{b}m    {RESET}"
        print(f"  Swatch: {swatch}")

    elif action == "rgb2hex":
        parts = value.replace(",", " ").split()
        if len(parts) != 3:
            err("Usage: color rgb2hex R G B   e.g.  color rgb2hex 255 87 51")
            return
        try:
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            err("R G B must be integers 0-255   e.g.  color rgb2hex 255 87 51")
            return
        if not all(0 <= x <= 255 for x in (r, g, b)):
            err("R, G, B values must be between 0 and 255.")
            return
        hex_val = f"#{r:02X}{g:02X}{b:02X}"
        ok(f"rgb({r}, {g}, {b}) → {hex_val}")
        swatch = f"\033[48;2;{r};{g};{b}m    {RESET}"
        print(f"  Swatch: {swatch}")

    else:
        err("Usage:  color hex2rgb #FF5733   |   color rgb2hex 255 87 51")



# ─── Environment Variables ────────────────────────────────────────────────────

def env_list(filter_: str = ""):
    from colors import info, CYAN, RESET
    items = [(k, v) for k, v in os.environ.items()
             if not filter_ or filter_.lower() in k.lower()]
    info(f"Environment variables ({len(items)} shown):")
    for k, v in sorted(items):
        v_display = v[:80] + ("..." if len(v) > 80 else "")
        print(f"  {CYAN}{k:<30}{RESET}  {v_display}")


def env_get(var: str):
    from colors import ok, warn, CYAN, RESET
    val = os.environ.get(var) or os.environ.get(var.upper())
    if val is None:
        warn(f"Variable '{var}' not found.")
    else:
        print(f"  {CYAN}{var}{RESET} = {val}")


# Exposing GREEN for http_request module-level use
from colors import GREEN
