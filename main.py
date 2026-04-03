# -*- coding: utf-8 -*-
import sys

from file_ops import (create_file, create_folder, delete, move,
                      rename, copy, list_dir, read_file, write_file,
                      search, tree, find_in_file, get_size, zip_path, unzip_path,
                      hash_file, compare_files, tail_file, count_file)
from system_ops import (set_volume, get_volume, set_brightness, get_brightness,
                        wifi, bluetooth, mute, shutdown, restart, sleep, lock, battery,
                        disk_usage, network_info, sysinfo, list_ips,
                        ps_list, kill_proc, top_procs, clip_copy, clip_paste, remind)
from extras import (find_duplicates, recent_files, find_empty, bulk_rename,
                    monitor, netstat, ping_host, speedtest,
                    pycheck, template, snippet_save, snippet_run, snippet_list)
from productivity import (note_add, note_list, note_clear,
                          todo_add, todo_list, todo_done, todo_remove,
                          encrypt_file, decrypt_file,
                          schedule_add, schedule_list, schedule_remove,
                          _ensure_scheduler)
from app_launcher import open_app, list_apps, add_app, remove_app
from ai_gen import ai_gen, ai_ask, set_key
from colors import ok, err, info, warn, header, GREEN, CYAN, BOLD, RESET, YELLOW
from utils import (
    log_command, show_log, clear_log,
    alias_add, alias_list, alias_remove, expand_alias,
    weather,
    clip_history_add, clip_history_show, clip_history_clear,
)
from tools import (
    calc, randpass, gen_uuid, countdown, stopwatch,
    download, jsonformat, b64_encode, b64_decode,
    serve, serve_stop, convert,
)
from dev_tools import (
    http_request, str_tool, portscan, file_replace,
    extstats, regex_test, csv_view, color_convert,
    env_list, env_get,
)
from advanced import (
    wordfreq, file_diff, checksum_dir, watch_file,
    geoip, dns_lookup, open_url, myip, backup_file,
)
from powertools import (
    speak, screenshot, notify, grep, hashtext,
    hexview, baseconv, lorem, zipls, dashboard,
)
from smart import (
    suggest, fileinfo, netspeed, health,
    startup, coderead, json2csv, csv2json,
)
from extra_tools import (
    define, quote, bigfiles, oldnew, sync_dirs,
    passcheck, textstats, urlencode, urldecode,
    datetools, pomodoro, currency, jsoncheck,
)
from unique import (
    matrix, banner, typetest, journal, habit,
    sysreport, joke, fact, brain, dircompare,
)
from ultra_unique import (
    qrgen, hacker, lifegrid, stegohide, stegoextract,
    biorhythm, sysmap, stock, moonphase, morse,
)
import env_loader

