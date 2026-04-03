import subprocess
import os

# Built-in app aliases
APPS = {
    "notepad":      "notepad.exe",
    "calculator":   "calc.exe",
    "paint":        "mspaint.exe",
    "explorer":     "explorer.exe",
    "cmd":          "cmd.exe",
    "powershell":   "powershell.exe",
    "taskmgr":      "taskmgr.exe",
    "control":      "control.exe",
    "settings":     "ms-settings:",
    "camera":       "microsoft.windows.camera:",
    "calendar":     "outlookcal:",
    "maps":         "bingmaps:",
    "store":        "ms-windows-store:",
    "chrome":       r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":      r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":         "msedge.exe",
    "vlc":          r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "vscode":       r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "word":         r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":        r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":   r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "spotify":      r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe",
    "discord":      r"C:\Users\{user}\AppData\Local\Discord\Update.exe",
    "whatsapp":     r"C:\Users\{user}\AppData\Local\WhatsApp\WhatsApp.exe",
    "telegram":     r"C:\Users\{user}\AppData\Roaming\Telegram Desktop\Telegram.exe",
}

CUSTOM_APPS_FILE = r"D:\custom_apps.txt"

def _resolve(path):
    user = os.environ.get("USERNAME", "User")
    return path.replace("{user}", user)

def _load_custom():
    custom = {}
    if os.path.exists(CUSTOM_APPS_FILE):
        with open(CUSTOM_APPS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    name, path = line.split('=', 1)
                    custom[name.strip().lower()] = path.strip()
    return custom

def open_app(name):
    name = name.lower().strip()
    all_apps = {**APPS, **_load_custom()}

    if name not in all_apps:
        print(f"Unknown app '{name}'. Use 'apps list' to see available apps or 'apps add' to register one.")
        return

    path = _resolve(all_apps[name])

    try:
        if path.endswith(":") or path.startswith("ms-"):
            os.startfile(path)
        elif os.path.exists(path):
            subprocess.Popen([path])
        else:
            subprocess.Popen(path, shell=True)
        print(f"Opened: {name}")
    except Exception as e:
        print(f"Failed to open '{name}': {e}")

def list_apps():
    all_apps = {**APPS, **_load_custom()}
    print("\nAvailable apps:")
    for name in sorted(all_apps):
        print(f"  {name}")

def add_app(name, path):
    custom = _load_custom()
    custom[name.lower()] = path
    with open(CUSTOM_APPS_FILE, 'w') as f:
        for k, v in custom.items():
            f.write(f"{k} = {v}\n")
    print(f"App '{name}' registered -> {path}")

def remove_app(name):
    custom = _load_custom()
    name = name.lower()
    if name in custom:
        del custom[name]
        with open(CUSTOM_APPS_FILE, 'w') as f:
            for k, v in custom.items():
                f.write(f"{k} = {v}\n")
        print(f"App '{name}' removed.")
    else:
        print(f"'{name}' not found in custom apps.")
