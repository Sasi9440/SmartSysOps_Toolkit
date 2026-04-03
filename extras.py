import os
import hashlib
import ast
import subprocess
import sys

BASE = "D:\\"

def safe_path(path):
    path = os.path.splitdrive(path)[1].lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        raise PermissionError("Access restricted to D: drive only.")
    return full

# --- File Intelligence ---

def find_duplicates(path="."):
    p = safe_path(path)
    hashes = {}
    for root, _, files in os.walk(p):
        for f in files:
            fp = os.path.join(root, f)
            try:
                h = hashlib.md5(open(fp, 'rb').read()).hexdigest()
                hashes.setdefault(h, []).append(fp)
            except Exception:
                pass
    found = {h: v for h, v in hashes.items() if len(v) > 1}
    if not found:
        print("No duplicates found.")
    else:
        for h, files in found.items():
            print(f"  [{h[:8]}]")
            for f in files:
                print(f"    {f}")

def recent_files(n=10):
    p = safe_path(".")
    files = []
    for root, _, fs in os.walk(p):
        for f in fs:
            fp = os.path.join(root, f)
            try:
                files.append((os.path.getmtime(fp), fp))
            except Exception:
                pass
    files.sort(reverse=True)
    for mtime, fp in files[:n]:
        import datetime
        t = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        print(f"  {t}  {fp}")

def find_empty(path="."):
    p = safe_path(path)
    found = False
    for root, dirs, files in os.walk(p):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.getsize(fp) == 0:
                print(f"  [FILE] {fp}")
                found = True
        for d in dirs:
            dp = os.path.join(root, d)
            if not os.listdir(dp):
                print(f"  [DIR]  {dp}")
                found = True
    if not found:
        print("No empty files or folders found.")

def bulk_rename(folder, old, new):
    p = safe_path(folder)
    count = 0
    for f in os.listdir(p):
        if old in f:
            src = os.path.join(p, f)
            dst = os.path.join(p, f.replace(old, new))
            os.rename(src, dst)
            print(f"  {f} -> {f.replace(old, new)}")
            count += 1
    print(f"Renamed {count} file(s).")

# --- System Monitor ---

def monitor():
    import psutil, time
    print()
    print("Live monitor (press Ctrl+C to stop)...")
    print()
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            bar_cpu = "█" * int(cpu / 5) + "░" * (20 - int(cpu / 5))
            bar_ram = "█" * int(ram.percent / 5) + "░" * (20 - int(ram.percent / 5))
            print(f"\r  CPU [{bar_cpu}] {cpu:5.1f}%   RAM [{bar_ram}] {ram.percent:5.1f}%  ", end="", flush=True)
    except KeyboardInterrupt:
        print()

def netstat():
    import psutil
    print(f"  {'PID':>6}  {'LADDR':<25}  {'RADDR':<25}  STATUS")
    print(f"  {'-'*6}  {'-'*25}  {'-'*25}  {'-'*12}")
    for conn in psutil.net_connections(kind='inet'):
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
        print(f"  {conn.pid or '':>6}  {laddr:<25}  {raddr:<25}  {conn.status}")

def ping_host(host):
    result = subprocess.run(["ping", "-n", "4", host], capture_output=True, text=True)
    print(result.stdout.strip())

def speedtest():
    try:
        import speedtest as st
        s = st.Speedtest()
        print("Testing download speed...")
        dl = s.download() / 1_000_000
        print("Testing upload speed...")
        ul = s.upload() / 1_000_000
        print(f"  Download : {dl:.2f} Mbps")
        print(f"  Upload   : {ul:.2f} Mbps")
        print(f"  Ping     : {s.results.ping:.1f} ms")
    except ImportError:
        print("Run: pip install speedtest-cli")
    except Exception as e:
        print(f"Speedtest error: {e}")

# --- Code Tools ---

def pycheck(name):
    p = safe_path(name)
    with open(p, 'r', errors='ignore') as f:
        src = f.read()
    try:
        ast.parse(src)
        print(f"No syntax errors found in {name}")
    except SyntaxError as e:
        print(f"Syntax error at line {e.lineno}: {e.msg}")

TEMPLATES = {
    "python": "# Python script\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()\n",
    "html": "<!DOCTYPE html>\n<html>\n<head><title>Page</title></head>\n<body>\n  <h1>Hello</h1>\n</body>\n</html>\n",
    "flask": "from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef index():\n    return 'Hello World'\n\nif __name__ == '__main__':\n    app.run(debug=True)\n",
    "class": "class MyClass:\n    def __init__(self):\n        pass\n\n    def method(self):\n        pass\n",
    "csv": "import csv\n\nwith open('data.csv', 'w', newline='') as f:\n    writer = csv.writer(f)\n    writer.writerow(['col1', 'col2'])\n",
}

def template(ttype, name):
    if ttype not in TEMPLATES:
        print(f"Unknown template. Available: {', '.join(TEMPLATES)}")
        return
    p = safe_path(name)
    with open(p, 'w') as f:
        f.write(TEMPLATES[ttype])
    print(f"Template '{ttype}' written to {p}")

SNIPPETS_FILE = "D:\\snippets.txt"

def snippet_save(name, filepath):
    p = safe_path(filepath)
    content = open(p, 'r', errors='ignore').read()
    snippets = _load_snippets()
    snippets[name] = content
    _save_snippets(snippets)
    print(f"Snippet '{name}' saved.")

def snippet_run(name):
    snippets = _load_snippets()
    if name not in snippets:
        print(f"Snippet '{name}' not found.")
        return
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(snippets[name])
        tmp_path = tmp.name
    result = subprocess.run([sys.executable, tmp_path], capture_output=True, text=True)
    os.unlink(tmp_path)
    if result.stdout: print(result.stdout.rstrip())
    if result.stderr: print(result.stderr.rstrip())

def snippet_list():
    snippets = _load_snippets()
    if not snippets:
        print("No snippets saved.")
    for name in snippets:
        print(f"  {name}")

def _load_snippets():
    import json
    if os.path.exists(SNIPPETS_FILE):
        try:
            return json.loads(open(SNIPPETS_FILE).read())
        except Exception:
            pass
    return {}

def _save_snippets(snippets):
    import json
    with open(SNIPPETS_FILE, 'w') as f:
        f.write(json.dumps(snippets, indent=2))