HELP = """
╔═════════════════════════════════════════════════════════╗
║        SYSTEM COMMANDER — COMMAND REFERENCE             ║
╠═════════════════════════════════════════════════════════╣
║  GENERAL                                                ║
║  help                         Show this reference       ║
║  history                      Show command history      ║
║  exit / quit                  Exit System Commander     ║
║  log [n]                      Show last N log entries   ║
║  log clear                    Clear the log file        ║
║  alias add <name> <cmd>       Save a command shortcut   ║
║  alias list                   List all aliases          ║
║  alias remove <name>          Delete an alias           ║
║  config list                  Show .env config keys     ║
║  config set <KEY> <value>     Save a key to .env        ║
║  config get <KEY>             Read a key from .env      ║
╠═════════════════════════════════════════════════════════╣
║  FILE OPERATIONS  (paths relative to D:\\)              ║
║  create file <name>           Create a new file         ║
║  create folder <name>         Create a new folder       ║
║  delete <name>                Delete file or folder     ║
║  move <src> <dst>             Move file/folder          ║
║  rename <old> <new>           Rename file/folder        ║
║  copy <src> <dst>             Copy file/folder          ║
║  list [path]                  List directory contents   ║
║  read <file>                  Print file contents       ║
║  write <file> <content>       Write text to file        ║
║  search <keyword> [path]      Find files by name        ║
║  tree [path]                  Show folder tree          ║
║  find <text> <file>           Search text inside file   ║
║  tail <file> [n]              Show last N lines         ║
║  count <file>                 Lines, words, chars       ║
║  size <path>                  File/folder size          ║
║  hash <file>                  MD5 & SHA256 of file      ║
║  compare <file1> <file2>      Compare two files         ║
║  codefile <file>              Write multi-line code     ║
║  run <file>                   Run a Python script       ║
╠═════════════════════════════════════════════════════════╣
║  FILE MANAGEMENT                                        ║
║  duplicate [path]             Find duplicate files      ║
║  recent [n]                   Last N modified files     ║
║  empty [path]                 Find empty files/folders  ║
║  bulkrename <dir> <old> <new> Rename pattern in folder  ║
║  zip <src> <out.zip>          Zip file or folder        ║
║  unzip <file.zip> <dest>      Unzip archive             ║
║  zipls <archive.zip>          List ZIP contents         ║
║  backup <file>                Timestamped file backup   ║
║  checksum [path]              MD5 checksums for folder  ║
║  sync <src> <dst>             Mirror directory          ║
║  bigfiles [path] [n]          Find N largest files      ║
║  newest [path] [n]            N most recently modified  ║
║  oldest [path] [n]            N oldest files            ║
╠═════════════════════════════════════════════════════════╣
║  FILE ANALYSIS                                          ║
║  fileinfo <file>              Detailed file metadata    ║
║  diff <file1> <file2>         Line-by-line file diff    ║
║  hexview <file> [bytes]       Hex dump viewer           ║
║  watch <file>                 Watch file for changes    ║
║  wordfreq <file> [n]          Top N word frequencies    ║
║  textstats <file>             Chars, words, read-time   ║
║  extstats [path]              File type breakdown       ║
║  coderead <file>              Syntax-coloured viewer    ║
║  csv <file> [rows]            View CSV as table         ║
║  grep <pattern> [path]        Search file contents      ║
║  replace <file> <old> <new>   Find & replace in file    ║
╠═════════════════════════════════════════════════════════╣
║  SYSTEM CONTROLS                                        ║
║  volume [0-100]               Get / set volume          ║
║  brightness [0-100]           Get / set brightness      ║
║  mute                         Toggle mute on/off        ║
║  wifi on|off|status|list      WiFi control              ║
║  bluetooth on|off|status      Bluetooth control         ║
║  battery                      Show battery level        ║
║  disk                         Show D:\ disk usage       ║
║  network                      IP, gateway, internet     ║
║  sysinfo                      CPU, RAM, OS, uptime      ║
║  ip                           All network interfaces    ║
║  lock                         Lock screen               ║
║  sleep                        Sleep mode                ║
║  restart                      Restart computer          ║
║  shutdown                     Shutdown computer         ║
╠═════════════════════════════════════════════════════════╣
║  SYSTEM MONITOR & DIAGNOSTICS                           ║
║  dashboard                    Full system overview      ║
║  health                       System health score       ║
║  monitor                      Live CPU/RAM bars         ║
║  netspeed                     Live upload/download      ║
║  netstat                      Active connections        ║
║  ping <host>                  Ping a host               ║
║  speedtest                    Internet speed test       ║
║  ps                           List all processes        ║
║  top [n]                      Top N processes by CPU    ║
║  kill <name or PID>           Kill a process            ║
║  startup                      List startup programs     ║
╠══════════════════════════════════════════════════════════╣
║  NETWORK & WEB                                          ║
║  http get <url>               Make a GET request        ║
║  http post <url> [data]       Make a POST request       ║
║  download <url> [file]        Download a file to D:\    ║
║  serve [port]                 Quick HTTP server on D:\  ║
║  serve stop                   Stop the HTTP server      ║
║  portscan <host> [s-e]        Threaded port scanner     ║
║  dns <host>                   DNS + reverse lookup      ║
║  geoip <ip/host>              IP geolocation lookup     ║
║  myip                         Your public IP address    ║
║  openurl <url>                Open URL in browser       ║
╠═════════════════════════════════════════════════════════╣
║  DEVELOPER TOOLS                                        ║
║  pycheck <file>               Check Python syntax       ║
║  template <type> <file>       Generate boilerplate      ║
║  snippet save <name> <file>   Save a code snippet       ║
║  snippet run <name>           Run a saved snippet       ║
║  snippet list                 List all snippets         ║
║  str <action> <text>          String tools              ║
║    upper lower title reverse snake camel len count      ║
║  regex <pattern> <text>       Test a regex pattern      ║
║  jsonformat <file>            Pretty-print JSON         ║
║  jsoncheck <file>             Validate a JSON file      ║
║  json2csv <file> [out]        JSON array -> CSV         ║
║  csv2json <file> [out]        CSV -> JSON array         ║
║  color hex2rgb #RRGGBB        Hex -> RGB + swatch       ║
║  color rgb2hex R G B          RGB -> hex + swatch       ║
║  hashtext <algo> <text>       Hash string (md5/sha256)  ║
║  b64 encode/decode <text>     Base64 encode / decode    ║
║  urlencode <text>             URL-encode a string       ║
║  urldecode <text>             URL-decode a string       ║
║  baseconv <n> <from> <to>     Convert number bases      ║
║  env list [filter]            List system env vars      ║
║  env get <var>                Get an env variable       ║
╠═════════════════════════════════════════════════════════╣
║  MATH & CONVERSION                                      ║
║  calc <expression>            Evaluate math expression  ║
║  convert <n> <from> <to>      Unit converter            ║
║  baseconv <n> <from> <to>     Base converter            ║
║  currency <n> <FROM> <TO>     Live currency converter   ║
║  date now                     Show current date & time  ║
║  date diff YYYY-MM-DD D2      Days between two dates    ║
║  date add YYYY-MM-DD N        Add N days to a date      ║
║  date weekday YYYY-MM-DD      Day of week for a date    ║
║  date unix [timestamp]        Unix timestamp convert    ║
╠═════════════════════════════════════════════════════════╣
║  PRODUCTIVITY                                           ║
║  note add <text>              Save a quick note         ║
║  note list                    Show all notes            ║
║  note clear                   Clear all notes           ║
║  todo add <task>              Add a task                ║
║  todo list                    Show all tasks            ║
║  todo done <id>               Mark task as complete     ║
║  todo remove <id>             Remove a task             ║
║  remind <secs> <message>      Popup reminder            ║
║  schedule <HH:MM> <cmd>       Daily scheduled command   ║
║  schedule list                Show scheduled commands   ║
║  schedule remove <id>         Remove a scheduled cmd    ║
║  clip copy <text>             Copy to clipboard         ║
║  clip paste                   Print clipboard contents  ║
║  clip history                 Show clipboard history    ║
║  clip history clear           Clear clipboard history   ║
║  timer <secs> [label]         Countdown timer           ║
║  stopwatch                    Stopwatch (Ctrl+C stops)  ║
║  pomodoro [work] [brk] [n]    Pomodoro timer            ║
╠══════════════════════════════════════════════════════════╣
║  UNIQUE & FUN                                           ║
║  matrix                       Matrix digital rain       ║
║  banner <text>                Generate ASCII art banner ║
║  typetest                     Test your typing speed    ║
║  journal [add|list|search]    Daily private journal     ║
║  habit [add|done|list]        Habit streak tracker      ║
║  sysreport                    Export full system report ║
║  joke                         Tell a random dad joke    ║
║  fact                         Share an interesting fact ║
║  brain [rounds]               Mental math speed quiz    ║
║  dircompare <dir1> <dir2>     Compare two directories   ║
╠═════════════════════════════════════════════════════════╣
║  ULTRA UNIQUE                                           ║
║  qrgen <text>                 Generate ASCII QR code    ║
║  hacker <text>                Hacker text animation     ║
║  lifegrid <YYYY-MM-DD>        90-year visual life grid  ║
║  stegohide <file> <msg>       Hide text invisibly in file║
║  stegoextract <file>          Extract text from file    ║
║  biorhythm <YYYY-MM-DD>       Calculate body cycles     ║
║  sysmap [path]                Visual folder size graph  ║
║  stock <symbol>               Live stock/crypto tracker ║
║  moonphase                    Current astrology phase   ║
║  morse <text>                 Play audio morse code     ║
╠═════════════════════════════════════════════════════════╣
║  AI & GENERATION                                        ║
║  ai setkey <key>              Save your Groq API key    ║
║  ai gen <file> <prompt>       Generate code to a file   ║
║  ai ask <prompt>              Ask the AI anything       ║
║  lorem [n]                    Lorem ipsum text          ║
║  randpass [n]                 Random secure password    ║
║  uuid                         Generate a UUID v4        ║
╠═════════════════════════════════════════════════════════╣
║  APPS, SECURITY & WINDOWS                               ║
║  open <appname>               Open an application       ║
║  apps list/add/remove         Manage known apps         ║
║  encrypt <file> <password>    Encrypt a file            ║
║  decrypt <file> <password>    Decrypt a file            ║
║  passcheck <password>         Password strength check   ║
║  speak <text>                 Text-to-speech            ║
║  screenshot [filename]        Save screenshot to D:\    ║
║  notify <title> [message]     Windows notification      ║
╠═════════════════════════════════════════════════════════╣
║  INFORMATION & LOOKUP                                   ║
║  define <word>                Dictionary definition     ║
║  quote                        Random inspirational quote║
║  weather <city>               Current weather           ║
║  geoip <ip>                   IP geolocation info       ║
║  dns <host>                   DNS lookup                ║
╚═════════════════════════════════════════════════════════╝
"""

