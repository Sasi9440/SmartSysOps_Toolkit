import subprocess
import sys

def _get_volume_interface():
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def set_volume(level):
    try:
        _get_volume_interface().SetMasterVolumeLevelScalar(max(0.0, min(1.0, int(level) / 100)), None)
        print(f"Volume set to {level}%")
    except Exception:
        try:
            subprocess.run(["powershell", "-Command",
                f"(New-Object -ComObject WScript.Shell).SendKeys([char]174 * 50); "
                f"$vol = {int(level)}; "
                "$wsh = New-Object -ComObject WScript.Shell; "
                "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public class Vol { [DllImport(\"winmm.dll\")] public static extern int waveOutSetVolume(IntPtr h, uint v); }'; "
                f"[Vol]::waveOutSetVolume([IntPtr]::Zero, [uint](($vol / 100) * 0xFFFF) * 0x10001)"],
                capture_output=True)
            print(f"Volume set to {level}%")
        except Exception as e:
            print(f"Volume error: {e}")

def get_volume():
    try:
        vol = _get_volume_interface().GetMasterVolumeLevelScalar()
        print(f"Current volume: {int(vol * 100)}%")
    except Exception:
        try:
            result = subprocess.run(["powershell", "-Command",
                "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public class Vol { [DllImport(\"winmm.dll\")] public static extern int waveOutGetVolume(IntPtr h, out uint v); }'; "
                "$v = 0; [Vol]::waveOutGetVolume([IntPtr]::Zero, [ref]$v); ($v -band 0xFFFF) * 100 / 0xFFFF"],
                capture_output=True, text=True)
            val = result.stdout.strip().split('.')[0]
            print(f"Current volume: {val}%" if val else "Could not get volume")
        except Exception as e:
            print(f"Volume error: {e}")

def set_brightness(level):
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(int(level))
        print(f"Brightness set to {level}%")
    except Exception as e:
        print(f"Brightness error: {e}")

def get_brightness():
    try:
        import screen_brightness_control as sbc
        b = sbc.get_brightness()
        print(f"Current brightness: {b}%")
    except Exception as e:
        print(f"Brightness error: {e}")

def wifi(action):
    action = action.lower()
    if action == "on":
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "enable"], check=True)
        print("WiFi enabled.")
    elif action == "off":
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disable"], check=True)
        print("WiFi disabled.")
    elif action == "status":
        result = subprocess.run(["netsh", "interface", "show", "interface", "Wi-Fi"],
                                capture_output=True, text=True)
        print(result.stdout)
    elif action == "list":
        result = subprocess.run(["netsh", "wlan", "show", "networks"],
                                capture_output=True, text=True)
        print(result.stdout)
    else:
        print("Usage: wifi on | off | status | list")

def bluetooth(action):
    action = action.lower()
    if action in ("on", "off"):
        state = "enable" if action == "on" else "disable"
        result = subprocess.run(
            ["powershell", "-Command",
             f"Get-PnpDevice | Where-Object {{$_.FriendlyName -like '*Wireless Bluetooth*' -or $_.FriendlyName -like '*Intel*Bluetooth*'}} | {state.capitalize()}-PnpDevice -Confirm:$false"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"Bluetooth {action}.")
        else:
            err = result.stderr.strip()
            if "Access" in err or "privilege" in err.lower():
                print("Bluetooth requires Administrator. Right-click terminal -> Run as Administrator.")
            else:
                print(f"Bluetooth error: {err[:200] if err else 'Unknown error'}")
    elif action == "status":
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-PnpDevice | Where-Object {$_.FriendlyName -like '*Wireless Bluetooth*' -or $_.FriendlyName -like '*Intel*Bluetooth*'} | Select-Object Status, FriendlyName | Format-Table -AutoSize"],
            capture_output=True, text=True
        )
        print(result.stdout.strip() or "Bluetooth device not found.")
    else:
        print("Usage: bluetooth on | off | status")

def mute():
    try:
        volume = _get_volume_interface()
        current = volume.GetMute()
        volume.SetMute(not current, None)
        print(f"Mute {'ON' if not current else 'OFF'}")
    except Exception as e:
        print(f"Mute error: {e}")

def shutdown():
    confirm = input("Shutdown the computer? (yes/no): ")
    if confirm.lower() == "yes":
        subprocess.run(["shutdown", "/s", "/t", "5"])
        print("Shutting down in 5 seconds...")

def restart():
    confirm = input("Restart the computer? (yes/no): ")
    if confirm.lower() == "yes":
        subprocess.run(["shutdown", "/r", "/t", "5"])
        print("Restarting in 5 seconds...")

