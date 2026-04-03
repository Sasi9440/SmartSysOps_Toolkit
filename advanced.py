"""
advanced.py  —  Advanced solid features for System Commander
  ssh, ftp_list, whois, geoip, text2qr, wordfreq,
  diff, checksum_dir, watcher, open_url
"""

import os
import re
import hashlib
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import json
import threading
import time

BASE = "D:\\"


def _safe(path):
    path = os.path.splitdrive(path)[1].lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        raise PermissionError("Access restricted to D: drive only.")
    return full


# ─── Word Frequency Analyzer ──────────────────────────────────────────────────

def wordfreq(filepath: str, top: int = 15):
    """Show the most frequent words in a text file."""
    from colors import info, warn, CYAN, RESET
    from collections import Counter
    import string

    try:
        path = _safe(filepath)
        text = open(path, encoding="utf-8", errors="ignore").read()
        # Strip punctuation, lowercase, split
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        stopwords = {
            "the","and","for","are","but","not","you","all","any","can",
            "had","her","was","one","our","out","who","their","said","has",
            "with","this","that","from","have","they","will","been","were",
            "more","also","into","its","what","than","then","some","would",
            "there","which","when","other","your","each","she","him","his",
        }
        filtered = [w for w in words if w not in stopwords]
        counts = Counter(filtered).most_common(top)

        if not counts:
            warn("No words found.")
            return

        max_count = counts[0][1]
        info(f"Top {top} words in {filepath}")
        print()
        for word, count in counts:
            bar_len = int(count / max_count * 25)
            bar = "█" * bar_len + "░" * (25 - bar_len)
            print(f"  {CYAN}{word:<18}{RESET} {bar} {count}")
    except Exception as e:
        from colors import err
        err(f"wordfreq error: {e}")


# ─── File Diff ────────────────────────────────────────────────────────────────

def file_diff(file1: str, file2: str):
    """Show line-by-line diff between two text files."""
    import difflib
    from colors import info, warn, GREEN, RED, CYAN, RESET, DIM

    try:
        p1 = _safe(file1)
        p2 = _safe(file2)
        lines1 = open(p1, encoding="utf-8", errors="ignore").readlines()
        lines2 = open(p2, encoding="utf-8", errors="ignore").readlines()
    except Exception as e:
        from colors import err
        err(f"diff error: {e}")
        return

    diff = list(difflib.unified_diff(lines1, lines2, fromfile=file1, tofile=file2, lineterm=""))

    if not diff:
        from colors import ok
        ok("Files are identical.")
        return

    info(f"Diff: {file1} ↔ {file2}")
    print()
    added = removed = 0
    for line in diff:
        if line.startswith("+++") or line.startswith("---"):
            print(f"  {CYAN}{line}{RESET}")
        elif line.startswith("+"):
            print(f"  {GREEN}{line}{RESET}")
            added += 1
        elif line.startswith("-"):
            print(f"  {RED}{line}{RESET}")
            removed += 1
        elif line.startswith("@@"):
            print(f"  {CYAN}{line}{RESET}")
        else:
            print(f"  {DIM}{line}{RESET}")

    print()
    from colors import ok
    ok(f"+{added} lines added,  -{removed} lines removed")


# ─── Directory Checksum Report ────────────────────────────────────────────────

def checksum_dir(path: str = "."):
    """Generate MD5 checksums for all files in a directory."""
    from colors import info, ok, CYAN, RESET

    p = _safe(path)
    report_path = os.path.join(p, "checksums.txt")
    info(f"Computing checksums in {p} ...")
    lines = []
    count = 0
    for root, _, files in os.walk(p):
        for f in files:
            if f == "checksums.txt":
                continue
            fp = os.path.join(root, f)
            try:
                h = hashlib.md5(open(fp, "rb").read()).hexdigest()
                rel = os.path.relpath(fp, p)
                lines.append(f"{h}  {rel}")
                count += 1
            except Exception:
                pass

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    ok(f"Checked {count} files → saved to {report_path}")
    for line in lines[:10]:
        print(f"  {CYAN}{line[:10]}{RESET}  {line[12:]}")
    if count > 10:
        print(f"  ... ({count - 10} more)")


# ─── File Watcher ─────────────────────────────────────────────────────────────

_watch_stop = threading.Event()