_history = []

# ─────────────────────────────────────────────────────────────────────────────
# SECURITY LAYER
# ─────────────────────────────────────────────────────────────────────────────

# Hard-blocked strings — any command containing these is rejected.
_BLOCKED = [
    # System directories
    "system32", "syswow64", "windows\\", "program files", "programdata",
    "appdata", "roaming", "localappdata",
    # Registry
    "registry", "regedit", "reg ", "reg.exe", "reg add", "reg del",
    # Disk destruction
    "format ", "format.com", "diskpart", "bcdedit", "bootrec",
    # Recursive delete / wipe
    "del /", "rd /s", "rmdir /s", "cipher /w", "sdelete",
    # Net user tampering
    "net user", "net localgroup", "net share", "net accounts",
    # Permission changes
    "icacls", "takeown", "cacls", "attrib +h", "attrib -h",
    # Shell spawning
    "cmd.exe", "wscript", "cscript", "mshta",
    "rundll32", "regsvr32", "msiexec", "wmic",
    # Env vars pointing outside D:
    "%systemroot%", "%windir%", "%appdata%", "%temp%", "%tmp%",
    "%userprofile%", "%programfiles%", "%programdata%",
    # Other drive letters
    "c:\\", "a:\\", "b:\\", "e:\\", "f:\\", "g:\\", "h:\\",
    "i:\\", "j:\\", "k:\\", "l:\\", "m:\\", "n:\\",
    "o:\\", "p:\\", "q:\\", "r:\\", "s:\\", "t:\\",
    "u:\\", "v:\\", "w:\\", "x:\\", "y:\\", "z:\\",
    # PowerShell abuse vectors
    "invoke-expression", "iex ", "invoke-webrequest",
    "downloadstring", "downloadfile", "start-process",
    "set-executionpolicy", "bypass",
    # Path traversal
    "../", "..\\",
]

_BLOCKED_COMMANDS = {
    "powershell", "cmd", "bash", "sh", "python", "py",
    "perl", "ruby", "node", "npm",
}

def _is_dangerous(cmd: str) -> str:
    """Return a reason string if blocked, empty string if safe."""
    low = cmd.lower().strip()

    # Block if first word is a raw shell/interpreter
    first = low.split()[0] if low.split() else ""
    if first in _BLOCKED_COMMANDS:
        return f"Direct execution of '{first}' is not allowed."

    # Block if any blocked substring is present
    for b in _BLOCKED:
        if b in low:
            return f"Blocked pattern detected: '{b}'"

    # Block drive letters other than D: (pattern like X: at word boundary)
    import re
    if re.search(r'\b[a-ce-zA-CE-Z]:[/\\]', low):
        return "Access restricted to D: drive only."

    return ""

