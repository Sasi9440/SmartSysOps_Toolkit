"""
smart.py  —  Smart & quality-of-life features for System Commander
  suggest (did-you-mean), fileinfo, netspeed, health,
  startup, coderead, history_search, template_vars, json2csv, csv2json
"""

import os
import re
import time
import json
import difflib

BASE = "D:\\"

ALL_COMMANDS = [
    "create","delete","move","rename","copy","list","read","write","search",
    "tree","find","size","zip","unzip","hash","compare","tail","count","run",
    "duplicate","recent","empty","bulkrename","volume","brightness","mute",
    "wifi","bluetooth","battery","disk","network","sysinfo","ip","lock","sleep",
    "restart","shutdown","monitor","netstat","ping","speedtest","dashboard","ps",
    "top","kill","clip","note","todo","encrypt","decrypt","schedule","remind",
    "open","apps","ai","alias","log","weather","calc","convert","baseconv",
    "randpass","uuid","lorem","timer","stopwatch","http","download","serve",
    "portscan","geoip","dns","myip","openurl","pycheck","template","snippet",
    "str","regex","grep","replace","jsonformat","csv","extstats","hexview",
    "hashtext","b64","color","env","config","wordfreq","diff","checksum",
    "watch","backup","speak","screenshot","notify","zipls","fileinfo",
    "netspeed","health","startup","coderead","json2csv","csv2json","suggest",
]


def _safe(path):
    path = os.path.splitdrive(path)[1].lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        raise PermissionError("Access restricted to D: drive only.")
    return full


# ─── Did-You-Mean Command Suggester ──────────────────────────────────────────

def suggest(bad_cmd: str):
    """Find the closest matching command to what was typed."""
    from colors import warn, CYAN, RESET
    matches = difflib.get_close_matches(bad_cmd.lower(), ALL_COMMANDS, n=3, cutoff=0.4)
    if matches:
        warn(f"Unknown command '{bad_cmd}'.  Did you mean:")
        for m in matches:
            print(f"    {CYAN}{m}{RESET}")
    else:
        warn(f"Unknown command '{bad_cmd}'.  Type 'help' for available commands.")


# ─── Detailed File Info ───────────────────────────────────────────────────────

def fileinfo(filepath: str):
    """Show detailed metadata for a file."""
    import hashlib
    import stat
    from colors import info, err, CYAN, RESET, BOLD

    try:
        path = _safe(filepath)
        st   = os.stat(path)
        size = st.st_size

        # Human size
        if size >= 1024**3:
            sz_str = f"{size/1024**3:.2f} GB"
        elif size >= 1024**2:
            sz_str = f"{size/1024**2:.2f} MB"
        elif size >= 1024:
            sz_str = f"{size/1024:.2f} KB"
        else:
            sz_str = f"{size} bytes"

        import datetime
        created  = datetime.datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        modified = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        accessed = datetime.datetime.fromtimestamp(st.st_atime).strftime("%Y-%m-%d %H:%M:%S")

        # MD5 (only for files < 100 MB)
        md5 = "skipped (file > 100 MB)"
        if size < 100 * 1024**2:
            md5 = hashlib.md5(open(path, "rb").read()).hexdigest()

        # Line count for text files
        lines = "N/A (binary)"
        ext = os.path.splitext(path)[1].lower()
        text_exts = {".txt",".py",".js",".ts",".json",".csv",".md",".html",".css",".xml",".log",".ini",".cfg",".yaml",".yml"}
        if ext in text_exts:
            try:
                lines = str(len(open(path, encoding="utf-8", errors="ignore").readlines()))
            except Exception:
                pass

        print()
        info(f"File Info: {path}")
        print(f"  {'Name':<16} {os.path.basename(path)}")
        print(f"  {'Extension':<16} {ext or '(none)'}")
        print(f"  {'Size':<16} {sz_str}  ({size:,} bytes)")
        print(f"  {'Lines':<16} {lines}")
        print(f"  {'Created':<16} {created}")
        print(f"  {'Modified':<16} {modified}")
        print(f"  {'Accessed':<16} {accessed}")
        print(f"  {'MD5':<16} {md5}")
        print(f"  {'Full path':<16} {path}")
        print()

    except Exception as e:
        from colors import err
        err(f"fileinfo error: {e}")


# ─── Live Network Speed ───────────────────────────────────────────────────────

