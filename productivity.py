import os
import json
import threading
import time

NOTES_FILE  = "D:\\notes.json"
TODO_FILE   = "D:\\todo.json"
SCHED_FILE  = "D:\\schedule.json"

# --- Notes ---

def note_add(text):
    notes = _load(NOTES_FILE, [])
    import datetime
    notes.append({"id": len(notes)+1, "text": text, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    _save(NOTES_FILE, notes)
    print(f"Note #{len(notes)} saved.")

def note_list():
    notes = _load(NOTES_FILE, [])
    if not notes:
        print("No notes.")
    for n in notes:
        print(f"  [{n['id']}] {n['time']}  {n['text']}")

def note_clear():
    _save(NOTES_FILE, [])
    print("All notes cleared.")

# --- Todo ---

def todo_add(task):
    todos = _load(TODO_FILE, [])
    todos.append({"id": len(todos)+1, "task": task, "done": False})
    _save(TODO_FILE, todos)
    print(f"Task #{len(todos)} added.")

def todo_list():
    todos = _load(TODO_FILE, [])
    if not todos:
        print("No tasks.")
    for t in todos:
        status = "✓" if t["done"] else "○"
        print(f"  [{t['id']}] {status} {t['task']}")

def todo_done(id_):
    todos = _load(TODO_FILE, [])
    for t in todos:
        if t["id"] == int(id_):
            t["done"] = True
            _save(TODO_FILE, todos)
            print(f"Task #{id_} marked done.")
            return
    print(f"Task #{id_} not found.")

def todo_remove(id_):
    todos = _load(TODO_FILE, [])
    todos = [t for t in todos if t["id"] != int(id_)]
    _save(TODO_FILE, todos)
    print(f"Task #{id_} removed.")

# --- Encrypt / Decrypt ---

def encrypt_file(name, password):
    from file_ops import safe_path
    p = safe_path(name)
    data = open(p, 'rb').read()
    key = _derive_key(password)
    encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    out = p + ".enc"
    open(out, 'wb').write(encrypted)
    print(f"Encrypted: {out}")

def decrypt_file(name, password):
    from file_ops import safe_path
    p = safe_path(name)
    data = open(p, 'rb').read()
    key = _derive_key(password)
    decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    out = p.replace(".enc", ".dec") if p.endswith(".enc") else p + ".dec"
    open(out, 'wb').write(decrypted)
    print(f"Decrypted: {out}")

def _derive_key(password):
    import hashlib
    return hashlib.sha256(password.encode()).digest()

# --- Scheduler ---

_sched_thread = None

def schedule_add(time_str, command):
    scheds = _load(SCHED_FILE, [])
    id_ = max((s["id"] for s in scheds), default=0) + 1
    scheds.append({"id": id_, "time": time_str, "command": command})
    _save(SCHED_FILE, scheds)
    print(f"Scheduled #{id_}: '{command}' at {time_str} daily.")
    _ensure_scheduler()

def schedule_list():
    scheds = _load(SCHED_FILE, [])
    if not scheds:
        print("No scheduled commands.")
    for s in scheds:
        print(f"  [{s['id']}] {s['time']}  {s['command']}")

def schedule_remove(id_):
    scheds = _load(SCHED_FILE, [])
    scheds = [s for s in scheds if s["id"] != int(id_)]
    _save(SCHED_FILE, scheds)
    print(f"Schedule #{id_} removed.")

def _ensure_scheduler():
    global _sched_thread
    if _sched_thread and _sched_thread.is_alive():
        return
    _sched_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    _sched_thread.start()

def _scheduler_loop():
    import datetime
    fired = set()
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        scheds = _load(SCHED_FILE, [])
        for s in scheds:
            key = (s["id"], now)
            if s["time"] == now and key not in fired:
                fired.add(key)
                print(f"\n[Scheduler] Running: {s['command']}")
                from main import handle
                handle(s["command"])
        # Clear fired keys from previous minutes
        fired = {k for k in fired if k[1] == now}
        time.sleep(30)

# --- Helpers ---

def _load(path, default):
    if os.path.exists(path):
        try:
            return json.loads(open(path).read())
        except Exception:
            pass
    return default

def _save(path, data):
    with open(path, 'w') as f:
        f.write(json.dumps(data, indent=2))
