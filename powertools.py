"""
powertools.py  —  10 new power-user features for System Commander
  speak, screenshot, notify, grep, hashtext,
  hexview, baseconv, lorem, zipls, dashboard
"""

import os
import re
import hashlib
import zipfile
import subprocess
import textwrap
import random
import time

BASE = "D:\\"


def _safe(path):
    path = os.path.splitdrive(path)[1].lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        raise PermissionError("Access restricted to D: drive only.")
    return full


# ─── Text-to-Speech ───────────────────────────────────────────────────────────

def speak(text: str):
    """Use Windows SAPI to speak text aloud."""
    from colors import ok, err
    try:
        # Uses PowerShell SAPI — no extra packages
        safe_text = text.replace("'", " ")
        subprocess.Popen(
            ["powershell", "-Command",
             f"Add-Type -AssemblyName System.Speech; "
             f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
             f"$s.Speak('{safe_text}')"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        ok(f"Speaking: {text[:60]}{'...' if len(text) > 60 else ''}")
    except Exception as e:
        err(f"Speak error: {e}")


# ─── Screenshot ───────────────────────────────────────────────────────────────

def screenshot(filename: str = ""):
    """Take a screenshot and save it to D:\\."""
    from colors import ok, err, info
    if not filename:
        filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
    dest = os.path.join(BASE, filename)
    try:
        # Uses PowerShell + .NET — no PIL needed
        subprocess.run(
            ["powershell", "-Command",
             f"Add-Type -AssemblyName System.Windows.Forms; "
             f"Add-Type -AssemblyName System.Drawing; "
             f"$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
             f"$bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height); "
             f"$g = [System.Drawing.Graphics]::FromImage($bmp); "
             f"$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size); "
             f"$bmp.Save('{dest}', [System.Drawing.Imaging.ImageFormat]::Png); "
             f"$g.Dispose(); $bmp.Dispose()"],
            capture_output=True, check=True
        )
        sz = os.path.getsize(dest)
        ok(f"Screenshot saved: {dest}  ({sz//1024} KB)")
    except Exception as e:
        err(f"Screenshot error: {e}")


# ─── Windows Toast Notification ───────────────────────────────────────────────

def notify(title: str, message: str = ""):
    """Show a Windows toast / balloon notification."""
    from colors import ok, err
    try:
        title_s   = title.replace("'", " ")
        message_s = message.replace("'", " ")
        subprocess.Popen(
            ["powershell", "-Command",
             f"Add-Type -AssemblyName System.Windows.Forms; "
             f"$n = New-Object System.Windows.Forms.NotifyIcon; "
             f"$n.Icon = [System.Drawing.SystemIcons]::Information; "
             f"$n.Visible = $true; "
             f"$n.ShowBalloonTip(5000, '{title_s}', '{message_s}', "
             f"[System.Windows.Forms.ToolTipIcon]::Info); "
             f"Start-Sleep -Seconds 6; $n.Dispose()"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        ok(f"Notification sent: {title}")
    except Exception as e:
        err(f"Notify error: {e}")


# ─── Recursive Content Search (grep) ──────────────────────────────────────────

def grep(pattern: str, path: str = ".", extensions: str = ""):
    """Search file contents recursively for a pattern."""
    from colors import ok, err, warn, info, CYAN, GREEN, YELLOW, RESET

    try:
        p = _safe(path)
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        from colors import err
        err(f"Invalid regex: {e}")
        return
    except Exception as e:
        from colors import err
        err(f"Error: {e}")
        return

    exts = [x.strip().lower().lstrip(".") for x in extensions.split(",") if x.strip()] if extensions else []
    matches = 0
    files_checked = 0

    info(f"Searching for '{pattern}' in {p}" + (f" [.{', .'.join(exts)}]" if exts else ""))
    print()

    for root, _, files in os.walk(p):
        for fname in files:
            if exts:
                if not any(fname.lower().endswith("." + e) for e in exts):
                    continue
            fpath = os.path.join(root, fname)
            files_checked += 1
            try:
                with open(fpath, encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, 1):
                        m = rx.search(line)
                        if m:
                            rel = os.path.relpath(fpath, p)
                            highlighted = (
                                line[:m.start()] +
                                f"{GREEN}{m.group()}{RESET}" +
                                line[m.end():]
                            ).rstrip()
                            print(f"  {CYAN}{rel}{RESET}:{YELLOW}{lineno}{RESET}  {highlighted}")
                            matches += 1
                            if matches >= 100:
                                warn("Limit 100 matches reached.")
                                return
            except Exception:
                pass

    print()
    ok(f"{matches} match(es) in {files_checked} file(s).")


# ─── Hash Text ────────────────────────────────────────────────────────────────

def hashtext(algo: str, text: str):
    """Hash a string using md5, sha1, sha256, or sha512."""
    from colors import ok, err, CYAN, RESET
    algos = {"md5": hashlib.md5, "sha1": hashlib.sha1,
             "sha256": hashlib.sha256, "sha512": hashlib.sha512}
    if algo.lower() not in algos:
        err(f"Unknown algorithm '{algo}'. Available: {', '.join(algos)}")
        return
    digest = algos[algo.lower()](text.encode()).hexdigest()
    print(f"  {CYAN}{digest}{RESET}")
    try:
        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{digest}'"],
                       capture_output=True)
        ok(f"{algo.upper()} hash copied to clipboard.")
    except Exception:
        ok(f"{algo.upper()} hash computed.")


# ─── Hex Viewer ───────────────────────────────────────────────────────────────

def hexview(filepath: str, length: int = 256):
    """Display a hex dump of a file (first N bytes)."""
    from colors import info, warn, CYAN, RESET, DIM

    try:
        path = _safe(filepath)
        with open(path, "rb") as f:
            data = f.read(length)
    except Exception as e:
        from colors import err
        err(f"hexview error: {e}")
        return

    info(f"Hex dump: {filepath}  (first {len(data)} bytes)")
    print()
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part  = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {CYAN}{i:08x}{RESET}  {hex_part:<47}  {DIM}|{ascii_part}|{RESET}")

    if len(data) == length:
        from colors import YELLOW
        print(f"\n  {YELLOW}(showing first {length} bytes — pass a larger number to see more){RESET}")


# ─── Number Base Converter ────────────────────────────────────────────────────

def baseconv(number: str, from_base: str, to_base: str):
    """Convert a number between bases (2, 8, 10, 16 or bin/oct/dec/hex)."""
    from colors import ok, err, CYAN, RESET

    base_map = {"bin": 2, "oct": 8, "dec": 10, "hex": 16,
                "2": 2, "8": 8, "10": 10, "16": 16}

    fb = base_map.get(from_base.lower())
    tb = base_map.get(to_base.lower())

    if fb is None:
        err(f"Unknown from-base '{from_base}'. Use: bin oct dec hex 2 8 10 16")
        return
    if tb is None:
        err(f"Unknown to-base '{to_base}'. Use: bin oct dec hex 2 8 10 16")
        return

    try:
        n = int(number, fb)
    except ValueError:
        err(f"'{number}' is not a valid base-{fb} number.")
        return

    result = (
        bin(n)[2:] if tb == 2 else
        oct(n)[2:] if tb == 8 else
        str(n)     if tb == 10 else
        hex(n)[2:].upper()
    )
    prefix = {2: "0b", 8: "0o", 10: "", 16: "0x"}
    ok(f"{number} (base {fb}) = {CYAN}{prefix[tb]}{result}{RESET} (base {tb})")


# ─── Lorem Ipsum Generator ────────────────────────────────────────────────────

_LOREM_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua enim ad minim veniam quis nostrud "
    "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute "
    "irure dolor in reprehenderit voluptate velit esse cillum dolore eu fugiat nulla "
    "pariatur excepteur sint occaecat cupidatat non proident sunt culpa qui officia "
    "deserunt mollit anim est laborum"
).split()

def lorem(word_count: int = 50):
    """Generate a block of lorem ipsum placeholder text."""
    from colors import ok, CYAN, RESET
    words = _LOREM_WORDS[:1] + random.choices(_LOREM_WORDS, k=word_count - 1)
    text = " ".join(words).capitalize() + "."
    wrapped = textwrap.fill(text, width=72)
    print(f"\n  {CYAN}{wrapped}{RESET}\n")
    try:
        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{text}'"],
                       capture_output=True)
        ok("Lorem text copied to clipboard.")
    except Exception:
        ok("Lorem text generated.")


# ─── ZIP Contents Lister ──────────────────────────────────────────────────────

def zipls(filepath: str):
    """List the contents of a ZIP archive without extracting it."""
    from colors import info, ok, warn, err, CYAN, RESET, DIM

    try:
        path = _safe(filepath)
        with zipfile.ZipFile(path, "r") as zf:
            members = zf.infolist()

        if not members:
            warn("Archive is empty.")
            return

        total_size   = sum(m.file_size for m in members)
        compressed   = sum(m.compress_size for m in members)
        ratio        = (1 - compressed / total_size) * 100 if total_size else 0

        info(f"{filepath}  ({len(members)} files,  {total_size//1024} KB → {compressed//1024} KB compressed,  {ratio:.0f}% saved)")
        print(f"\n  {'NAME':<45} {'SIZE':>10}  {'COMPRESSED':>12}  MODIFIED")
        print(f"  {'-'*45} {'-'*10}  {'-'*12}  {'-'*16}")

        for m in sorted(members, key=lambda x: x.filename):
            dt   = f"{m.date_time[0]}-{m.date_time[1]:02d}-{m.date_time[2]:02d}"
            sz   = f"{m.file_size:,}"
            csz  = f"{m.compress_size:,}"
            name = m.filename[:44]
            print(f"  {CYAN}{name:<45}{RESET} {sz:>10}  {DIM}{csz:>12}{RESET}  {dt}")

    except zipfile.BadZipFile:
        from colors import err
        err("Not a valid ZIP file.")
    except Exception as e:
        from colors import err
        err(f"zipls error: {e}")


# ─── System Dashboard ─────────────────────────────────────────────────────────

def dashboard():
    """Display a rich all-in-one system overview."""
    import platform
    import shutil
    import socket
    from colors import BOLD, CYAN, GREEN, YELLOW, RESET, DIM

    try:
        import psutil
    except ImportError:
        from colors import err
        err("psutil required.  Run: pip install psutil")
        return

    print()
    print(f"  {BOLD}{CYAN}{'─'*56}")
    print(f"  {'  SYSTEM COMMANDER  ─  DASHBOARD':^56}")
    print(f"  {'─'*56}{RESET}")
    print()

    # OS & Machine
    print(f"  {BOLD}SYSTEM{RESET}")
    print(f"    {'OS':<18} {platform.system()} {platform.release()} ({platform.version()[:30]})")
    print(f"    {'Machine':<18} {platform.machine()}")
    print(f"    {'Hostname':<18} {socket.gethostname()}")
    try:
        ip = socket.gethostbyname(socket.gethostname())
        print(f"    {'Local IP':<18} {ip}")
    except Exception:
        pass
    print()

    # CPU
    cpu_pct   = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_log   = psutil.cpu_count()
    cpu_bar   = "█" * int(cpu_pct / 5) + "░" * (20 - int(cpu_pct / 5))
    cpu_color = RED if cpu_pct > 80 else YELLOW if cpu_pct > 50 else GREEN
    print(f"  {BOLD}CPU{RESET}  {platform.processor()[:40]}")
    print(f"    [{cpu_color}{cpu_bar}{RESET}] {cpu_pct:.1f}%   {cpu_cores}P / {cpu_log}L cores")
    print()

    # RAM
    ram = psutil.virtual_memory()
    ram_bar = "█" * int(ram.percent / 5) + "░" * (20 - int(ram.percent / 5))
    ram_color = RED if ram.percent > 85 else YELLOW if ram.percent > 65 else GREEN
    print(f"  {BOLD}MEMORY{RESET}")
    print(f"    [{ram_color}{ram_bar}{RESET}] {ram.percent:.1f}%   "
          f"{ram.used//1024**2} MB used / {ram.total//1024**2} MB total")
    print()

    # Disk
    print(f"  {BOLD}DISK  (D:\\){RESET}")
    total, used, free = shutil.disk_usage("D:\\")
    pct  = used / total * 100
    dbar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    dcol = RED if pct > 85 else YELLOW if pct > 65 else GREEN
    print(f"    [{dcol}{dbar}{RESET}] {pct:.1f}%   "
          f"{used//1024**3:.1f} GB used / {total//1024**3:.1f} GB total  ({free//1024**3:.1f} GB free)")
    print()

    # Battery
    try:
        bat = psutil.sensors_battery()
        if bat:
            bat_bar = "█" * int(bat.percent / 5) + "░" * (20 - int(bat.percent / 5))
            bat_col = RED if bat.percent < 20 else YELLOW if bat.percent < 40 else GREEN
            status  = f"{'Charging' if bat.power_plugged else 'On battery'}"
            print(f"  {BOLD}BATTERY{RESET}")
            print(f"    [{bat_col}{bat_bar}{RESET}] {bat.percent:.0f}%   {status}")
            print()
    except Exception:
        pass

    # Uptime
    import datetime
    boot  = psutil.boot_time()
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot)
    print(f"  {BOLD}UPTIME{RESET}  {str(uptime).split('.')[0]}")
    print()

    # Top 5 processes (skip System Idle Process, cap CPU at 100%)
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = p.info
            if info['name'] and 'idle' in info['name'].lower():
                continue
            info['cpu_percent'] = min(info['cpu_percent'], 100.0)
            procs.append(info)
        except Exception:
            pass
    procs.sort(key=lambda x: x['cpu_percent'], reverse=True)
    print(f"  {BOLD}TOP PROCESSES{RESET}")
    print(f"    {'PID':>6}  {'CPU%':>5}  {'MEM%':>5}  NAME")
    print(f"    {'─'*6}  {'─'*5}  {'─'*5}  {'─'*25}")
    for p in procs[:5]:
        cpu_c = RED if p['cpu_percent'] > 50 else YELLOW if p['cpu_percent'] > 20 else GREEN
        print(f"    {p['pid']:>6}  {cpu_c}{p['cpu_percent']:>5.1f}{RESET}  {p['memory_percent']:>5.1f}  {p['name']}")

    print()
    print(f"  {DIM}{'─'*56}{RESET}")
    print()



# Import RED for dashboard
from colors import RED
