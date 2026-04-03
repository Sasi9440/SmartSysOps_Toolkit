# System Commander

A CLI tool to manage files, system settings, and apps — all from one place.
File operations are **restricted to D:\ drive only**.

---

## Demo

> 📹 Demo videos are in the [`demos/`](./demos) folder

| Feature | Video |
|---|---|
| File Operations | `demos/file_ops.mp4` |
| AI Code Generator | `demos/ai_gen.mp4` |
| System Controls | `demos/system.mp4` |
| Unique Features | `demos/unique.mp4` |

---

## Setup

```bash
pip install -r requirements.txt
python main.py
```

> Run as Administrator for WiFi, Bluetooth, and brightness controls to work properly.

---

## Commands

### File Operations
All paths are relative to `D:\`

| Command | Description |
|---|---|
| `create file notes.txt` | Create a file |
| `create folder myproject` | Create a folder |
| `delete notes.txt` | Delete file or folder |
| `move notes.txt myproject/notes.txt` | Move a file |
| `rename notes.txt renamed.txt` | Rename a file |
| `copy notes.txt backup.txt` | Copy a file |
| `list` | List D:\ root |
| `list myproject` | List a subfolder |
| `read notes.txt` | Print file contents |
| `write notes.txt Hello World` | Write text to file |

### System Controls

| Command | Description |
|---|---|
| `volume 70` | Set volume to 70% |
| `volume` | Show current volume |
| `brightness 50` | Set brightness to 50% |
| `brightness` | Show current brightness |
| `mute` | Toggle mute on/off |
| `wifi on` | Enable WiFi |
| `wifi off` | Disable WiFi |
| `wifi status` | Show WiFi status |
| `wifi list` | List nearby networks |
| `bluetooth on` | Enable Bluetooth |
| `bluetooth off` | Disable Bluetooth |
| `bluetooth status` | Show Bluetooth status |
| `battery` | Show battery percentage |
| `lock` | Lock the screen |
| `sleep` | Put PC to sleep |
| `restart` | Restart PC |
| `shutdown` | Shutdown PC |

### App Launcher

| Command | Description |
|---|---|
| `open chrome` | Open Chrome |
| `open notepad` | Open Notepad |
| `open vlc` | Open VLC |
| `apps list` | List all known apps |
| `apps add myapp C:\path\to\app.exe` | Register a custom app |
| `apps remove myapp` | Remove a custom app |

Built-in apps: `notepad`, `calculator`, `paint`, `explorer`, `cmd`, `powershell`,
`taskmgr`, `control`, `settings`, `chrome`, `firefox`, `edge`, `vlc`, `vscode`,
`word`, `excel`, `powerpoint`, `spotify`, `discord`, `whatsapp`, `telegram`, `camera`

---

## Notes
- WiFi/Bluetooth controls require **Administrator** privileges
- Brightness control works on laptops with supported display drivers
- Custom apps are saved to `D:\custom_apps.txt`
- No access outside of `D:\` is allowed for file operations
