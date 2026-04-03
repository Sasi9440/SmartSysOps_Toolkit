# -*- coding: utf-8 -*-
"""
ultra_unique.py  —  Extremely unique, stand-out features for System Commander
qrgen, hacker, lifegrid, stegohide, stegoextract, biorhythm, sysmap, stock, moonphase, morse
"""

import os
import sys
import time
import math
import random
import datetime
import urllib.request
import urllib.parse
import json
import base64

from colors import info, ok, err, warn, GREEN, RED, YELLOW, CYAN, BOLD, DIM, RESET
from unique import _safe

# ─── 1. Terminal QR Code Generator ────────────────────────────────────────────

def qrgen(text: str):
    """Generate a terminal-ready ASCII QR code."""
    try:
        url = f"https://qrenco.de/{urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.64.1"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            ascii_qr = resp.read().decode('utf-8')
        info(f"QR Code for: {text}")
        print(f"\n{ascii_qr}\n")
    except Exception as e:
        err(f"QR generation failed: {e}")


# ─── 2. Hollywood Hacker Animation ────────────────────────────────────────────

def hacker(text: str):
    """Decrypts text character by character like a hacking movie."""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    print()
    sys.stdout.write("\033[?25l")  # hide cursor
    try:
        for i in range(len(text)):
            # Random loops before settling on the correct character
            for _ in range(5 + min(i, 8)):
                tail = ''.join(random.choice(chars) for _ in range(len(text) - i - 1))
                random_char = random.choice(chars) if i < len(text) else ""
                sys.stdout.write(f"\r  {GREEN}{text[:i]}{random_char}{tail}{RESET}")
                sys.stdout.flush()
                time.sleep(0.015)
        sys.stdout.write(f"\r  {GREEN}{text}{RESET}\n\n")
    except KeyboardInterrupt:
        sys.stdout.write(f"\r  {GREEN}{text}{RESET}\n\n")
    finally:
        sys.stdout.write("\033[?25h")  # show cursor
        sys.stdout.flush()


# ─── 3. 90-Year Life Grid (Memento Mori) ──────────────────────────────────────

def lifegrid(dob: str):
    """Generates a visual 90-year grid of weeks showing lived vs remaining life."""
    try:
        birth = datetime.datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        err("Format must be YYYY-MM-DD")
        return
    
    now = datetime.datetime.now()
    age_days = (now - birth).days
    if age_days < 0:
        err("Birth date is in the future!")
        return

    weeks_lived = int(age_days / 7)
    total_weeks = 90 * 52

    info(f"Memento Mori - 90 Year Life Grid (Birth: {dob})")
    print(f"\n  {BOLD}{RED}█{RESET} Lived     : {weeks_lived} weeks")
    print(f"  {BOLD}{GREEN}░{RESET} Remaining : {total_weeks - weeks_lived} weeks (out of 90 years)\n")

    grid = []
    for y in range(90):
        row = ""
        for w in range(52):
            idx = y * 52 + w
            if idx < weeks_lived:
                row += f"{RED}█{RESET}"
            else:
                row += f"{GREEN}░{RESET}"
        grid.append(row)
    
    for y, r in enumerate(grid):
        if y % 10 == 0:
            print(f"  {DIM}{y:02d} yrs{RESET} | " + r)
        else:
            print(f"         | " + r)
    print()


# ─── 4 & 5. Steganography (Hide text in ANY file) ─────────────────────────

_STEGO_MARKER = b"::SC_STEGO::"

def stegohide(filepath: str, message: str):
    """Hide a secret message seamlessly at the end of a file."""
    try:
        path = _safe(filepath)
        payload = base64.b64encode(message.encode("utf-8"))
        with open(path, "ab") as f:
            f.write(_STEGO_MARKER + payload)
        ok(f"Secret message hidden seamlessly inside {path}")
        print(f"  {DIM}(File size increased by {len(_STEGO_MARKER) + len(payload)} bytes){RESET}")
    except Exception as e:
        err(f"stegohide failed: {e}")

def stegoextract(filepath: str):
    """Extract a hidden message from a file."""
    try:
        path = _safe(filepath)
        with open(path, "rb") as f:
            content = f.read()
        
        idx = content.rfind(_STEGO_MARKER)
        if idx == -1:
            err("No secret message found in this file.")
            return
            
        payload = content[idx + len(_STEGO_MARKER):]
        msg = base64.b64decode(payload).decode("utf-8")
        info("Secret message extracted from file:")
        print(f"\n  {CYAN}{msg}{RESET}\n")
    except Exception as e:
        err(f"stegoextract failed: {e}")


# ─── 6. Biorhythm Cycles ──────────────────────────────────────────────────────

def biorhythm(dob: str):
    """Physical, Emotional, and Intellectual body cycles calculation."""
    try:
        birth = datetime.datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        err("Format must be YYYY-MM-DD")
        return
    
    days = (datetime.datetime.now() - birth).days
    
    physical = math.sin(2 * math.pi * days / 23) * 100
    emotional = math.sin(2 * math.pi * days / 28) * 100
    intellectual = math.sin(2 * math.pi * days / 33) * 100

    def get_color(val):
        if val > 30: return GREEN
        elif val < -30: return RED
        return YELLOW

    info(f"Biorhythm Cycles (Age: {days} days)")
    print()
    print(f"  Physical     : {get_color(physical)}{physical:>6.1f}%{RESET}  (23-day cycle - strength, endurance)")
    print(f"  Emotional    : {get_color(emotional)}{emotional:>6.1f}%{RESET}  (28-day cycle - mood, creativity)")
    print(f"  Intellectual : {get_color(intellectual)}{intellectual:>6.1f}%{RESET}  (33-day cycle - logic, memory)")
    print()


