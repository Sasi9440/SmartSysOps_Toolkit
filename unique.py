# -*- coding: utf-8 -*-
"""
unique.py  —  Distinctive features for System Commander
  matrix, banner, typetest, journal, habit,
  sysreport, joke, fact, brain, dircompare
"""

import os, sys, json, time, random, math, difflib
import urllib.request, urllib.error
import datetime, shutil, threading, re

BASE = "D:\\"
_DATA = "D:\\sc_data.json"   # shared data store for journal & habits


def _safe(path):
    path = os.path.splitdrive(path)[1].lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        raise PermissionError("Access restricted to D: drive only.")
    return full


def _load_data() -> dict:
    if os.path.exists(_DATA):
        try:
            return json.loads(open(_DATA, encoding="utf-8").read())
        except Exception:
            pass
    return {"journal": {}, "habits": {}}


def _save_data(d: dict):
    with open(_DATA, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


# ─── Matrix Digital Rain ──────────────────────────────────────────────────────

def matrix():
    """Matrix-style digital rain. Press Ctrl+C to stop."""
    from colors import warn
    try:
        W = shutil.get_terminal_size((80, 24)).columns
    except Exception:
        W = 80

    CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789"
    GREEN  = "\033[32m"
    BGREEN = "\033[92m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

    drops   = [0] * W
    speeds  = [random.randint(1, 3) for _ in range(W)]
    lengths = [random.randint(5, 20) for _ in range(W)]

    print("\033[?25l", end="")   # hide cursor
    print("\033[2J", end="")     # clear screen

    try:
        tick = 0
        while True:
            tick += 1
            for col in range(W):
                if tick % speeds[col] != 0:
                    continue
                row = drops[col]
                char = random.choice(CHARS)

                # bright head character
                print(f"\033[{row};{col+1}H{BGREEN}{char}{RESET}", end="")
                # dim trail
                trail_row = row - 1
                if trail_row > 0:
                    print(f"\033[{trail_row};{col+1}H{DIM}{GREEN}{random.choice(CHARS)}{RESET}", end="")
                # erase tail
                erase_row = row - lengths[col]
                if erase_row > 0:
                    print(f"\033[{erase_row};{col+1}H ", end="")

                drops[col] += 1
                if drops[col] > 35 + random.randint(0, 10):
                    drops[col]   = random.randint(-10, 0)
                    lengths[col] = random.randint(5, 22)

            sys.stdout.flush()
            time.sleep(0.045)

    except KeyboardInterrupt:
        print("\033[?25h", end="")   # restore cursor
        print("\033[2J\033[H", end="")
        warn("Matrix stopped.")


# ─── ASCII Big Banner ─────────────────────────────────────────────────────────

_FONT = {
    'A':["▄▀█","█▀█"],  'B':["█▄▄","█▄█"],  'C':["█▀▀","█▄▄"],
    'D':["█▀▄","█▄▀"],  'E':["█▀▀","██▄"],  'F':["█▀▀","█▀ "],
    'G':["█▀▀","█▄█"],  'H':["█ █","███"],  'I':["█","█"],
    'J':["  █","█▄█"],  'K':["█▀▄","█▄▀"],  'L':["█  ","███"],
    'M':["█▄█","█ █"],  'N':["█▄ ","█ █"],  'O':["█▀█","█▄█"],
    'P':["█▀█","█▀ "],  'Q':["█▀█","█▄█"],  'R':["█▀▄","█▄▀"],
    'S':["▄▀▀","▄▄▀"],  'T':["▀█▀","  █"],  'U':["█ █","█▄█"],
    'V':["█ █","▀▄▀"],  'W':["█ █","█▄█"],  'X':["▀▄▀","▄▀▄"],
    'Y':["▀▄▀","  █"],  'Z':["▀▀█","█▄▄"],
    '0':["█▀█","█▄█"],  '1':["▀█","▄█"],   '2':["▀▀█","█▄▄"],
    '3':["▀▀█","▄▄█"],  '4':["█▄█","  █"],  '5':["█▀▀","▄▄█"],
    '6':["█▀ ","███"],  '7':["▀▀█","  █"],  '8':["█▀█","█▄█"],
    '9':["█▀█","▀▄█"],
    ' ':["  ","  "],   '!':["█","▄"],      '?':["▀▀█","  ▄"],
    '.':["  "," ▄"],   '-':["   ","▄▄▄"],
}

def banner(text: str, color: str = "cyan"):
    """Print text as a large 2-row ASCII banner."""
    from colors import CYAN, GREEN, YELLOW, MAGENTA, RED, RESET, BOLD

    color_map = {"cyan": CYAN, "green": GREEN, "yellow": YELLOW,
                 "magenta": MAGENTA, "red": RED}
    col = color_map.get(color.lower(), CYAN)

    text = text.upper()
    row1 = ""
    row2 = ""
    for ch in text:
        if ch in _FONT:
            r = _FONT[ch]
            row1 += r[0] + "  "
            row2 += r[1] + "  "
        else:
            row1 += "?  "
            row2 += "?  "

    print(f"\n  {BOLD}{col}{row1}{RESET}")
    print(f"  {BOLD}{col}{row2}{RESET}\n")


# ─── Typing Speed Test ────────────────────────────────────────────────────────

_SENTENCES = [
    "The quick brown fox jumps over the lazy dog",
    "Pack my box with five dozen liquor jugs",
    "How vexingly quick daft zebras jump",
    "The five boxing wizards jump quickly",
    "Bright vixens jump dozy fowl quack",
    "Sphinx of black quartz judge my vow",
    "System Commander is the best CLI tool ever built",
    "Programming is thinking not typing",
    "Every line of code is a decision made under uncertainty",
    "First solve the problem then write the code",
]

def typetest():
    """Typing speed test — measure your WPM with accuracy score."""
    from colors import ok, info, warn, CYAN, GREEN, YELLOW, RED, RESET, BOLD

    sentence = random.choice(_SENTENCES)
    info("Type the following sentence exactly:")
    print(f"\n  {BOLD}{CYAN}{sentence}{RESET}\n")
    print("  Press ENTER when done (timer starts now):\n  ", end="", flush=True)

    start = time.time()
    typed = input()
    elapsed = time.time() - start

    words   = len(sentence.split())
    wpm     = (words / elapsed) * 60

    # Accuracy
    correct = sum(1 for a, b in zip(typed, sentence) if a == b)
    total   = max(len(sentence), len(typed))
    acc     = correct / total * 100

    # Colour-code result
    wpm_c = GREEN if wpm >= 60 else YELLOW if wpm >= 40 else RED
    acc_c = GREEN if acc >= 95 else YELLOW if acc >= 80 else RED

    print()
    print(f"  {BOLD}WPM      :{RESET} {wpm_c}{wpm:.0f} words/min{RESET}")
    print(f"  {BOLD}Accuracy :{RESET} {acc_c}{acc:.1f}%{RESET}")
    print(f"  {BOLD}Time     :{RESET} {elapsed:.2f} seconds")

    grade = "S" if wpm >= 80 and acc >= 97 else \
            "A" if wpm >= 60 and acc >= 93 else \
            "B" if wpm >= 45 and acc >= 85 else \
            "C" if wpm >= 30 else "D"

    grade_c = GREEN if grade in ("S","A") else YELLOW if grade == "B" else RED
    print(f"  {BOLD}Grade    :{RESET} {grade_c}{grade}{RESET}\n")


# ─── Daily Journal ────────────────────────────────────────────────────────────

def journal(action: str = "list", text: str = ""):
    """Dated daily journal — add entries, list, or search."""
    from colors import ok, info, warn, err, CYAN, GREEN, YELLOW, RESET, BOLD, DIM

    data = _load_data()
    jnl  = data.setdefault("journal", {})
    today = datetime.date.today().isoformat()

    if action == "add":
        if not text:
            from colors import err
            err("Usage: journal add <your entry text>")
            return
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
        if today not in jnl:
            jnl[today] = []
        jnl[today].append({"time": stamp, "entry": text})
        _save_data(data)
        ok(f"Journal entry saved for {today} at {stamp}")

    elif action in ("list", "show"):
        if not jnl:
            warn("No journal entries yet.  Use: journal add <text>")
            return
        days = sorted(jnl.keys(), reverse=True)[:7]   # last 7 days
        info(f"Journal — last {len(days)} days")
        for day in days:
            print(f"\n  {BOLD}{CYAN}{day}{RESET}")
            for e in jnl[day]:
                print(f"    {DIM}{e['time']}{RESET}  {e['entry']}")

    elif action == "search":
        if not text:
            from colors import err
            err("Usage: journal search <keyword>")
            return
        hits = 0
        for day, entries in sorted(jnl.items(), reverse=True):
            for e in entries:
                if text.lower() in e["entry"].lower():
                    if hits == 0:
                        info(f"Journal search: '{text}'")
                    print(f"  {CYAN}{day}{RESET} {DIM}{e['time']}{RESET}  {e['entry']}")
                    hits += 1
        if hits == 0:
            warn(f"No entries containing '{text}'.")
        else:
            ok(f"{hits} match(es) found.")

    elif action == "clear":
        jnl.clear()
        _save_data(data)
        ok("Journal cleared.")

    else:
        from colors import err
        err("Usage: journal add <text> | journal list | journal search <kw> | journal clear")


# ─── Habit Tracker ────────────────────────────────────────────────────────────

def habit(action: str = "list", name: str = ""):
    """Track daily habits with streaks."""
    from colors import ok, info, warn, err, CYAN, GREEN, YELLOW, RED, RESET, BOLD, DIM

    data  = _load_data()
    habits = data.setdefault("habits", {})
    today  = datetime.date.today().isoformat()

    if action == "add":
        if not name:
            err("Usage: habit add <name>")
            return
        if name in habits:
            warn(f"Habit '{name}' already exists.")
            return
        habits[name] = {"created": today, "done": []}
        _save_data(data)
        ok(f"Habit '{name}' added.")

    elif action == "done":
        if not name:
            err("Usage: habit done <name>")
            return
        if name not in habits:
            err(f"Habit '{name}' not found.")
            return
        if today in habits[name]["done"]:
            warn(f"'{name}' already marked done today!")
            return
        habits[name]["done"].append(today)
        _save_data(data)
        # Calculate streak
        streak = _calc_streak(habits[name]["done"])
        ok(f"'{name}' marked done for today!  🔥 Streak: {streak} day(s)")

    elif action in ("list", ""):
        if not habits:
            warn("No habits tracked yet.  Use: habit add <name>")
            return
        info(f"Habit Tracker — {today}")
        print(f"\n  {'HABIT':<24} {'STREAK':>8}  {'TODAY':>6}  TOTAL DONE")
        print(f"  {'─'*24} {'─'*8}  {'─'*6}  {'─'*10}")
        for h, d in habits.items():
            streak = _calc_streak(d["done"])
            done_today = "✓" if today in d["done"] else "○"
            total  = len(d["done"])
            sc = GREEN if today in d["done"] else YELLOW
            print(f"  {CYAN}{h:<24}{RESET} {sc}{streak:>8}🔥{RESET}  {sc}{done_today:>6}{RESET}  {total:>10}")
        print()

    elif action == "remove":
        if not name:
            err("Usage: habit remove <name>")
            return
        if name not in habits:
            err(f"Habit '{name}' not found.")
            return
        del habits[name]
        _save_data(data)
        ok(f"Habit '{name}' removed.")

    else:
        from colors import err
        err("Usage: habit add|done|list|remove <name>")


def _calc_streak(done_list: list) -> int:
    """Calculate current consecutive-day streak."""
    if not done_list:
        return 0
    dates = sorted(set(done_list), reverse=True)
    today = datetime.date.today()
    streak = 0
    for i, d in enumerate(dates):
        dt = datetime.date.fromisoformat(d)
        if dt == today - datetime.timedelta(days=i):
            streak += 1
        else:
            break
    return streak


# ─── System Report Export ─────────────────────────────────────────────────────

def sysreport():
    """Export a full system report to a timestamped .txt file on D:\\."""
    from colors import ok, err, info
    import platform, socket

    try:
        import psutil
    except ImportError:
        err("psutil required.  Run: pip install psutil")
        return

    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BASE, f"sysreport_{ts}.txt")

    lines = []
    def w(*args): lines.append(" ".join(str(a) for a in args))

    w("=" * 60)
    w("  SYSTEM COMMANDER — SYSTEM REPORT")
    w(f"  Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    w("=" * 60)
    w()
    w("SYSTEM")
    w(f"  OS          : {platform.system()} {platform.release()} ({platform.version()})")
    w(f"  Machine     : {platform.machine()}")
    w(f"  Processor   : {platform.processor()}")
    w(f"  Hostname    : {socket.gethostname()}")
    try:
        w(f"  Local IP    : {socket.gethostbyname(socket.gethostname())}")
    except Exception: pass
    w()
    w("CPU")
    w(f"  Physical    : {psutil.cpu_count(logical=False)} cores")
    w(f"  Logical     : {psutil.cpu_count()} threads")
    w(f"  Usage       : {psutil.cpu_percent(interval=1):.1f}%")
    w()
    ram = psutil.virtual_memory()
    w("MEMORY")
    w(f"  Total       : {ram.total//1024**3:.1f} GB")
    w(f"  Used        : {ram.used//1024**2} MB  ({ram.percent:.1f}%)")
    w(f"  Free        : {ram.available//1024**2} MB")
    w()
    w("DISK (D:\\)")
    total, used, free = shutil.disk_usage("D:\\")
    w(f"  Total       : {total//1024**3:.1f} GB")
    w(f"  Used        : {used//1024**3:.1f} GB  ({used/total*100:.1f}%)")
    w(f"  Free        : {free//1024**3:.1f} GB")
    w()
    try:
        bat = psutil.sensors_battery()
        if bat:
            w("BATTERY")
            w(f"  Level       : {bat.percent:.0f}%")
            w(f"  Status      : {'Charging' if bat.power_plugged else 'On battery'}")
            w()
    except Exception: pass
    w("TOP PROCESSES")
    w(f"  {'PID':>6}  {'CPU%':>5}  {'MEM%':>5}  NAME")
    procs = []
    for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
        try:
            inf = p.info
            if inf['name'] and 'idle' not in inf['name'].lower():
                inf['cpu_percent'] = min(inf['cpu_percent'], 100.0)
                procs.append(inf)
        except Exception: pass
    procs.sort(key=lambda x: x['cpu_percent'], reverse=True)
    for p in procs[:10]:
        w(f"  {p['pid']:>6}  {p['cpu_percent']:>5.1f}  {p['memory_percent']:>5.1f}  {p['name']}")
    w()
    w("=" * 60)

    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    ok(f"System report saved: {dest}")


# ─── Random Joke ──────────────────────────────────────────────────────────────

def joke():
    """Fetch a random joke."""
    from colors import ok, err, CYAN, RESET, DIM

    try:
        req = urllib.request.Request(
            "https://icanhazdadjoke.com/",
            headers={"Accept": "application/json", "User-Agent": "SystemCommander/2.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
        j = data.get("joke", "")
        print(f"\n  {CYAN}{j}{RESET}\n")
    except Exception:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
            "Why do Java developers wear glasses? Because they don't C#.",
            "How many programmers does it take to change a light bulb? None — that's a hardware problem.",
            "I would tell you a UDP joke, but you might not get it.",
            "There are 10 types of people: those who understand binary and those who don't.",
        ]
        print(f"\n  {CYAN}{random.choice(jokes)}{RESET}\n")


# ─── Random Fact ──────────────────────────────────────────────────────────────

def fact():
    """Fetch a random interesting fact."""
    from colors import ok, err, CYAN, RESET, DIM

    try:
        req = urllib.request.Request(
            "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en",
            headers={"User-Agent": "SystemCommander/2.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
        f = data.get("text", "")
        print(f"\n  {CYAN}{f}{RESET}\n")
    except Exception:
        facts = [
            "A group of flamingos is called a flamboyance.",
            "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs still perfectly edible.",
            "The word 'nerd' was first coined by Dr. Seuss in 'If I Ran the Zoo' in 1950.",
            "The first computer bug was an actual real bug — a moth found in a Harvard Mark II computer in 1947.",
            "There are more possible iterations of a game of chess than there are atoms in the universe.",
            "Python was named after Monty Python, not the snake.",
        ]
        print(f"\n  {CYAN}{random.choice(facts)}{RESET}\n")


# ─── Mental Math Quiz ─────────────────────────────────────────────────────────

def brain(rounds: int = 10):
    """Mental math quiz — test your arithmetic speed."""
    from colors import ok, info, warn, GREEN, YELLOW, RED, CYAN, RESET, BOLD

    ops   = [('+', lambda a, b: a + b),
             ('-', lambda a, b: a - b),
             ('×', lambda a, b: a * b)]
    score = 0
    times = []

    info(f"Mental Math Quiz — {rounds} rounds.  Type the answer and press ENTER.")
    print()

    for i in range(1, rounds + 1):
        op_sym, op_fn = random.choice(ops)
        if op_sym == '×':
            a, b = random.randint(2, 12), random.randint(2, 12)
        else:
            a, b = random.randint(10, 99), random.randint(10, 99)
            if op_sym == '-' and b > a:
                a, b = b, a

        answer = op_fn(a, b)

        print(f"  {BOLD}[{i}/{rounds}]{RESET}  {CYAN}{a} {op_sym} {b} = ?{RESET}  ", end="", flush=True)
        t0 = time.time()
        try:
            raw = input().strip()
        except KeyboardInterrupt:
            print()
            warn("Quiz stopped.")
            return
        elapsed = time.time() - t0

        try:
            guess = int(raw)
        except ValueError:
            print(f"         {RED}✗  (not a number — answer was {answer}){RESET}")
            continue

        if guess == answer:
            t_col = GREEN if elapsed < 5 else YELLOW
            print(f"         {GREEN}✓  correct!{RESET}  {t_col}{elapsed:.1f}s{RESET}")
            score += 1
            times.append(elapsed)
        else:
            print(f"         {RED}✗  wrong  (correct: {answer}){RESET}")

    print()
    pct   = score / rounds * 100
    avg_t = sum(times) / len(times) if times else 0
    sc    = GREEN if pct >= 80 else YELLOW if pct >= 60 else RED
    print(f"  {BOLD}Score:{RESET}   {sc}{score}/{rounds}  ({pct:.0f}%){RESET}")
    print(f"  {BOLD}Avg time:{RESET} {avg_t:.1f}s per correct answer\n")


# ─── Directory Comparison ─────────────────────────────────────────────────────

def dircompare(dir1: str, dir2: str):
    """Compare two directories — show added, removed, changed files."""
    from colors import info, ok, warn, GREEN, RED, YELLOW, CYAN, RESET

    try:
        d1 = _safe(dir1)
        d2 = _safe(dir2)
    except Exception as e:
        from colors import err
        err(str(e))
        return

    if not os.path.isdir(d1):
        from colors import err; err(f"Not a directory: {d1}"); return
    if not os.path.isdir(d2):
        from colors import err; err(f"Not a directory: {d2}"); return

    def get_files(base):
        result = {}
        for root, _, files in os.walk(base):
            for f in files:
                fp  = os.path.join(root, f)
                rel = os.path.relpath(fp, base)
                try:
                    result[rel] = os.path.getmtime(fp)
                except Exception:
                    result[rel] = 0
        return result

    files1 = get_files(d1)
    files2 = get_files(d2)

    only_in_1  = set(files1) - set(files2)
    only_in_2  = set(files2) - set(files1)
    in_both    = set(files1) & set(files2)
    changed    = {f for f in in_both if abs(files1[f] - files2[f]) > 1}
    identical  = in_both - changed

    info(f"Directory Compare:  {dir1}  ←→  {dir2}")
    print(f"\n  {'─'*54}")
    print(f"  {GREEN}+ Only in {dir1:<20}{RESET} ({len(only_in_1)} files)")
    for f in sorted(only_in_1)[:15]:
        print(f"    {GREEN}+ {f}{RESET}")
    if len(only_in_1) > 15: print(f"    {GREEN}... and {len(only_in_1)-15} more{RESET}")

    print(f"\n  {RED}- Only in {dir2:<20}{RESET} ({len(only_in_2)} files)")
    for f in sorted(only_in_2)[:15]:
        print(f"    {RED}- {f}{RESET}")
    if len(only_in_2) > 15: print(f"    {RED}... and {len(only_in_2)-15} more{RESET}")

    print(f"\n  {YELLOW}≠ Modified{RESET} ({len(changed)} files)")
    for f in sorted(changed)[:15]:
        print(f"    {YELLOW}≠ {f}{RESET}")
    if len(changed) > 15: print(f"    {YELLOW}... and {len(changed)-15} more{RESET}")

    print(f"\n  = Identical: {len(identical)} files")
    print(f"  {'─'*54}")
    print(f"\n  Total: {len(files1)} ↔ {len(files2)} files\n")
