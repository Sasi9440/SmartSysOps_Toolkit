# SmartSysOps Toolkit

A powerful AI-powered CLI toolkit to manage files, system settings, processes, and apps — all from one place.
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

## Features

- 🤖 **AI Code Generator** — Generate code into any file using Groq AI
- 📁 **File Operations** — Create, delete, move, copy, zip, search and more
- ⚙️ **System Controls** — Volume, brightness, WiFi, Bluetooth, battery
- 📊 **System Monitor** — Live CPU/RAM, processes, network speed, health score
- 🔐 **Security** — File encryption, password checker, restricted to D:\ only
- 📝 **Productivity** — Notes, todo, scheduler, reminders, pomodoro timer
- 🛠️ **Dev Tools** — HTTP requests, regex tester, port scanner, JSON tools
- 🎨 **Unique Features** — Matrix rain, ASCII banner, morse code, QR generator
- 🌐 **Network Tools** — GeoIP, DNS lookup, speedtest, ping, public IP
- 📦 **100+ Commands** across all categories

---

## Setup

```bash
pip install -r requirements.txt
python main.py
```

> Run as Administrator for WiFi, Bluetooth, and brightness controls to work properly.

---

## Quick Start

```
>> ai setkey <your_groq_api_key>
>> ai gen myfolder/app.py write a python calculator
>> run myfolder/app.py
```

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
| `search report` | Find files by name |
| `tree myproject` | Show folder tree |
| `zip myproject backup.zip` | Zip a folder |
| `hash notes.txt` | MD5 & SHA256 of file |

### AI Code Generator

| Command | Description |
|---|---|
| `ai setkey <key>` | Save your Groq API key |
| `ai gen <file> <prompt>` | Generate code into a file |
| `ai ask <prompt>` | Ask AI anything |

### System Controls

| Command | Description |
|---|---|
| `volume 70` | Set volume to 70% |
| `brightness 50` | Set brightness to 50% |
| `mute` | Toggle mute on/off |
| `wifi on/off/status/list` | WiFi control |
| `bluetooth on/off/status` | Bluetooth control |
| `battery` | Show battery percentage |
| `sysinfo` | CPU, RAM, OS, uptime |
| `dashboard` | Full system overview |
| `lock` | Lock the screen |
| `sleep` | Put PC to sleep |
| `restart` | Restart PC |
| `shutdown` | Shutdown PC |

### Productivity

| Command | Description |
|---|---|
| `note add <text>` | Save a quick note |
| `todo add <task>` | Add a task |
| `remind 60 meeting` | Popup reminder after 60s |
| `schedule 09:00 note add standup` | Daily scheduled command |
| `pomodoro` | Start pomodoro timer |
| `timer 300 break` | Countdown timer |

### Unique & Fun

| Command | Description |
|---|---|
| `matrix` | Matrix digital rain |
| `banner Hello` | ASCII art banner |
| `morse hello` | Play morse code audio |
| `qrgen https://github.com` | Generate ASCII QR code |
| `joke` | Random dad joke |
| `fact` | Random interesting fact |
| `brain` | Mental math quiz |

---

## Notes
- WiFi/Bluetooth controls require **Administrator** privileges
- Brightness control works on laptops with supported display drivers
- All file operations are restricted to `D:\` — no access to other drives
- API key is stored securely in `.env` (never committed to git)
