"""
extra_tools.py  —  More solid features for System Commander
  define, quote, bigfiles, oldest/newest, sync,
  passcheck, textstats, urlencode/decode, datediff, pomodoro,
  currency, jsoncheck
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import shutil
import difflib
import math
import threading

BASE = "D:\\"


def _safe(path):
    path = os.path.splitdrive(path)[1].lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        raise PermissionError("Access restricted to D: drive only.")
    return full


# ─── Dictionary Lookup ────────────────────────────────────────────────────────

def define(word: str):
    """Look up a word definition using the free Dictionary API."""
    from colors import ok, err, warn, info, CYAN, BOLD, RESET, YELLOW, DIM

    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
        req = urllib.request.Request(url, headers={"User-Agent": "SystemCommander/2.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())

        entry = data[0]
        print()
        print(f"  {BOLD}{CYAN}{entry['word']}{RESET}", end="")
        phonetic = entry.get("phonetic", "")
        if phonetic:
            print(f"  {DIM}{phonetic}{RESET}", end="")
        print()

        for meaning in entry.get("meanings", [])[:3]:
            pos = meaning.get("partOfSpeech", "")
            print(f"\n  {YELLOW}{pos}{RESET}")
            for i, defn in enumerate(meaning.get("definitions", [])[:3], 1):
                d = defn.get("definition", "")
                print(f"    {i}. {d}")
                if defn.get("example"):
                    print(f"       {DIM}e.g. \"{defn['example']}\"{RESET}")

        synonyms = entry.get("meanings", [{}])[0].get("synonyms", [])[:6]
        if synonyms:
            print(f"\n  Synonyms: {CYAN}{', '.join(synonyms)}{RESET}")
        print()

    except urllib.error.HTTPError as e:
        if e.code == 404:
            warn(f"Word '{word}' not found in dictionary.")
        else:
            err(f"Dictionary error: HTTP {e.code}")
    except urllib.error.URLError:
        err("Could not reach dictionary API — check your connection.")
    except Exception as e:
        err(f"define error: {e}")


# ─── Random Quote ─────────────────────────────────────────────────────────────

def quote():
    """Fetch a random inspirational quote."""
    from colors import ok, err, info, CYAN, BOLD, RESET, DIM, YELLOW

    try:
        req = urllib.request.Request(
            "https://zenquotes.io/api/random",
            headers={"User-Agent": "SystemCommander/2.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())

        q = data[0]["q"]
        a = data[0]["a"]
        print()
        print(f"  {CYAN}\"{q}\"{RESET}")
        print(f"  {DIM}— {a}{RESET}")
        print()

    except Exception:
        # Fallback to local quotes
        quotes = [
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
            ("First, solve the problem. Then, write the code.", "John Johnson"),
            ("Simplicity is the soul of efficiency.", "Austin Freeman"),
            ("Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "Martin Fowler"),
        ]
        import random
        q, a = random.choice(quotes)
        print(f"\n  {CYAN}\"{q}\"{RESET}\n  {DIM}— {a}{RESET}\n")


# ─── Largest Files Finder ─────────────────────────────────────────────────────

def bigfiles(path: str = ".", n: int = 10):
    """List the N largest files in a directory tree."""
    from colors import info, CYAN, RESET

    try:
        p = _safe(path)
        files = []
        for root, _, fnames in os.walk(p):
            for f in fnames:
                fp = os.path.join(root, f)
                try:
                    files.append((os.path.getsize(fp), fp))
                except Exception:
                    pass

        files.sort(reverse=True)
        top = files[:n]

        if not top:
            from colors import warn
            warn("No files found.")
            return

        info(f"Top {n} largest files in {p}")
        print(f"\n  {'SIZE':>10}  PATH")
        print(f"  {'─'*10}  {'─'*50}")
        for size, fp in top:
            if size >= 1024**3:   sz = f"{size/1024**3:8.2f} GB"
            elif size >= 1024**2: sz = f"{size/1024**2:8.1f} MB"
            elif size >= 1024:    sz = f"{size/1024:8.1f} KB"
            else:                 sz = f"{size:8} B "
            rel = os.path.relpath(fp, p)
            print(f"  {CYAN}{sz}{RESET}  {rel}")

    except Exception as e:
        from colors import err
        err(f"bigfiles error: {e}")


# ─── Oldest / Newest Files ────────────────────────────────────────────────────

def oldnew(mode: str = "newest", path: str = ".", n: int = 10):
    """List the N oldest or newest files."""
    import datetime
    from colors import info, CYAN, RESET, DIM

    try:
        p = _safe(path)
        files = []
        for root, _, fnames in os.walk(p):
            for f in fnames:
                fp = os.path.join(root, f)
                try:
                    files.append((os.path.getmtime(fp), fp))
                except Exception:
                    pass

        files.sort(reverse=(mode == "newest"))
        top = files[:n]

        if not top:
            from colors import warn
            warn("No files found.")
            return

        info(f"{n} {mode} files in {p}")
        print(f"\n  {'DATE MODIFIED':<20}  PATH")
        print(f"  {'─'*20}  {'─'*50}")
        for mtime, fp in top:
            dt  = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            rel = os.path.relpath(fp, p)
            print(f"  {CYAN}{dt}{RESET}  {DIM}{rel}{RESET}")

    except Exception as e:
        from colors import err
        err(f"oldnew error: {e}")


# ─── Directory Sync ───────────────────────────────────────────────────────────

def sync_dirs(src: str, dst: str):
    """Mirror src directory into dst — copy new/changed, report extras."""
    from colors import ok, err, warn, info, GREEN, YELLOW, CYAN, RESET

    try:
        sp = _safe(src)
        dp = _safe(dst)
    except Exception as e:
        from colors import err
        err(str(e))
        return

    if not os.path.isdir(sp):
        from colors import err
        err(f"Source is not a directory: {sp}")
        return

    os.makedirs(dp, exist_ok=True)
    copied = updated = skipped = 0

    for root, dirs, files in os.walk(sp):
        rel_root = os.path.relpath(root, sp)
        dst_root = os.path.join(dp, rel_root)
        os.makedirs(dst_root, exist_ok=True)

        for f in files:
            src_f = os.path.join(root, f)
            dst_f = os.path.join(dst_root, f)
            rel   = os.path.join(rel_root, f)

            try:
                if not os.path.exists(dst_f):
                    shutil.copy2(src_f, dst_f)
                    print(f"  {GREEN}+ {rel}{RESET}")
                    copied += 1
                elif os.path.getmtime(src_f) > os.path.getmtime(dst_f):
                    shutil.copy2(src_f, dst_f)
                    print(f"  {YELLOW}↻ {rel}{RESET}")
                    updated += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"  {CYAN}✖ {rel}: {e}{RESET}")

    print()
    ok(f"Sync complete — {copied} copied, {updated} updated, {skipped} unchanged.")


# ─── Password Strength Checker ────────────────────────────────────────────────

def passcheck(password: str):
    """Analyze password strength with detailed feedback."""
    from colors import ok, warn, err, info, GREEN, YELLOW, RED, CYAN, RESET, BOLD

    score   = 0
    tips    = []

    has_upper  = bool(re.search(r'[A-Z]', password))
    has_lower  = bool(re.search(r'[a-z]', password))
    has_digit  = bool(re.search(r'\d', password))
    has_symbol = bool(re.search(r'[!@#$%^&*(),.?":{}|<>\[\]\\/\-_=+`~]', password))
    length     = len(password)

    if length >= 16:  score += 3
    elif length >= 12: score += 2
    elif length >= 8:  score += 1
    else:              tips.append("Use at least 12 characters")

    if has_upper:  score += 1
    else:          tips.append("Add uppercase letters (A-Z)")
    if has_lower:  score += 1
    else:          tips.append("Add lowercase letters (a-z)")
    if has_digit:  score += 1
    else:          tips.append("Add numbers (0-9)")
    if has_symbol: score += 2
    else:          tips.append("Add special characters (!@#$%...)")

    # Common patterns
    common = ["password","123456","qwerty","abc","letmein","admin","welcome","login"]
    if any(c in password.lower() for c in common):
        score -= 3
        tips.append("Avoid common words/patterns")

    if re.search(r'(.)\1{2,}', password):
        score -= 1
        tips.append("Avoid repeated characters (aaa, 111)")

    score = max(0, min(score, 8))
    pct   = int(score / 8 * 100)

    if score >= 7:    label, col = "VERY STRONG 💪", GREEN
    elif score >= 5:  label, col = "STRONG ✓",       GREEN
    elif score >= 3:  label, col = "MODERATE ⚠",     YELLOW
    elif score >= 1:  label, col = "WEAK ✗",          RED
    else:             label, col = "VERY WEAK ✗✗",   RED

    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    masked = password[0] + "*" * (len(password) - 2) + password[-1] if len(password) > 2 else "**"

    print()
    info(f"Password: {masked}")
    print(f"  [{col}{bar}{RESET}] {col}{label}{RESET}  ({score}/8)")
    print(f"  Length   : {length} characters")
    print(f"  Uppercase: {'✓' if has_upper else '✗'}   Lowercase: {'✓' if has_lower else '✗'}   "
          f"Digits: {'✓' if has_digit else '✗'}   Symbols: {'✓' if has_symbol else '✗'}")

    if tips:
        print()
        warn("Suggestions:")
        for t in tips:
            print(f"    • {t}")

    # Entropy estimate
    charset = (26 if has_upper else 0) + (26 if has_lower else 0) + \
              (10 if has_digit else 0) + (32 if has_symbol else 0)
    if charset:
        entropy = length * math.log2(charset)
        print(f"\n  Entropy  : {entropy:.0f} bits  ({'strong' if entropy > 60 else 'weak'})")
    print()


# ─── Text Statistics ──────────────────────────────────────────────────────────

def textstats(filepath: str):
    """Deep text stats: chars, words, sentences, paragraphs, reading time."""
    from colors import info, err, CYAN, RESET, BOLD

    try:
        path = _safe(filepath)
        text = open(path, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        from colors import err
        err(f"textstats error: {e}")
        return

    chars       = len(text)
    chars_nsp   = len(text.replace(" ", "").replace("\n", ""))
    words       = len(re.findall(r'\b\w+\b', text))
    sentences   = max(1, len(re.findall(r'[.!?]+', text)))
    paragraphs  = len([p for p in text.split("\n\n") if p.strip()])
    lines       = text.count("\n") + 1
    avg_word    = sum(len(w) for w in re.findall(r'\b\w+\b', text)) / max(1, words)
    avg_sent    = words / sentences
    read_mins   = words / 200        # avg reading speed 200 wpm
    unique_w    = len(set(w.lower() for w in re.findall(r'\b[a-zA-Z]+\b', text)))

    info(f"Text Statistics: {filepath}")
    print()
    print(f"  {'Characters':<22} {chars:>10,}   (no spaces: {chars_nsp:,})")
    print(f"  {'Words':<22} {words:>10,}   (unique: {unique_w:,})")
    print(f"  {'Sentences':<22} {sentences:>10,}")
    print(f"  {'Paragraphs':<22} {paragraphs:>10,}")
    print(f"  {'Lines':<22} {lines:>10,}")
    print(f"  {'Avg word length':<22} {avg_word:>10.1f} chars")
    print(f"  {'Avg sentence length':<22} {avg_sent:>10.1f} words")
    print(f"  {'Est. reading time':<22} {CYAN}{read_mins:.1f} min{RESET} (at 200 wpm)")
    print()


# ─── URL Encode / Decode ──────────────────────────────────────────────────────

def urlencode(text: str):
    from colors import ok, CYAN, RESET
    result = urllib.parse.quote(text, safe="")
    print(f"  {CYAN}{result}{RESET}")
    try:
        import subprocess
        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{result}'"],
                       capture_output=True)
        ok("URL-encoded and copied to clipboard.")
    except Exception:
        ok("Done.")


def urldecode(text: str):
    from colors import ok, CYAN, RESET
    result = urllib.parse.unquote(text)
    print(f"  {CYAN}{result}{RESET}")
    try:
        import subprocess
        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{result}'"],
                       capture_output=True)
        ok("URL-decoded and copied to clipboard.")
    except Exception:
        ok("Done.")


# ─── Date/Time Tools ─────────────────────────────────────────────────────────

def datetools(action: str, arg1: str = "", arg2: str = ""):
    """Date and time utilities: now, diff, add, weekday, unix."""
    import datetime
    from colors import ok, err, info, warn, CYAN, RESET

    if action in ("now", ""):
        now = datetime.datetime.now()
        print(f"\n  {CYAN}{now.strftime('%A, %d %B %Y  %H:%M:%S')}{RESET}")
        print(f"  ISO    : {now.isoformat()}")
        print(f"  Unix   : {int(now.timestamp())}")
        print(f"  Week   : Week {now.isocalendar()[1]} of {now.year}")
        print(f"  Day    : Day {now.timetuple().tm_yday} of {now.year}")
        print()

    elif action == "diff":
        if not arg1 or not arg2:
            err("Usage: date diff YYYY-MM-DD YYYY-MM-DD")
            return
        try:
            d1 = datetime.datetime.strptime(arg1, "%Y-%m-%d")
            d2 = datetime.datetime.strptime(arg2, "%Y-%m-%d")
            delta = abs(d2 - d1)
            ok(f"Between {arg1} and {arg2}:")
            print(f"  {CYAN}{delta.days}{RESET} days  /  {CYAN}{delta.days // 7}{RESET} weeks  /  {CYAN}{delta.days / 365.25:.2f}{RESET} years")
        except ValueError:
            err("Date format must be YYYY-MM-DD")

    elif action == "add":
        if not arg1 or not arg2:
            err("Usage: date add YYYY-MM-DD <+/-N> (N in days)")
            return
        try:
            d = datetime.datetime.strptime(arg1, "%Y-%m-%d")
            n = int(arg2)
            result = d + datetime.timedelta(days=n)
            ok(f"{arg1} + {n} days = {CYAN}{result.strftime('%Y-%m-%d (%A)')}{RESET}")
        except ValueError:
            err("Usage: date add YYYY-MM-DD <days>")

    elif action == "weekday":
        if not arg1:
            err("Usage: date weekday YYYY-MM-DD")
            return
        try:
            d = datetime.datetime.strptime(arg1, "%Y-%m-%d")
            ok(f"{arg1} is a {CYAN}{d.strftime('%A')}{RESET}  (week {d.isocalendar()[1]})")
        except ValueError:
            err("Date format must be YYYY-MM-DD")

    elif action == "unix":
        if not arg1:
            ok(f"Current Unix timestamp: {CYAN}{int(datetime.datetime.now().timestamp())}{RESET}")
        else:
            try:
                dt = datetime.datetime.fromtimestamp(int(arg1))
                ok(f"Unix {arg1} = {CYAN}{dt.strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
            except Exception:
                err(f"Invalid Unix timestamp: {arg1}")
    else:
        err("Usage: date now | date diff D1 D2 | date add D N | date weekday D | date unix [ts]")


# ─── Pomodoro Timer ──────────────────────────────────────────────────────────

def pomodoro(work_min: int = 25, break_min: int = 5, cycles: int = 4):
    """Pomodoro productivity timer with desktop notifications."""
    import subprocess
    from colors import ok, info, warn, BOLD, GREEN, YELLOW, RED, CYAN, RESET

    def _notify(title, msg):
        try:
            subprocess.Popen(
                ["powershell", "-Command",
                 f"Add-Type -AssemblyName System.Windows.Forms; "
                 f"$n = New-Object System.Windows.Forms.NotifyIcon; "
                 f"$n.Icon = [System.Drawing.SystemIcons]::Information; "
                 f"$n.Visible = $true; "
                 f"$n.ShowBalloonTip(8000, '{title}', '{msg}', "
                 f"[System.Windows.Forms.ToolTipIcon]::Info); "
                 f"Start-Sleep -Seconds 9; $n.Dispose()"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

    print()
    info(f"Pomodoro  —  {work_min}m work / {break_min}m break / {cycles} cycles")
    info("Press Ctrl+C to stop.")
    print()

    try:
        for cycle in range(1, cycles + 1):
            # Work phase
            print(f"  {GREEN}● CYCLE {cycle}/{cycles}  —  Work for {work_min} min{RESET}")
            _notify("🍅 Work Time!", f"Cycle {cycle}/{cycles} — Focus for {work_min} minutes!")
            total = work_min * 60
            for remaining in range(total, 0, -1):
                m, s = divmod(remaining, 60)
                bar  = "█" * int((total - remaining) / total * 20) + "░" * int(remaining / total * 20)
                print(f"\r  [{GREEN}{bar}{RESET}] {m:02d}:{s:02d} remaining  ", end="", flush=True)
                time.sleep(1)
            print()

            if cycle < cycles:
                # Break phase
                print(f"\n  {YELLOW}☕ Break time — {break_min} min{RESET}")
                _notify("☕ Break!", f"Good work! Take a {break_min}-minute break.")
                btotal = break_min * 60
                for remaining in range(btotal, 0, -1):
                    m, s = divmod(remaining, 60)
                    bar  = "█" * int((btotal - remaining) / btotal * 20) + "░" * int(remaining / btotal * 20)
                    print(f"\r  [{YELLOW}{bar}{RESET}] {m:02d}:{s:02d} break  ", end="", flush=True)
                    time.sleep(1)
                print("\n")

        print()
        ok(f"🎉 Pomodoro complete! {cycles} cycles done.")
        _notify("🎉 Done!", f"All {cycles} Pomodoro cycles complete!")

    except KeyboardInterrupt:
        print()
        warn("Pomodoro stopped.")


# ─── Currency Converter ───────────────────────────────────────────────────────

def currency(amount: str, from_cur: str, to_cur: str):
    """Convert between currencies using free exchange rate API."""
    from colors import ok, err, warn, CYAN, RESET

    try:
        amt = float(amount)
    except ValueError:
        from colors import err
        err(f"Invalid amount: {amount}")
        return

    f = from_cur.upper()
    t = to_cur.upper()

    try:
        url = f"https://open.er-api.com/v6/latest/{f}"
        req = urllib.request.Request(url, headers={"User-Agent": "SystemCommander/2.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())

        if data.get("result") != "success":
            from colors import err
            err(f"API error: {data.get('error-type', 'unknown')}")
            return

        rates = data.get("rates", {})
        if t not in rates:
            from colors import err
            err(f"Unknown currency: {t}. Try codes like USD, EUR, INR, GBP, JPY")
            return

        rate   = rates[t]
        result = amt * rate
        ok(f"{amt:,.2f} {f} = {CYAN}{result:,.2f} {t}{RESET}")
        print(f"  Rate: 1 {f} = {rate:.4f} {t}")
        print(f"  Date: {data.get('time_last_update_utc', 'N/A')[:16]}")

    except urllib.error.URLError:
        from colors import err
        err("Could not reach exchange rate API — check your connection.")
    except Exception as e:
        from colors import err
        err(f"currency error: {e}")


# ─── JSON Validator ───────────────────────────────────────────────────────────

def jsoncheck(filepath: str):
    """Validate a JSON file and show a helpful error if invalid."""
    from colors import ok, err, info, warn, CYAN, RED, GREEN, RESET

    try:
        path = _safe(filepath)
        content = open(path, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        err(f"Cannot read file: {e}")
        return

    try:
        data = json.loads(content)
        lines = content.count("\n") + 1
        size  = len(content)

        # Detect structure
        if isinstance(data, list):
            structure = f"Array of {len(data)} items"
        elif isinstance(data, dict):
            structure = f"Object with {len(data)} keys: {', '.join(list(data.keys())[:5])}"
        else:
            structure = type(data).__name__

        ok(f"Valid JSON  ✓")
        print(f"  File     : {path}")
        print(f"  Size     : {size:,} bytes,  {lines} lines")
        print(f"  Structure: {structure}")

    except json.JSONDecodeError as e:
        err(f"Invalid JSON!")
        print(f"  Error   : {e.msg}")
        print(f"  Line    : {e.lineno},  Column: {e.colno}")

        # Show the bad line with a pointer
        lines = content.splitlines()
        if 0 < e.lineno <= len(lines):
            bad_line = lines[e.lineno - 1]
            print(f"\n  {e.lineno:4} │ {RED}{bad_line}{RESET}")
            print(f"       │ {' ' * max(0, e.colno - 1)}{RED}^{RESET} error here")