def handle(cmd):
    cmd = expand_alias(cmd)          # expand aliases first
    parts = cmd.strip().split()
    if not parts:
        return
    reason = _is_dangerous(cmd)
    if reason:
        err(f"Blocked: {reason}")
        log_command(f"[BLOCKED] {cmd.strip()}")
        return
    _history.append(cmd.strip())
    log_command(cmd.strip())         # persist to log file
    c = parts[0].lower()

    try:
        # --- File Operations ---
        if c == "create":
            if len(parts) < 3:
                print("Usage: create file <name> | create folder <name>")
            elif parts[1].lower() == "file":
                create_file(parts[2])
            elif parts[1].lower() == "folder":
                create_folder(parts[2])
            else:
                print("Usage: create file <name> | create folder <name>")

        elif c == "delete":
            if len(parts) < 2: print("Usage: delete <name>")
            else:
                target = parts[2] if len(parts) > 2 and parts[1].lower() in ("file", "folder") else parts[1]
                delete(target)

        elif c == "move":
            if len(parts) < 3: print("Usage: move <src> <dst>")
            else: move(parts[1], parts[2])

        elif c == "rename":
            if len(parts) < 3: print("Usage: rename <old> <new>")
            else: rename(parts[1], parts[2])

        elif c == "copy":
            if len(parts) < 3: print("Usage: copy <src> <dst>")
            else: copy(parts[1], parts[2])

        elif c == "list":
            list_dir(parts[1] if len(parts) > 1 else ".")

        elif c == "read":
            if len(parts) < 2: print("Usage: read <file>")
            else: read_file(parts[1])

        elif c == "write":
            if len(parts) < 3: print("Usage: write <file> <content>")
            else: write_file(parts[1], " ".join(parts[2:]))

        elif c == "search":
            if len(parts) < 2: print("Usage: search <keyword> [path]")
            else: search(parts[1], parts[2] if len(parts) > 2 else ".")

        elif c == "tree":
            tree(parts[1] if len(parts) > 1 else ".")

        elif c == "find":
            if len(parts) < 3: print("Usage: find <text> <file>")
            else: find_in_file(parts[1], parts[2])

        elif c == "size":
            if len(parts) < 2: print("Usage: size <path>")
            else: get_size(parts[1])

        elif c == "zip":
            if len(parts) < 3: print("Usage: zip <src> <out.zip>")
            else: zip_path(parts[1], parts[2])

        elif c == "unzip":
            if len(parts) < 3: print("Usage: unzip <file.zip> <dest>")
            else: unzip_path(parts[1], parts[2])

        elif c == "hash":
            if len(parts) < 2: print("Usage: hash <file>")
            else: hash_file(parts[1])

        elif c == "compare":
            if len(parts) < 3: print("Usage: compare <file1> <file2>")
            else: compare_files(parts[1], parts[2])

        elif c == "tail":
            if len(parts) < 2: print("Usage: tail <file> [n]")
            else: tail_file(parts[1], int(parts[2]) if len(parts) > 2 else 10)

        elif c == "count":
            if len(parts) < 2: print("Usage: count <file>")
            else: count_file(parts[1])

        elif c == "codefile":
            if len(parts) < 2:
                print("Usage: codefile <file>")
            else:
                from file_ops import safe_path
                p = safe_path(parts[1])
                print("Enter code line by line. Type 'END' on a new line to save.")
                lines = []
                while True:
                    line = input("... ")
                    if line.strip() == "END":
                        break
                    lines.append(line)
                with open(p, 'w') as f:
                    f.write("\n".join(lines))
                print(f"Saved to: {p}")

        elif c == "run":
            if len(parts) < 2:
                print("Usage: run <file>")
            else:
                from file_ops import safe_path
                import subprocess
                p = safe_path(parts[1])
                result = subprocess.run([sys.executable, p], capture_output=True, text=True)
                if result.stdout: print(result.stdout.rstrip())
                if result.stderr: print(result.stderr.rstrip())

        # --- File Intelligence ---
        elif c == "duplicate":
            find_duplicates(parts[1] if len(parts) > 1 else ".")

        elif c == "recent":
            recent_files(int(parts[1]) if len(parts) > 1 else 10)

        elif c == "empty":
            find_empty(parts[1] if len(parts) > 1 else ".")

        elif c == "bulkrename":
            if len(parts) < 4: print("Usage: bulkrename <folder> <old> <new>")
            else: bulk_rename(parts[1], parts[2], parts[3])

        # --- Code Tools ---
        elif c == "pycheck":
            if len(parts) < 2: print("Usage: pycheck <file>")
            else: pycheck(parts[1])

        elif c == "template":
            if len(parts) < 3: print(f"Usage: template <type> <file>  types: python, html, flask, class, csv")
            else: template(parts[1], parts[2])

        elif c == "snippet":
            if len(parts) < 2: print("Usage: snippet save <name> <file> | snippet run <name> | snippet list")
            elif parts[1] == "save":
                if len(parts) < 4: print("Usage: snippet save <name> <file>")
                else: snippet_save(parts[2], parts[3])
            elif parts[1] == "run":
                if len(parts) < 3: print("Usage: snippet run <name>")
                else: snippet_run(parts[2])
            elif parts[1] == "list":
                snippet_list()
            else: print("Usage: snippet save <name> <file> | snippet run <name> | snippet list")

        # --- System Controls ---
        elif c == "volume":
            if len(parts) < 2: get_volume()
            else: set_volume(parts[1])

        elif c == "brightness":
            if len(parts) < 2: get_brightness()
            else: set_brightness(parts[1])

        elif c == "mute":
            mute()

        elif c == "wifi":
            if len(parts) < 2: print("Usage: wifi on|off|status|list")
            else: wifi(parts[1])

        elif c == "bluetooth":
            if len(parts) < 2: print("Usage: bluetooth on|off|status")
            else: bluetooth(parts[1])

        elif c == "battery":
            battery()

        elif c == "disk":
            disk_usage()

        elif c == "network":
            network_info()

        elif c == "sysinfo":
            sysinfo()

        elif c == "ip":
            list_ips()

        # --- System Monitor ---
        elif c == "monitor":
            monitor()

        elif c == "netstat":
            netstat()

        elif c == "ping":
            if len(parts) < 2: print("Usage: ping <host>")
            else: ping_host(parts[1])

        elif c == "speedtest":
            speedtest()

        # --- Process Management ---
        elif c == "ps":
            ps_list()

        elif c == "top":
            top_procs(int(parts[1]) if len(parts) > 1 else 10)

        elif c == "kill":
            if len(parts) < 2: print("Usage: kill <name or PID>")
            else: kill_proc(parts[1])

        # --- Clipboard ---
        elif c == "clip":
            if len(parts) < 2: err("Usage: clip copy <text> | clip paste | clip history")
            elif parts[1] == "paste": clip_paste()
            elif parts[1] == "history":
                if len(parts) > 2 and parts[2] == "clear": clip_history_clear()
                else: clip_history_show()
            elif parts[1] == "copy":
                if len(parts) < 3: err("Usage: clip copy <text>")
                else:
                    text = " ".join(parts[2:])
                    clip_copy(text)
                    clip_history_add(text)
            else: err("Usage: clip copy <text> | clip paste | clip history")

        # --- Notes ---
        elif c == "note":
            if len(parts) < 2: print("Usage: note add <text> | note list | note clear")
            elif parts[1] == "add":
                if len(parts) < 3: print("Usage: note add <text>")
                else: note_add(" ".join(parts[2:]))
            elif parts[1] == "list": note_list()
            elif parts[1] == "clear": note_clear()
            else: print("Usage: note add <text> | note list | note clear")

        # --- Todo ---
        elif c == "todo":
            if len(parts) < 2: print("Usage: todo add <task> | todo list | todo done <id> | todo remove <id>")
            elif parts[1] == "add":
                if len(parts) < 3: print("Usage: todo add <task>")
                else: todo_add(" ".join(parts[2:]))
            elif parts[1] == "list": todo_list()
            elif parts[1] == "done":
                if len(parts) < 3: print("Usage: todo done <id>")
                else: todo_done(parts[2])
            elif parts[1] == "remove":
                if len(parts) < 3: print("Usage: todo remove <id>")
                else: todo_remove(parts[2])
            else: print("Usage: todo add <task> | todo list | todo done <id> | todo remove <id>")

        # --- Encryption ---
        elif c == "encrypt":
            if len(parts) < 3: print("Usage: encrypt <file> <password>")
            else: encrypt_file(parts[1], parts[2])

        elif c == "decrypt":
            if len(parts) < 3: print("Usage: decrypt <file> <password>")
            else: decrypt_file(parts[1], parts[2])

        # --- Scheduler ---
        elif c == "schedule":
            if len(parts) < 2: print("Usage: schedule <HH:MM> <command> | schedule list | schedule remove <id>")
            elif parts[1] == "list": schedule_list()
            elif parts[1] == "remove":
                if len(parts) < 3: print("Usage: schedule remove <id>")
                else: schedule_remove(parts[2])
            elif len(parts) >= 3: schedule_add(parts[1], " ".join(parts[2:]))
            else: print("Usage: schedule <HH:MM> <command>")

        # --- Reminders ---
        elif c == "remind":
            if len(parts) < 3: print("Usage: remind <seconds> <message>")
            else: remind(parts[1], " ".join(parts[2:]))

        # --- AI ---
        elif c == "ai":
            if len(parts) < 2: print("Usage: ai setkey <key> | ai gen <file> <prompt> | ai ask <prompt>")
            elif parts[1] == "setkey":
                if len(parts) < 3: print("Usage: ai setkey <your_groq_api_key>")
                else: set_key(parts[2])
            elif parts[1] == "gen":
                if len(parts) < 4: print("Usage: ai gen <file> <prompt>")
                else: ai_gen(" ".join(parts[3:]), parts[2])
            elif parts[1] == "ask":
                if len(parts) < 3: print("Usage: ai ask <prompt>")
                else: ai_ask(" ".join(parts[2:]))
            else: print("Usage: ai setkey <key> | ai gen <file> <prompt> | ai ask <prompt>")

        elif c == "lock":
            lock()

        elif c == "sleep":
            sleep()

        elif c == "restart":
            restart()

        elif c == "shutdown":
            shutdown()

        # --- App Launcher ---
        elif c == "open":
            if len(parts) < 2: print("Usage: open <appname>")
            else: open_app(parts[1])

        elif c == "apps":
            if len(parts) < 2 or parts[1] == "list":
                list_apps()
            elif parts[1] == "add":
                if len(parts) < 4: print("Usage: apps add <name> <path>")
                else: add_app(parts[2], " ".join(parts[3:]))
            elif parts[1] == "remove":
                if len(parts) < 3: print("Usage: apps remove <name>")
                else: remove_app(parts[2])

        elif c == "history":
            if not _history:
                print("No history yet.")
            else:
                for i, h in enumerate(_history, 1):
                    print(f"  {i:3}. {h}")

        elif c in ("help", "?"):
            print(HELP)

        elif c in ("exit", "quit"):
            print("Goodbye!")
            sys.exit(0)

        # ── Aliases ──────────────────────────────────────────────────────────
        elif c == "alias":
            if len(parts) < 2 or parts[1] == "list":
                alias_list()
            elif parts[1] == "add":
                if len(parts) < 4: err("Usage: alias add <name> <command>")
                else: alias_add(parts[2], " ".join(parts[3:]))
            elif parts[1] == "remove":
                if len(parts) < 3: err("Usage: alias remove <name>")
                else: alias_remove(parts[2])
            else: err("Usage: alias add <name> <cmd> | alias list | alias remove <name>")

        # ── Log ──────────────────────────────────────────────────────────────
        elif c == "log":
            if len(parts) > 1 and parts[1] == "clear": clear_log()
            else: show_log(int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 20)

        # ── Weather ──────────────────────────────────────────────────────────
        elif c == "weather":
            weather(" ".join(parts[1:]) if len(parts) > 1 else "")

        elif c == "calc":
            if len(parts) < 2: err("Usage: calc <expression>  e.g. calc 2+3*4")
            else: calc(" ".join(parts[1:]))

        # ── Environment Variables ───────────────────────────────────────────
        elif c == "env":
            if len(parts) < 2 or parts[1] == "list": env_list(parts[2] if len(parts) > 2 else "")
            elif parts[1] == "get":
                if len(parts) < 3: err("Usage: env get <variable>")
                else: env_get(parts[2])
            else: err("Usage: env list [filter] | env get <var>")

        # ── .env Config ──────────────────────────────────────────────────────
        elif c == "config":
            if len(parts) < 2 or parts[1] == "list":
                keys = env_loader.list_keys()
                info("Stored config (.env):")
                for k, v in keys.items():
                    print(f"  {CYAN}{k:<25}{RESET}  {v}")
            elif parts[1] == "set":
                if len(parts) < 4: err("Usage: config set <KEY> <value>")
                else:
                    env_loader.set_value(parts[2], " ".join(parts[3:]))
                    ok(f"{parts[2]} saved to .env")
            elif parts[1] == "get":
                if len(parts) < 3: err("Usage: config get <KEY>")
                else:
                    v = env_loader.get(parts[2])
                    if v: print(f"  {CYAN}{parts[2]}{RESET} = {v}")
                    else: warn(f"{parts[2]} not set in .env")
            else: err("Usage: config list | config set <KEY> <value> | config get <KEY>")

        # ── Word Frequency ────────────────────────────────────────────────
        elif c == "wordfreq":
            if len(parts) < 2: err("Usage: wordfreq <file> [top_n]")
            else: wordfreq(parts[1], int(parts[2]) if len(parts) > 2 else 15)

        # ── File Diff ────────────────────────────────────────────────────────
        elif c == "diff":
            if len(parts) < 3: err("Usage: diff <file1> <file2>")
            else: file_diff(parts[1], parts[2])

        # ── Directory Checksum ─────────────────────────────────────────────
        elif c == "checksum":
            checksum_dir(parts[1] if len(parts) > 1 else ".")

        # ── File Watcher ───────────────────────────────────────────────────────
        elif c == "watch":
            if len(parts) < 2: err("Usage: watch <file>")
            else: watch_file(parts[1])

        # ── GeoIP ────────────────────────────────────────────────────────────
        elif c == "geoip":
            if len(parts) < 2: err("Usage: geoip <ip_or_hostname>")
            else: geoip(parts[1])

        # ── DNS Lookup ───────────────────────────────────────────────────────
        elif c == "dns":
            if len(parts) < 2: err("Usage: dns <hostname_or_ip>")
            else: dns_lookup(parts[1])

        # ── Open URL ─────────────────────────────────────────────────────────
        elif c == "openurl":
            if len(parts) < 2: err("Usage: openurl <url>")
            else: open_url(parts[1])

        # ── My Public IP ───────────────────────────────────────────────────
        elif c == "myip":
            myip()

        # ── Backup File ─────────────────────────────────────────────────────
        elif c == "backup":
            if len(parts) < 2: err("Usage: backup <file>")
            else: backup_file(parts[1])

        # ── Random Password ──────────────────────────────────────────────────
        elif c == "randpass":
            length = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 16
            no_sym = len(parts) > 2 and parts[2] == "--nosym"
            randpass(length, symbols=not no_sym)

        # ── UUID ─────────────────────────────────────────────────────────────
        elif c == "uuid":
            gen_uuid()

        # ── Timer ────────────────────────────────────────────────────────────
        elif c == "timer":
            if len(parts) < 2: err("Usage: timer <seconds> [label]")
            else: countdown(int(parts[1]), " ".join(parts[2:]))

        # ── Stopwatch ────────────────────────────────────────────────────────
        elif c == "stopwatch":
            stopwatch()

        # ── Download ─────────────────────────────────────────────────────────
        elif c == "download":
            if len(parts) < 2: err("Usage: download <url> [filename]")
            else: download(parts[1], parts[2] if len(parts) > 2 else "")

        # ── JSON Format ──────────────────────────────────────────────────────
        elif c == "jsonformat":
            if len(parts) < 2: err("Usage: jsonformat <file>")
            else: jsonformat(parts[1])

        # ── Base64 ───────────────────────────────────────────────────────────
        elif c == "b64":
            if len(parts) < 3: err("Usage: b64 encode <text> | b64 decode <text>")
            elif parts[1] == "encode": b64_encode(" ".join(parts[2:]))
            elif parts[1] == "decode": b64_decode(" ".join(parts[2:]))
            else: err("Usage: b64 encode <text> | b64 decode <text>")

        # ── HTTP Server ──────────────────────────────────────────────────────
        elif c == "serve":
            if len(parts) > 1 and parts[1] == "stop": serve_stop()
            else: serve(int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 8080)

        # ── Unit Converter ───────────────────────────────────────────────────
        elif c == "convert":
            if len(parts) < 4: err("Usage: convert <number> <from_unit> <to_unit>  e.g. convert 100 km mi")
            else: convert(parts[1], parts[2], parts[3])

        # ── HTTP Request ───────────────────────────────────────────────────
        elif c == "http":
            if len(parts) < 3: err("Usage: http get <url> | http post <url> [data]")
            else: http_request(parts[1], parts[2], " ".join(parts[3:]))

        # ── String Tools ───────────────────────────────────────────────────
        elif c == "str":
            if len(parts) < 3: err("Usage: str <action> <text>  actions: upper lower title reverse snake camel pascal len count")
            else: str_tool(parts[1], " ".join(parts[2:]))

        # ── Port Scanner ───────────────────────────────────────────────────
        elif c == "portscan":
            if len(parts) < 2: err("Usage: portscan <host> [start_port] [end_port]")
            else:
                s = int(parts[2]) if len(parts) > 2 else 1
                e = int(parts[3]) if len(parts) > 3 else 1024
                portscan(parts[1], s, e)

        # ── Find & Replace in File ────────────────────────────────────────
        elif c == "replace":
            if len(parts) < 4: err("Usage: replace <file> <old_text> <new_text>")
            else: file_replace(parts[1], parts[2], parts[3])

        # ── Extension Stats ──────────────────────────────────────────────────
        elif c == "extstats":
            extstats(parts[1] if len(parts) > 1 else ".")

        # ── Regex Tester ───────────────────────────────────────────────────
        elif c == "regex":
            if len(parts) < 3: err("Usage: regex <pattern> <text>")
            else: regex_test(parts[1], " ".join(parts[2:]))

        # ── CSV Viewer ────────────────────────────────────────────────────────
        elif c == "csv":
            if len(parts) < 2: err("Usage: csv <file> [rows]")
            else: csv_view(parts[1], int(parts[2]) if len(parts) > 2 else 20)

        # ── Color Converter ──────────────────────────────────────────────────
        elif c == "color":
            if len(parts) < 3: err("Usage: color hex2rgb <#HEX> | color rgb2hex <R> <G> <B>")
            else: color_convert(parts[1], " ".join(parts[2:]))

        # ── Environment Variables ────────────────────────────────────────────
        elif c == "env":
            if len(parts) < 2 or parts[1] == "list": env_list(parts[2] if len(parts) > 2 else "")
            elif parts[1] == "get":
                if len(parts) < 3: err("Usage: env get <variable>")
                else: env_get(parts[2])
            else: err("Usage: env list [filter] | env get <var>")

        # ── Speak ────────────────────────────────────────────────────────────
        elif c == "speak":
            if len(parts) < 2: err("Usage: speak <text>")
            else: speak(" ".join(parts[1:]))

        # ── Screenshot ───────────────────────────────────────────────────────
        elif c == "screenshot":
            screenshot(parts[1] if len(parts) > 1 else "")

        # ── Notify ───────────────────────────────────────────────────────────
        elif c == "notify":
            if len(parts) < 2: err("Usage: notify <title> [message]")
            else: notify(parts[1], " ".join(parts[2:]))

        # ── Grep (content search) ─────────────────────────────────────────────
        elif c == "grep":
            if len(parts) < 2: err("Usage: grep <pattern> [path] [--ext py,txt]")
            else:
                path = parts[2] if len(parts) > 2 and not parts[2].startswith("--") else "."
                ext  = ""
                if "--ext" in parts:
                    idx = parts.index("--ext")
                    ext = parts[idx + 1] if idx + 1 < len(parts) else ""
                grep(parts[1], path, ext)

        # ── Hash Text ─────────────────────────────────────────────────────────
        elif c == "hashtext":
            if len(parts) < 3: err("Usage: hashtext <md5|sha1|sha256|sha512> <text>")
            else: hashtext(parts[1], " ".join(parts[2:]))

        # ── Hex View ──────────────────────────────────────────────────────────
        elif c == "hexview":
            if len(parts) < 2: err("Usage: hexview <file> [bytes]")
            else: hexview(parts[1], int(parts[2]) if len(parts) > 2 else 256)

        # ── Base Converter ────────────────────────────────────────────────────
        elif c == "baseconv":
            if len(parts) < 4: err("Usage: baseconv <number> <from_base> <to_base>  e.g. baseconv ff hex dec")
            else: baseconv(parts[1], parts[2], parts[3])

        # ── Lorem Ipsum ───────────────────────────────────────────────────────
        elif c == "lorem":
            lorem(int(parts[1]) if len(parts) > 1 else 50)

        # ── ZIP Lister ────────────────────────────────────────────────────────
        elif c == "zipls":
            if len(parts) < 2: err("Usage: zipls <archive.zip>")
            else: zipls(parts[1])

        # ── Dashboard ─────────────────────────────────────────────────────────
        elif c == "dashboard":
            dashboard()

        # ── File Info ────────────────────────────────────────────────────
        elif c == "fileinfo":
            if len(parts) < 2: err("Usage: fileinfo <file>")
            else: fileinfo(parts[1])

        # ── Network Speed ───────────────────────────────────────────────
        elif c == "netspeed":
            netspeed()

        # ── Health Report ───────────────────────────────────────────────
        elif c == "health":
            health()

        # ── Startup Programs ────────────────────────────────────────────
        elif c == "startup":
            startup()

        # ── Syntax-Colored Code Reader ─────────────────────────────────
        elif c == "coderead":
            if len(parts) < 2: err("Usage: coderead <file>")
            else: coderead(parts[1])

        # ── JSON ↔ CSV ──────────────────────────────────────────────────
        elif c == "json2csv":
            if len(parts) < 2: err("Usage: json2csv <file.json> [output.csv]")
            else: json2csv(parts[1], parts[2] if len(parts) > 2 else "")

        elif c == "csv2json":
            if len(parts) < 2: err("Usage: csv2json <file.csv> [output.json]")
            else: csv2json(parts[1], parts[2] if len(parts) > 2 else "")

        # ── Dictionary ──────────────────────────────────────────────────────
        elif c == "define":
            if len(parts) < 2: err("Usage: define <word>")
            else: define(parts[1])

        # ── Random Quote ───────────────────────────────────────────────────
        elif c == "quote":
            quote()

        # ── Big Files ───────────────────────────────────────────────────────
        elif c == "bigfiles":
            path = parts[1] if len(parts) > 1 else "."
            n    = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 10
            bigfiles(path, n)

        # ── Newest / Oldest Files ────────────────────────────────────────
        elif c in ("newest", "oldest"):
            path = parts[1] if len(parts) > 1 else "."
            n    = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 10
            oldnew(c, path, n)

        # ── Directory Sync ────────────────────────────────────────────────
        elif c == "sync":
            if len(parts) < 3: err("Usage: sync <source_dir> <dest_dir>")
            else: sync_dirs(parts[1], parts[2])

        # ── Password Strength ─────────────────────────────────────────────
        elif c == "passcheck":
            if len(parts) < 2: err("Usage: passcheck <password>")
            else: passcheck(" ".join(parts[1:]))

        # ── Text Statistics ───────────────────────────────────────────────
        elif c == "textstats":
            if len(parts) < 2: err("Usage: textstats <file>")
            else: textstats(parts[1])

        # ── URL Encode/Decode ─────────────────────────────────────────────
        elif c == "urlencode":
            if len(parts) < 2: err("Usage: urlencode <text>")
            else: urlencode(" ".join(parts[1:]))

        elif c == "urldecode":
            if len(parts) < 2: err("Usage: urldecode <text>")
            else: urldecode(" ".join(parts[1:]))

        # ── Date Tools ──────────────────────────────────────────────────────
        elif c == "date":
            action = parts[1] if len(parts) > 1 else "now"
            a1 = parts[2] if len(parts) > 2 else ""
            a2 = parts[3] if len(parts) > 3 else ""
            datetools(action, a1, a2)

        # ── Pomodoro ────────────────────────────────────────────────────────
        elif c == "pomodoro":
            work  = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 25
            brk   = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 5
            cyc   = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 4
            pomodoro(work, brk, cyc)

        # ── Currency Converter ────────────────────────────────────────────
        elif c == "currency":
            if len(parts) < 4: err("Usage: currency <amount> <FROM> <TO>   e.g. currency 100 USD INR")
            else: currency(parts[1], parts[2], parts[3])

        # ── JSON Validator ───────────────────────────────────────────────
        elif c == "jsoncheck":
            if len(parts) < 2: err("Usage: jsoncheck <file.json>")
            else: jsoncheck(parts[1])

        # ── UNIQUE & FUN ──────────────────────────────────────────────────
        elif c == "matrix":
            matrix()

        elif c == "banner":
            if len(parts) < 2: err("Usage: banner <text>")
            else: banner(" ".join(parts[1:]))

        elif c == "typetest":
            typetest()

        elif c == "journal":
            action = parts[1] if len(parts) > 1 else "list"
            text   = " ".join(parts[2:]) if len(parts) > 2 else ""
            journal(action, text)

        elif c == "habit":
            action = parts[1] if len(parts) > 1 else "list"
            name   = " ".join(parts[2:]) if len(parts) > 2 else ""
            habit(action, name)

        elif c == "sysreport":
            sysreport()

        elif c == "joke":
            joke()

        elif c == "fact":
            fact()

        elif c == "brain":
            n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
            brain(n)

        elif c == "dircompare":
            if len(parts) < 3: err("Usage: dircompare <dir1> <dir2>")
            else: dircompare(parts[1], parts[2])

        # ── ULTRA UNIQUE ──────────────────────────────────────────────────
        elif c == "qrgen":
            if len(parts) < 2: err("Usage: qrgen <text>")
            else: qrgen(" ".join(parts[1:]))

        elif c == "hacker":
            if len(parts) < 2: err("Usage: hacker <text>")
            else: hacker(" ".join(parts[1:]))

        elif c == "lifegrid":
            if len(parts) < 2: err("Usage: lifegrid <YYYY-MM-DD>")
            else: lifegrid(parts[1])

        elif c == "stegohide":
            if len(parts) < 3: err("Usage: stegohide <file> <message>")
            else: stegohide(parts[1], " ".join(parts[2:]))

        elif c == "stegoextract":
            if len(parts) < 2: err("Usage: stegoextract <file>")
            else: stegoextract(parts[1])

        elif c == "biorhythm":
            if len(parts) < 2: err("Usage: biorhythm <YYYY-MM-DD>")
            else: biorhythm(parts[1])

        elif c == "sysmap":
            path = parts[1] if len(parts) > 1 else "."
            sysmap(path)

        elif c == "stock":
            if len(parts) < 2: err("Usage: stock <symbol>")
            else: stock(parts[1])

        elif c == "moonphase":
            moonphase()

        elif c == "morse":
            if len(parts) < 2: err("Usage: morse <text>")
            else: morse(" ".join(parts[1:]))

        else:
            suggest(c)   # did-you-mean instead of plain error


    except PermissionError as e:
        err(f"Permission denied: {e}")
    except FileNotFoundError as e:
        err(f"Not found: {e}")
    except Exception as e:
        err(f"Error: {e}")

def main():
    import os
    os.system("")
    print(f"{BOLD}{CYAN}")
    print("╔══════════════════════════════════════════════╗")
    print("║         SYSTEM COMMANDER  v2.0               ║")
    print("║  Type 'help' for commands, 'exit' to quit    ║")
    print("║  File ops restricted to D:\\                  ║")
    print(f"╚══════════════════════════════════════════════╝{RESET}")
    print()
    _ensure_scheduler()
    while True:
        try:
            cmd = input(f"{BOLD}{GREEN}>>{RESET} ").strip()
            if cmd:
                handle(cmd)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Use 'exit' to quit.{RESET}")

if __name__ == "__main__":
    main()