def sleep():
    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    print("Going to sleep...")

def lock():
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    print("Screen locked.")

def battery():
    result = subprocess.run(
        ["powershell", "-Command",
         "(Get-WmiObject Win32_Battery).EstimatedChargeRemaining"],
        capture_output=True, text=True
    )
    val = result.stdout.strip()
    print(f"Battery: {val}%" if val else "No battery info (desktop?)")

def disk_usage():
    import shutil
    total, used, free = shutil.disk_usage("D:\\")
    gb = 1024 ** 3
    print(f"D:\\ Disk Usage:")
    print(f"  Total : {total / gb:.2f} GB")
    print(f"  Used  : {used  / gb:.2f} GB")
    print(f"  Free  : {free  / gb:.2f} GB")

def network_info():
    import socket
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print(f"Hostname : {hostname}")
    print(f"Local IP : {ip}")
    result = subprocess.run(["powershell", "-Command",
        "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Sort-Object RouteMetric | Select-Object -First 1).NextHop"],
        capture_output=True, text=True)
    gw = result.stdout.strip()
    print(f"Gateway  : {gw if gw else 'N/A'}")
    ping = subprocess.run(["ping", "-n", "1", "8.8.8.8"], capture_output=True, text=True)
    print(f"Internet : {'Online' if ping.returncode == 0 else 'Offline'}")

def sysinfo():
    import platform, psutil
    print(f"  OS       : {platform.system()} {platform.release()} ({platform.version()})")
    print(f"  Machine  : {platform.machine()}")
    print(f"  CPU      : {platform.processor()}")
    print(f"  CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical")
    print(f"  CPU Use  : {psutil.cpu_percent(interval=1)}%")
    ram = psutil.virtual_memory()
    print(f"  RAM      : {ram.used / 1024**3:.1f} GB / {ram.total / 1024**3:.1f} GB ({ram.percent}%)")
    uptime = psutil.boot_time()
    import datetime
    up = datetime.datetime.now() - datetime.datetime.fromtimestamp(uptime)
    print(f"  Uptime   : {str(up).split('.')[0]}")

def list_ips():
    import socket
    result = subprocess.run(["powershell", "-Command",
        "Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4'} | Select-Object InterfaceAlias, IPAddress | Format-Table -AutoSize"],
        capture_output=True, text=True)
    print(result.stdout.strip())

def ps_list():
    import psutil
    print(f"  {'PID':>6}  {'CPU%':>5}  {'MEM%':>5}  NAME")
    print(f"  {'-'*6}  {'-'*5}  {'-'*5}  {'-'*30}")
    procs = sorted(psutil.process_iter(['pid','name','cpu_percent','memory_percent']),
                   key=lambda p: p.info['name'] or '')
    for p in procs:
        try:
            print(f"  {p.info['pid']:>6}  {p.info['cpu_percent']:>5.1f}  {p.info['memory_percent']:>5.1f}  {p.info['name']}")
        except Exception:
            pass

def kill_proc(target):
    import psutil
    killed = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if str(p.info['pid']) == target or p.info['name'].lower() == target.lower():
                p.kill()
                killed.append(f"{p.info['name']} (PID {p.info['pid']})")
        except Exception:
            pass
    print(f"Killed: {', '.join(killed)}" if killed else f"No process found: {target}")

def top_procs(n=10):
    import psutil
    psutil.cpu_percent(interval=0.5)
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(p.info)
        except Exception:
            pass
    print(f"  Top {n} by CPU:")
    print(f"  {'PID':>6}  {'CPU%':>5}  {'MEM%':>5}  NAME")
    for p in sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:n]:
        print(f"  {p['pid']:>6}  {p['cpu_percent']:>5.1f}  {p['memory_percent']:>5.1f}  {p['name']}")

def clip_copy(text):
    subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{text}'"])
    print(f"Copied to clipboard.")

def clip_paste():
    result = subprocess.run(["powershell", "-Command", "Get-Clipboard"],
                            capture_output=True, text=True)
    print(result.stdout.strip() or "(clipboard is empty)")

def remind(seconds, message):
    import threading
    def _fire():
        import time
        time.sleep(int(seconds))
        subprocess.run(["powershell", "-Command",
            f"Add-Type -AssemblyName System.Windows.Forms; "
            f"[System.Windows.Forms.MessageBox]::Show('{message}', 'Reminder')"])
    threading.Thread(target=_fire, daemon=True).start()
    print(f"Reminder set for {seconds}s: {message}")