def netspeed():
    """Show live upload/download network speed. Ctrl+C to stop."""
    from colors import info, ok, CYAN, GREEN, YELLOW, RED, RESET

    try:
        import psutil
    except ImportError:
        from colors import err
        err("psutil required.  Run: pip install psutil")
        return

    info("Network speed monitor  (Ctrl+C to stop)")
    print()

    prev = psutil.net_io_counters()
    prev_time = time.time()

    try:
        while True:
            time.sleep(1)
            curr      = psutil.net_io_counters()
            curr_time = time.time()
            elapsed   = curr_time - prev_time

            dl = (curr.bytes_recv - prev.bytes_recv) / elapsed
            ul = (curr.bytes_sent - prev.bytes_sent) / elapsed

            def fmt(bps):
                if bps >= 1024**2: return f"{bps/1024**2:6.1f} MB/s"
                if bps >= 1024:    return f"{bps/1024:6.1f} KB/s"
                return f"{bps:6.0f}  B/s"

            dl_c = RED if dl > 5*1024**2 else YELLOW if dl > 512*1024 else GREEN
            ul_c = RED if ul > 5*1024**2 else YELLOW if ul > 512*1024 else GREEN

            print(f"\r  ⬇ {dl_c}{fmt(dl)}{RESET}   ⬆ {ul_c}{fmt(ul)}{RESET}   "
                  f"Total: ↓{curr.bytes_recv//1024**2}MB ↑{curr.bytes_sent//1024**2}MB  ",
                  end="", flush=True)

            prev = curr
            prev_time = curr_time

    except KeyboardInterrupt:
        print()
        ok("Network speed monitor stopped.")


# ─── System Health Score ──────────────────────────────────────────────────────

def health():
    """Generate a system health score and recommendations."""
    import shutil
    from colors import ok, warn, info, BOLD, GREEN, YELLOW, RED, CYAN, RESET

    try:
        import psutil
    except ImportError:
        from colors import err
        err("psutil required.  Run: pip install psutil")
        return

    print()
    info("System Health Report")
    print()

    score = 100
    issues = []

    # CPU
    cpu = psutil.cpu_percent(interval=1)
    if cpu > 85:   score -= 20; issues.append("CPU usage critically high")
    elif cpu > 60: score -= 10; issues.append("CPU usage elevated")
    cpu_c = RED if cpu > 85 else YELLOW if cpu > 60 else GREEN
    print(f"  CPU Usage       {cpu_c}{cpu:5.1f}%{RESET}")

    # RAM
    ram = psutil.virtual_memory()
    if ram.percent > 90:   score -= 20; issues.append("RAM usage critically high")
    elif ram.percent > 75: score -= 10; issues.append("RAM usage elevated")
    ram_c = RED if ram.percent > 90 else YELLOW if ram.percent > 75 else GREEN
    print(f"  RAM Usage       {ram_c}{ram.percent:5.1f}%{RESET}  ({ram.available//1024**2} MB free)")

    # Disk D:\
    total, used, free = shutil.disk_usage("D:\\")
    disk_pct = used / total * 100
    if disk_pct > 90:   score -= 20; issues.append("D:\\ disk almost full")
    elif disk_pct > 75: score -= 10; issues.append("D:\\ disk usage elevated")
    disk_c = RED if disk_pct > 90 else YELLOW if disk_pct > 75 else GREEN
    print(f"  Disk D:\\        {disk_c}{disk_pct:5.1f}%{RESET}  ({free//1024**3:.1f} GB free)")

    # Battery
    try:
        bat = psutil.sensors_battery()
        if bat and not bat.power_plugged:
            if bat.percent < 15:   score -= 20; issues.append("Battery critically low!")
            elif bat.percent < 30: score -= 10; issues.append("Battery low")
            bat_c = RED if bat.percent < 15 else YELLOW if bat.percent < 30 else GREEN
            print(f"  Battery         {bat_c}{bat.percent:5.0f}%{RESET}  (unplugged)")
        elif bat and bat.power_plugged:
            print(f"  Battery         {GREEN}{bat.percent:5.0f}%{RESET}  (charging ✓)")
    except Exception:
        pass

    # Process count
    proc_count = len(list(psutil.process_iter()))
    if proc_count > 200: score -= 5; issues.append("High process count")
    print(f"  Processes       {proc_count}")

    # Uptime
    import datetime
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    days   = uptime.days
    if days > 14: score -= 5; issues.append(f"System up for {days} days — consider restarting")
    print(f"  Uptime          {str(uptime).split('.')[0]}")

    # Score display
    score = max(0, score)
    sc = RED if score < 50 else YELLOW if score < 75 else GREEN
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 50 else "F"
    print()
    print(f"  {BOLD}Health Score:  {sc}{score}/100  (Grade: {grade}){RESET}")
    print()

    if issues:
        warn("Issues found:")
        for issue in issues:
            print(f"    ⚠  {YELLOW}{issue}{RESET}")
    else:
        ok("System is healthy — no issues found! ✓")
    print()