# ─── 7. Visual Directory Size Map ─────────────────────────────────────────────

def sysmap(path: str = "."):
    """Graphically displays distribution of folder sizes."""
    try:
        p = _safe(path)
    except Exception as e:
        err(str(e))
        return

    dirs = []
    print(f"  {DIM}Analyzing sizes...{RESET}")
    for d in os.listdir(p):
        dp = os.path.join(p, d)
        if os.path.isdir(dp):
            try:
                sz = sum(os.path.getsize(os.path.join(root, f)) 
                         for root, _, files in os.walk(dp) for f in files)
                if sz > 0:
                    dirs.append((sz, d))
            except Exception:
                pass
                
    dirs.sort(reverse=True)
    if not dirs:
        warn("No subdirectories with size found.")
        return
    
    max_sz = dirs[0][0]
    info(f"Directory Map (Size Distribution) for {p}")
    print()
    for sz, name in dirs[:20]:
        sz_mb = sz / (1024*1024)
        pct = sz / max_sz
        bar_len = int(pct * 40)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"  {CYAN}{bar}{RESET} {sz_mb:8.1f} MB  {name}")
    print()


# ─── 8. Real-time Stock Data ──────────────────────────────────────────────────

def stock(symbol: str):
    """Fetch current stock or crypto price using Yahoo Finance."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}?interval=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            
        meta = data['chart']['result'][0]['meta']
        price = meta['regularMarketPrice']
        prev_close = meta['chartPreviousClose']
        diff = price - prev_close
        pct = (diff / prev_close) * 100
        
        c = GREEN if diff >= 0 else RED
        sign = "+" if diff >= 0 else ""
        
        info(f"Market Data for {symbol.upper()}")
        print(f"\n  Current Price : {BOLD}{c}{price:,.2f} {meta['currency']}{RESET}")
        print(f"  Day Change    : {c}{sign}{diff:,.2f} ({sign}{pct:.2f}%){RESET}")
        print(f"  Exchange      : {meta['exchangeName']}")
        print()
    except Exception as e:
        err(f"Could not fetch market data for '{symbol}'. (Check symbol / network)")


# ─── 9. Moon Phase Calculator ─────────────────────────────────────────────────

def moonphase():
    """Calculates and displays the current phase of the moon."""
    # Known new moon reference
    new_moon = datetime.datetime(2000, 1, 6)
    now = datetime.datetime.now()
    diff = now - new_moon
    days = diff.days + (diff.seconds / 86400.0)
    cycle = 29.53058867
    phase = (days % cycle) / cycle
    
    phases = [
        "New Moon 🌑", "Waxing Crescent 🌒", "First Quarter 🌓", "Waxing Gibbous 🌔", 
        "Full Moon 🌕", "Waning Gibbous 🌖", "Last Quarter 🌗", "Waning Crescent 🌘"
    ]
    
    idx = int(math.floor(phase * 8 + 0.5)) % 8
    
    info("Astrology & Space")
    print(f"\n  Current Moon Phase : {CYAN}{phases[idx]}{RESET}")
    print(f"  Cycle progression  : {phase*100:.1f}%")
    print(f"  Age (days)         : {(days % cycle):.1f} days into cycle\n")


# ─── 10. Text to Audio Morse Code ─────────────────────────────────────────────

def morse(text: str):
    """Converts string to morse code and actually plays the beeps."""
    try:
        import winsound
    except ImportError:
        err("Audio morse code requires Windows.")
        return
        
    MORSE_CODE = {
        'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 
        'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---', 
        'K':'-.-', 'L':'.-..', 'M':'--', 'N':'-.', 'O':'---', 
        'P':'.--.', 'Q':'--.-', 'R':'.-.', 'S':'...', 'T':'-', 
        'U':'..-', 'V':'...-', 'W':'.--', 'X':'-..-', 'Y':'-.--', 
        'Z':'--..', '1':'.----', '2':'..---', '3':'...--', 
        '4':'....-', '5':'.....', '6':'-....', '7':'--...', 
        '8':'---..', '9':'----.', '0':'-----', ', ':'--..--', 
        '.':'.-.-.-', '?':'..--..', '/':'-..-.', '-':'-....-', 
        '(':'-.--.', ')':'-.--.-', ' ':' '
    }
    
    text = text.upper()
    morse_string = ""
    for char in text:
        if char in MORSE_CODE:
            morse_string += MORSE_CODE[char] + "  "
            
    info(f"Morse Code Audio Transmission")
    print(f"\n  Text  : {text}")
    print(f"  Morse : {CYAN}{morse_string}{RESET}\n")
    print(f"  {DIM}Playing audio over speakers...{RESET}")
    
    dot = 80
    freq = 700
    for char in morse_string:
        if char == '.':
            winsound.Beep(freq, dot)
            time.sleep(dot / 1000.0)
        elif char == '-':
            winsound.Beep(freq, dot * 3)
            time.sleep(dot / 1000.0)
        elif char == ' ':
            time.sleep(dot * 3 / 1000.0)
    
    ok("Transmission complete.")