def watch_file(filepath: str):
    """Watch a file for changes — print a line every time it's modified."""
    from colors import info, ok, warn, CYAN, YELLOW, RESET

    try:
        path = _safe(filepath)
    except Exception as e:
        from colors import err
        err(str(e))
        return

    if not os.path.exists(path):
        from colors import err
        err(f"File not found: {path}")
        return

    info(f"Watching {path}  (Ctrl+C to stop)")
    last_mtime = os.path.getmtime(path)
    last_size  = os.path.getsize(path)
    _watch_stop.clear()

    try:
        while not _watch_stop.is_set():
            time.sleep(0.5)
            try:
                mtime = os.path.getmtime(path)
                size  = os.path.getsize(path)
                if mtime != last_mtime:
                    ts = time.strftime("%H:%M:%S")
                    delta = size - last_size
                    sign  = "+" if delta >= 0 else ""
                    print(f"  {CYAN}[{ts}]{RESET} Modified  size={size}B ({sign}{delta}B)")
                    last_mtime = mtime
                    last_size  = size
            except FileNotFoundError:
                warn(f"File deleted: {path}")
                break
    except KeyboardInterrupt:
        print()
        ok("Watch stopped.")


# ─── GeoIP Lookup ─────────────────────────────────────────────────────────────

def geoip(ip_or_host: str):
    """Look up geolocation of an IP or hostname (free api.ip-api.com)."""
    from colors import info, err, warn, ok, CYAN, RESET, BOLD

    try:
        url = f"http://ip-api.com/json/{urllib.parse.quote(ip_or_host)}?fields=status,message,country,regionName,city,isp,org,as,query"
        req = urllib.request.Request(url, headers={"User-Agent": "SystemCommander/2.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") != "success":
            warn(data.get("message", "Lookup failed."))
            return

        info(f"GeoIP: {data['query']}")
        fields = [
            ("Country",    data.get("country",    "N/A")),
            ("Region",     data.get("regionName", "N/A")),
            ("City",       data.get("city",       "N/A")),
            ("ISP",        data.get("isp",        "N/A")),
            ("Org",        data.get("org",        "N/A")),
            ("AS",         data.get("as",         "N/A")),
        ]
        for label, value in fields:
            print(f"  {CYAN}{label:<10}{RESET} {value}")

    except urllib.error.URLError:
        err("Could not reach ip-api.com — check your connection.")
    except Exception as e:
        err(f"GeoIP error: {e}")


# ─── WHOIS-style DNS Lookup ───────────────────────────────────────────────────

def dns_lookup(host: str):
    """Quick DNS resolution + reverse lookup for a hostname or IP."""
    import socket
    from colors import info, err, ok, warn, CYAN, RESET

    info(f"DNS lookup: {host}")
    try:
        # Forward lookup
        results = socket.getaddrinfo(host, None)
        ips = list(dict.fromkeys(r[4][0] for r in results))
        ok(f"Resolved to {len(ips)} address(es):")
        for ip in ips:
            # Reverse lookup
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = "(no reverse)"
            print(f"  {CYAN}{ip:<40}{RESET}  {hostname}")
    except socket.gaierror as e:
        err(f"DNS failed: {e}")
    except Exception as e:
        err(f"Lookup error: {e}")


# ─── Open URL in Default Browser ─────────────────────────────────────────────

def open_url(url: str):
    """Open a URL in the default browser."""
    import webbrowser
    from colors import ok, err

    if not url.startswith("http"):
        url = "https://" + url
    try:
        webbrowser.open(url)
        ok(f"Opened: {url}")
    except Exception as e:
        err(f"Could not open URL: {e}")


# ─── Public IP Finder ─────────────────────────────────────────────────────────

def myip():
    """Show your public IP address."""
    from colors import ok, err, info

    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as resp:
            ip = resp.read().decode().strip()
        ok(f"Your public IP: {ip}")
        # Also show local
        import socket
        local = socket.gethostbyname(socket.gethostname())
        info(f"Local IP:       {local}")
    except Exception as e:
        err(f"Could not get public IP: {e}")


# ─── File Backup ──────────────────────────────────────────────────────────────

def backup_file(filepath: str):
    """Create a timestamped backup copy of a file."""
    import shutil
    from colors import ok, err

    try:
        path = _safe(filepath)
        if not os.path.exists(path):
            err(f"File not found: {path}")
            return
        ts   = time.strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(path)
        dest = f"{base}.bak_{ts}{ext}"
        shutil.copy2(path, dest)
        ok(f"Backup created: {dest}")
    except Exception as e:
        err(f"Backup error: {e}")