# ─── Windows Startup Programs ─────────────────────────────────────────────────

def startup():
    """List Windows startup programs via registry query (read-only)."""
    from colors import info, warn, err, CYAN, RESET
    import subprocess

    try:
        result = subprocess.run(
            ["reg", "query", "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"],
            capture_output=True, text=True
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip() and "REG_SZ" in l]

        result2 = subprocess.run(
            ["reg", "query", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"],
            capture_output=True, text=True
        )
        lines2 = [l.strip() for l in result2.stdout.splitlines() if l.strip() and "REG_SZ" in l]

        all_entries = [("System", l) for l in lines] + [("User", l) for l in lines2]

        if not all_entries:
            warn("No startup items found.")
            return

        info(f"Startup Programs  ({len(all_entries)} found)")
        print(f"\n  {'SCOPE':<8}  {'NAME':<30}  CMD")
        print(f"  {'─'*8}  {'─'*30}  {'─'*30}")
        for scope, line in all_entries:
            parts = line.split(None, 2)
            name  = parts[0][:29] if parts else line[:29]
            cmd   = parts[2][:50] if len(parts) > 2 else ""
            print(f"  {CYAN}{scope:<8}{RESET}  {name:<30}  {cmd}")

    except Exception as e:
        err(f"startup error: {e}")


# ─── Syntax-Colored Code Reader ───────────────────────────────────────────────

def coderead(filepath: str):
    """Print a code file with simple syntax highlighting."""
    from colors import info, err, warn, CYAN, GREEN, YELLOW, RED, RESET, DIM, BOLD

    KEYWORDS = {"def","class","import","from","return","if","elif","else","for",
                "while","try","except","finally","with","as","pass","break",
                "continue","and","or","not","in","is","None","True","False",
                "lambda","yield","raise","assert","del","global","nonlocal"}

    try:
        path = _safe(filepath)
        lines = open(path, encoding="utf-8", errors="ignore").readlines()
    except Exception as e:
        err(f"coderead error: {e}")
        return

    info(f"  {filepath}  ({len(lines)} lines)")
    print()

    for i, line in enumerate(lines, 1):
        # Simple token colorizer
        colored = line

        # Comments
        if line.strip().startswith("#"):
            print(f"  {DIM}{i:4} │ {line.rstrip()}{RESET}")
            continue

        # Strings (basic)
        colored = re.sub(r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\"[^\"]*\"|\'[^\']*\')',
                         lambda m: f"{GREEN}{m.group()}{RESET}", colored)
        # Numbers
        colored = re.sub(r'\b(\d+\.?\d*)\b',
                         lambda m: f"{YELLOW}{m.group()}{RESET}", colored)
        # Keywords
        for kw in KEYWORDS:
            colored = re.sub(rf'\b{kw}\b', f"{CYAN}{kw}{RESET}", colored)

        print(f"  {DIM}{i:4}{RESET} │ {colored.rstrip()}")

    print()


# ─── JSON to CSV ──────────────────────────────────────────────────────────────

def json2csv(json_file: str, csv_file: str = ""):
    """Convert a JSON array of objects to a CSV file."""
    import csv
    from colors import ok, err, warn

    try:
        src  = _safe(json_file)
        data = json.loads(open(src, encoding="utf-8").read())

        if not isinstance(data, list):
            warn("JSON must be an array of objects.")
            return
        if not data:
            warn("JSON array is empty.")
            return

        dest_name = csv_file or json_file.replace(".json", ".csv")
        dest = _safe(dest_name)
        keys = list(data[0].keys())

        with open(dest, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data)

        ok(f"Converted {src} → {dest}  ({len(data)} rows, {len(keys)} columns)")

    except json.JSONDecodeError as e:
        from colors import err
        err(f"Invalid JSON: {e}")
    except Exception as e:
        from colors import err
        err(f"json2csv error: {e}")


# ─── CSV to JSON ──────────────────────────────────────────────────────────────

def csv2json(csv_file: str, json_file: str = ""):
    """Convert a CSV file to a JSON array of objects."""
    import csv
    from colors import ok, err

    try:
        src  = _safe(csv_file)
        rows = []
        with open(src, newline="", encoding="utf-8", errors="ignore") as f:
            rows = list(csv.DictReader(f))

        dest_name = json_file or csv_file.replace(".csv", ".json")
        dest = _safe(dest_name)

        with open(dest, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)

        ok(f"Converted {src} → {dest}  ({len(rows)} records)")

    except Exception as e:
        err(f"csv2json error: {e}")
