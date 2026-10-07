#!/usr/bin/env python3
"""
FIRDHAN AGENT — AI + FULL WINDOWS ASSISTANT 2026
MULTI TASKING GUI assistant. Cyberpunk theme.
Features: OpenRouter AI Chat, Full Windows Control, WSL Auto-Shortcut, Persona Editor.
"""

import os
import sys
import re
import json
import shutil
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error
import random
#INI APIKEYS NGASAL YA GAEEESSS
API_KEYS = [
  
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
    "YOUR APIKEYS",
]

# Model gratis TERAVALIDASI — di-fetch live dari OpenRouter saat startup.
# (model lama seperti llama-3.3-70b:free / mistral-small:free sudah tidak free lagi → 404)
FALLBACK_FREE_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "openrouter/free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "nvidia/nemotron-3.5-lightning:free",
    "thinkingmachines/inkling:free",
    "inclusionai/ling-3.1-flash",
    "inclusionai/ling-3.0-flash-sante:free",
    "dots-studio/dots-3-note-preview:free",
    "liquid/lfm-2.5-2.6b:free",
    "poolside/laguna-s-2.1:free",
    "poolside/laguna-xs-2.1:free",
    "cohere/north-mini-code:free",
    "apodex/apodex-1.1-mini:free",
]

# Model yang pernah error (403 agentic harness / 404 tidak free / 400 invalid)
# tidak akan pernah dipakai lagi selama sesi berjalan.
BLACKLISTED_MODELS = set()


def load_free_models():
    """Ambil daftar model gratis terbaru dari API OpenRouter (cache 24 jam + fallback)."""
    cache = Path.home() / ".firdhan_agent" / "free_models.json"
    try:
        if cache.exists():
            cached = json.loads(cache.read_text(encoding="utf-8"))
            age = time.time() - cached.get("fetched_at", 0)
            models = [m for m in cached.get("models", []) if m not in BLACKLISTED_MODELS]
            if age < 86400 and models:
                return models
    except Exception:
        pass
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={"User-Agent": "FIRDHAN-AGENT/2.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        free = []
        for m in data.get("data", []):
            p = m.get("pricing", {})
            mid = m.get("id", "")
            if p.get("prompt") == "0" and p.get("completion") == "0" and ":free" in mid:
                free.append(mid)
        # buang model audio / safety / yang gated ke agentic harness
        skip = ("lyria", "content-safety", "inkling-small")
        free = [f for f in free if not any(x in f for x in skip)]
        free = [f for f in free if f not in BLACKLISTED_MODELS]
        if free:
            try:
                cache.write_text(json.dumps(
                    {"fetched_at": time.time(), "models": free}), encoding="utf-8")
            except Exception:
                pass
            return free
    except Exception:
        pass
    return [m for m in FALLBACK_FREE_MODELS if m not in BLACKLISTED_MODELS]

_api_index = 0
_model_index = 0

# ═══════════════════════════════════════════════════════
# OPTIONAL DEPENDENCIES
# ═══════════════════════════════════════════════════════
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from PIL import ImageGrab, Image as PILImage, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# ═══════════════════════════════════════════════════════
# CONFIG & PATHS
# ═══════════════════════════════════════════════════════
CONFIG_DIR = Path.home() / ".firdhan_agent"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "chat_history.json"
for p in (CONFIG_DIR,):
    p.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "OPENROUTER_API_KEY": "",  # will be set by rotation
    "OPENROUTER_MODEL": "",    # will be set by rotation
    "PERSONA": "",
    "SYSTEM_PROMPT": "You are FIRDHAN AI, a helpful local Windows assistant. You help users with computer tasks, answer questions, and can execute Windows commands when asked. Respond concisely and helpfully. If user asks in Indonesian, reply in Indonesian."
}

# Load or create config
if CONFIG_FILE.exists():
    try:
        USER_CONFIG = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except:
        USER_CONFIG = {}
else:
    USER_CONFIG = {}
# Merge with defaults
for k, v in DEFAULT_CONFIG.items():
    if k not in USER_CONFIG:
        USER_CONFIG[k] = v
CONFIG = USER_CONFIG


def save_config():
    CONFIG_FILE.write_text(json.dumps(CONFIG, indent=2), encoding="utf-8")


# ═══════════════════════════════════════════════════════
# THEME
# ═══════════════════════════════════════════════════════
class Theme:
    BG = "#000000"          # Pure black
    PANEL = "#000000"       # Black panels
    PANEL2 = "#000000"
    ACCENT = "#00ff00"      # Hacker green
    ACCENT_DIM = "#008000"
    GREEN = "#00ff00"
    RED = "#ff0000"
    ORANGE = "#ff8000"
    PURPLE = "#ff00ff"
    YELLOW = "#ffff00"
    CYAN = "#00ffff"
    TEXT = "#00ff00"        # Green text
    MUTED = "#006000"
    BORDER = "#003300"
    INPUT_BG = "#000000"
    USER_COLOR = "#00ff00"
    AI_COLOR = "#00ff00"
class OpenRouterClient:
    """Rotasi key + model dengan retry otomatis.
    - Key 401 (User not found)  → key diblacklist permanen sesi ini
    - Model 403/404/400         → model diblacklist, lanjut model lain
    - Respons kosong            → retry model berikutnya
    """

    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    MAX_TRIES = 14

    def __init__(self):
        self.dead_keys = set()     # API key yang 401
        self.bad_models = set()    # model yang 400/403/404
        self._models = None

    # ── model list ──
    def get_models(self):
        global BLACKLISTED_MODELS
        BLACKLISTED_MODELS |= self.bad_models
        models = [m for m in load_free_models() if m not in self.bad_models]
        return models or [m for m in FALLBACK_FREE_MODELS if m not in self.bad_models]

    def get_current_credentials(self):
        global _api_index, _model_index
        models = self.get_models()
        alive_keys = [k for k in API_KEYS if k not in self.dead_keys] or list(API_KEYS)
        if not models:
            return "", ""
        key = alive_keys[_api_index % len(alive_keys)]
        model = models[_model_index % len(models)]
        _api_index += 1
        _model_index += 1
        return key, model

    # ── single request ──
    def _request(self, api_key, model, messages, temperature, max_tokens):
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.API_URL, data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://firdhan.local",
                "X-Title": "FIRDHAN AGENT"
            },
            method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return (result["choices"][0]["message"].get("content") or "").strip()

    # ── main chat dengan retry penuh ──
    def chat(self, messages, temperature=0.7, max_tokens=2048):
        errors = []
        for _attempt in range(self.MAX_TRIES):
            api_key, model = self.get_current_credentials()
            if not api_key:
                return False, "API Key belum diatur. Buka AI CONFIG."
            try:
                content = self._request(api_key, model, messages, temperature, max_tokens)
                if content:
                    return True, content
                self.bad_models.add(model)   # model aneh (respons kosong), jangan dipakai lagi
                errors.append(f"{model}: respons kosong")
            except urllib.error.HTTPError as e:
                try:
                    body = e.read().decode(errors="replace")
                except Exception:
                    body = ""
                code = e.code
                if code == 401:
                    self.dead_keys.add(api_key)
                    errors.append("401: API key tidak valid (User not found)")
                elif code == 403 and "agentic harness" in body:
                    self.bad_models.add(model)
                    errors.append(f"403: {model} butuh agentic harness")
                elif code in (400, 404):
                    self.bad_models.add(model)
                    errors.append(f"{code}: {model} tidak valid / tidak free lagi")
                elif code == 429:
                    errors.append("429: rate limit, rotasi key/model...")
                elif code in (500, 502, 503):
                    errors.append(f"{code}: server OpenRouter error")
                else:
                    errors.append(f"HTTP {code}: {body[:100]}")
            except Exception as e:
                errors.append(str(e)[:100])

        uniq = list(dict.fromkeys(errors))
        return False, (
            f"Semua percobaan ({self.MAX_TRIES}x) gagal. Ringkasan:" + chr(10)
            + chr(10).join(f" • {e}" for e in uniq[:8])
            + chr(10) + chr(10) + "Tips: cek koneksi internet / key di AI CONFIG, atau tunggu rate limit reset."
        )

class ChatStore:
    def __init__(self):
        self.messages = []
        self.load()

    def load(self):
        if HISTORY_FILE.exists():
            try:
                self.messages = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            except:
                self.messages = []
        else:
            self.messages = []

    def save(self):
        HISTORY_FILE.write_text(json.dumps(self.messages[-100:], indent=2), encoding="utf-8")

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        self.save()

    def clear(self):
        self.messages = []
        self.save()

    def build_prompt(self, user_msg):
        """Build messages array with system prompt + persona."""
        system = CONFIG.get("SYSTEM_PROMPT", DEFAULT_CONFIG["SYSTEM_PROMPT"])
        persona = CONFIG.get("PERSONA", "").strip()
        if persona:
            system += f"\n\n[PERSONA]\n{persona}"

        msgs = [{"role": "system", "content": system}]
        # Add last 20 messages for context
        for m in self.messages[-20:]:
            msgs.append(m)
        msgs.append({"role": "user", "content": user_msg})
        return msgs


# ═══════════════════════════════════════════════════════
# COMMAND ENGINE (FULL WINDOWS)
# ═══════════════════════════════════════════════════════
class CommandEngine:
    VS_CODE_PATH = r"C:\Users\MAJA\AppData\Local\Programs\Microsoft VS Code\Code.exe"

    APP_MAP = {
        "chrome": ["chrome", "google chrome", "browser", "chromium", "edge"],
        "word": ["winword", "microsoft word", "ms word"],
        "excel": ["excel", "microsoft excel", "spreadsheet"],
        "powerpoint": ["powerpnt", "microsoft powerpoint", "ppt"],
        "notepad": ["notepad", "text editor"],
        "notepad++": ["notepad++"],
        "paint": ["mspaint", "paint", "drawing"],
        "calculator": ["calc", "calculator", "kalkulator"],
        "cmd": ["cmd", "command prompt", "dos", "terminal"],
        "powershell": ["powershell", "ps", "posh"],
        "explorer": ["explorer", "file explorer", "my computer"],
        "settings": ["ms-settings:", "settings", "pengaturan", "windows settings"],
        "control": ["control", "control panel"],
        "taskmanager": ["taskmgr", "task manager"],
        "spotify": ["spotify"],
        "discord": ["discord"],
        "steam": ["steam"],
        "vlc": ["vlc", "media player"],
        "obs": ["obs", "obs studio"],
        "zoom": ["zoom"],
        "teams": ["teams", "microsoft teams"],
        "outlook": ["outlook"],
        "edge": ["msedge", "microsoft edge"],
        "firefox": ["firefox"],
        "opera": ["opera"],
        "brave": ["brave"],
        "photoshop": ["photoshop"],
        "illustrator": ["illustrator"],
        "premiere": ["premiere", "premiere pro"],
        "after effects": ["afterfx"],
        "blender": ["blender"],
        "unity": ["unity"],
        "eclipse": ["eclipse"],
        "intellij": ["idea", "intellij"],
        "pycharm": ["pycharm"],
        "postman": ["postman"],
        "figma": ["figma"],
        "github desktop": ["github"],
        "docker desktop": ["docker"],
        "virtualbox": ["virtualbox"],
        "vmware": ["vmware"],
        "putty": ["putty"],
        "winscp": ["winscp"],
        "filezilla": ["filezilla"],
        "7z": ["7z", "7zip", "seven zip"],
        "winrar": ["winrar"],
        "ccleaner": ["ccleaner"],
        "cpu-z": ["cpu-z"],
        "gpu-z": ["gpu-z"],
        "msinfo32": ["msinfo32", "system information"],
        "dxdiag": ["dxdiag", "directx"],
        "regedit": ["regedit", "registry editor"],
        "services": ["services.msc", "services"],
        "event viewer": ["eventvwr", "event viewer"],
        "device manager": ["devmgmt.msc", "device manager"],
        "disk management": ["diskmgmt.msc", "disk management"],
        "performance monitor": ["perfmon"],
        "resource monitor": ["resmon"],
        "character map": ["charmap"],
        "snipping tool": ["snippingtool", "snip"],
        "magnifier": ["magnify"],
        "narrator": ["narrator"],
        "on-screen keyboard": ["osk"],
        "remote desktop": ["mstsc", "rdp"],
        "xampp": ["xampp-control"],
    }

    ALIAS_TO_EXE = {}
    for exe, aliases in APP_MAP.items():
        for a in aliases:
            ALIAS_TO_EXE[a] = exe

    @classmethod
    def resolve_app(cls, text: str):
        t = text.lower()
        for alias, exe in cls.ALIAS_TO_EXE.items():
            if alias in t:
                return exe
        words = re.findall(r'\b\w+\b', t)
        for w in words:
            if w in cls.ALIAS_TO_EXE:
                return cls.ALIAS_TO_EXE[w]
        return None

    @classmethod
    def execute(cls, text: str, log=None):
        text = text.strip()
        if not text:
            return False, "Perintah kosong."
        t = text.lower()

        if any(x in t for x in ["vscode", "visual studio code", "vs code", "code editor"]):
            return cls._vscode(log)
        if any(x in t for x in ["ubuntu", "wsl", "linux", "bash"]):
            return cls._wsl(log)
        if any(x in t for x in ["webcam", "kamera", "camera", "nyalakan kamera", "buka kamera"]):
            return cls._webcam(log)
        if any(x in t for x in ["screenshot", "tangkap layar", "ss", "screen capture", "print screen"]):
            return cls._screenshot(log)
        if any(x in t for x in ["clipboard", "paste", "isi clipboard", "show clipboard"]):
            return cls._clipboard(log)
        if any(x in t for x in ["matikan laptop", "shutdown", "turn off", "mati"]):
            return cls._confirm_power("shutdown", log)
        if any(x in t for x in ["restart", "reboot", "mulai ulang"]):
            return cls._confirm_power("restart", log)
        if any(x in t for x in ["sleep", "tidur", "suspend"]):
            return cls._confirm_power("sleep", log)
        if "hibernate" in t:
            return cls._confirm_power("hibernate", log)
        if any(x in t for x in ["logoff", "logout", "keluar"]):
            return cls._confirm_power("logoff", log)
        if any(x in t for x in ["lock", "kunci layar", "lock screen"]):
            return cls._run(["rundll32.exe", "user32.dll,LockWorkStation"], "Layar dikunci.", log)
        if "mute" in t or "bisukan" in t:
            return cls._volume_mute(log)
        if any(x in t for x in ["unmute", "nyalakan suara"]):
            return cls._volume_unmute(log)
        vol_match = re.search(r'(?:volume|suara|vol)\s+(\d+)', t)
        if vol_match:
            return cls._volume_set(int(vol_match.group(1)), log)
        bright_match = re.search(r'(?:brightness|kecerahan|cahaya)\s+(\d+)', t)
        if bright_match:
            return cls._brightness(int(bright_match.group(1)), log)
        if any(x in t for x in ["wifi", "jaringan", "network", "wireless"]):
            if "connect" in t or "sambung" in t or "hubung" in t:
                ssid = re.search(r'(?:ke|to)\s+(\w+)', t)
                return cls._wifi_connect(ssid.group(1) if ssid else None, log)
            if "disconnect" in t or "putus" in t:
                return cls._wifi_disconnect(log)
            return cls._wifi_list(log)
        if any(x in t for x in ["battery", "baterai", "daya", "power status"]):
            return cls._battery(log)
        if any(x in t for x in ["tasklist", "daftar proses", "running apps", "processes"]):
            return cls._tasklist(log)
        kill_match = re.search(r'(?:kill|matikan proses|tutup proses|end task)\s+(.+)', t)
        if kill_match:
            return cls._kill(kill_match.group(1).strip(), log)
        if any(x in t for x in ["empty trash", "empty recycle", "kosongkan recycle", "kosongkan tong sampah"]):
            return cls._empty_recycle(log)
        eject_match = re.search(r'(?:eject|safely remove|lepas|cabut)\s+(?:drive\s+)?([a-z]:)', t)
        if eject_match:
            return cls._eject(eject_match.group(1).upper(), log)
        if any(x in t for x in ["waktu", "jam", "tanggal", "time", "date", "sekarang"]):
            now = datetime.now().strftime("%A, %d %B %Y — %H:%M:%S")
            return True, f"⏰ {now}"
        if any(x in t for x in ["ip address", "ip saya", "my ip", "alamat ip"]):
            return cls._ip_address(log)
        file_match = re.search(r'(?:buka file|open file|jalankan file)\s+(.+)', t)
        if file_match:
            path = file_match.group(1).strip().strip('"').strip("'")
            return cls._open_file(path, log)
        folder_match = re.search(r'(?:buka folder|open folder|buka direktori|open directory|buka path)\s+(.+)', t)
        if folder_match:
            path = folder_match.group(1).strip().strip('"').strip("'")
            return cls._open_folder(path, log)

        app = cls.resolve_app(t)
        if app:
            return cls._run_app(app, log)

        if os.path.exists(text.strip('"').strip("'")):
            path = text.strip('"').strip("'")
            if os.path.isfile(path):
                return cls._open_file(path, log)
            elif os.path.isdir(path):
                return cls._open_folder(path, log)

        # Run Python script
        python_match = re.search(r'(?:jalankan|run|execute)\\s+python\\s+(.+)', t)
        if python_match:
            path = python_match.group(1).strip().strip('"').strip("'")
            return cls._run_python(path, log)
        return False, (
            "Perintah tidak dikenali.\n\n"
            "Coba:\n"
            "  • buka chrome / vscode / word / excel / notepad / paint\n"
            "  • buka file C:\\Users\\Nama\\file.txt\n"
            "  • buka folder D:\\Projects\n"
            "  • webcam / screenshot / clipboard\n"
            "  • matikan laptop / restart / sleep / lock\n"
            "  • volume 50 / mute / unmute\n"
            "  • kecerahan 70\n"
            "  • wifi / battery / tasklist\n"
            "  • kill notepad\n"
            "  • kosongkan recycle bin"
        )

    @classmethod
    def _run(cls, cmd, success_msg, log=None, shell=False):
        try:
            if shell:
                subprocess.Popen(cmd, shell=True)
            else:
                subprocess.Popen(cmd)
            if log:
                log(success_msg, "success")
            return True, success_msg
        except Exception as e:
            err = f"Error: {e}"
            if log:
                log(err, "error")
            return False, err

    @classmethod
    def _run_app(cls, app, log=None):
        exe = shutil.which(app)
        if exe:
            return cls._run([exe], f"{app} dijalankan.", log)
        return cls._run(["start", "", app], f"{app} dijalankan.", log, shell=True)

    @classmethod
    def _vscode(cls, log=None):
        path = cls.VS_CODE_PATH
        if os.path.exists(path):
            return cls._run([path], "Visual Studio Code dibuka (path absolut).", log)
        exe = shutil.which("code")
        if exe:
            return cls._run([exe], "VS Code dibuka (dari PATH).", log)
        err = "VS Code tidak ditemukan."
        if log:
            log(err, "error")
        return False, err

    @classmethod
    def _wsl(cls, log=None):
        """Auto-WSL: buka cmd langsung masuk WSL home (~)."""
        try:
            subprocess.Popen(["cmd", "/k", "wsl", "~"])
            msg = "WSL dibuka otomatis (cmd /k wsl ~)."
            if log:
                log(msg, "success")
            return True, msg
        except Exception as e:
            err = f"Gagal membuka WSL: {e}"
            if log:
                log(err, "error")
            return False, err
    @classmethod
    def _run_python(cls, path, log=None):
        path = os.path.expandvars(os.path.expanduser(path.strip('"').strip("'")))
        if not os.path.exists(path):
            err = f"File tidak ditemukan: {path}"
            if log:
                log(err, "error")
            return False, err
        try:
            # Run with python.exe
            subprocess.Popen([sys.executable, path], shell=False)
            if log:
                log(f"Python script dijalankan: {path}", "success")
            return True, f"Python script dijalankan: {path}"
        except Exception as e:
            err = f"Gagal menjalankan Python: {e}"
            if log:
                log(err, "error")
            return False, err
    @classmethod
    def _open_file(cls, path, log=None):
        path = os.path.expandvars(os.path.expanduser(path.strip('"').strip("'")))
        if not os.path.exists(path):
            err = f"File tidak ditemukan: {path}"
            if log:
                log(err, "error")
            return False, err
        return cls._run(["start", "", path], f"File dibuka: {path}", log, shell=True)

    @classmethod
    def _open_folder(cls, path, log=None):
        path = os.path.expandvars(os.path.expanduser(path.strip('"').strip("'")))
        if not os.path.exists(path):
            err = f"Folder tidak ditemukan: {path}"
            if log:
                log(err, "error")
            return False, err
        return cls._run(["explorer", path], f"Folder dibuka: {path}", log)

    @classmethod
    def _webcam(cls, log=None):
        if not HAS_CV2:
            msg = "Install opencv-python: pip install opencv-python"
            if log:
                log(msg, "error")
            return False, msg

        def cam_thread():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                if log:
                    log("Webcam tidak terdeteksi.", "error")
                return
            if log:
                log("Webcam aktif. Tekan 'Q' untuk menutup.", "success")
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                h, w = frame.shape[:2]
                cv2.putText(frame, "FIRDHAN CAM // LIVE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 240, 255), 2)
                cv2.putText(frame, datetime.now().strftime("%H:%M:%S"), (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 240, 255), 1)
                cv2.rectangle(frame, (5, 5), (w - 5, h - 5), (0, 240, 255), 2)
                cv2.imshow("FIRDHAN WEBCAM // Tekan Q untuk tutup", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
            if log:
                log("Webcam ditutup.", "info")

        threading.Thread(target=cam_thread, daemon=True).start()
        return True, "Webcam diaktifkan..."

    @classmethod
    def _screenshot(cls, log=None):
        if not HAS_PIL:
            msg = "Install Pillow: pip install Pillow"
            if log:
                log(msg, "error")
            return False, msg
        try:
            path = Path.home() / "Pictures" / f"firdhan_ss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            img = ImageGrab.grab()
            img.save(path)
            msg = f"Screenshot disimpan: {path}"
            if log:
                log(msg, "success")
            os.startfile(path)
            return True, msg
        except Exception as e:
            err = f"Screenshot gagal: {e}"
            if log:
                log(err, "error")
            return False, err

    @classmethod
    def _clipboard(cls, log=None):
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            preview = data[:500] + "..." if len(data) > 500 else data
            msg = f"Clipboard:\n{preview}"
            if log:
                log(msg, "info")
            return True, msg
        except Exception:
            try:
                result = subprocess.run(["powershell", "-command", "Get-Clipboard"], capture_output=True, text=True, timeout=5)
                text = result.stdout.strip()
                preview = text[:500] + "..." if len(text) > 500 else text
                msg = f"Clipboard:\n{preview}"
                if log:
                    log(msg, "info")
                return True, msg
            except Exception as e:
                err = f"Clipboard error: {e}"
                if log:
                    log(err, "error")
                return False, err

    @classmethod
    def _confirm_power(cls, action, log=None):
        labels = {
            "shutdown": ("SHUTDOWN", "Matikan laptop sekarang?", "shutdown /s /t 0"),
            "restart": ("RESTART", "Restart laptop sekarang?", "shutdown /r /t 0"),
            "sleep": ("SLEEP", "Laptop akan sleep.", "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"),
            "hibernate": ("HIBERNATE", "Laptop akan hibernate.", "rundll32.exe powrprof.dll,SetSuspendState Hibernate"),
            "logoff": ("LOGOFF", "Keluar dari Windows?", "shutdown /l")
        }
        title, msg, cmd = labels.get(action, ("?", "?", ""))
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(f"⚠ {title}", msg, icon="warning")
        root.destroy()
        if result:
            if log:
                log(f"{title} diproses...", "success")
            subprocess.call(cmd, shell=True)
            return True, f"{title} dieksekusi."
        return False, f"{title} dibatalkan."

    @classmethod
    def _volume_mute(cls, log=None):
        return cls._run(["powershell", "-c", "(new-object -com wscript.shell).SendKeys([char]173)"], "Volume muted.", log)

    @classmethod
    def _volume_unmute(cls, log=None):
        return cls._run(["powershell", "-c", "(new-object -com wscript.shell).SendKeys([char]173)"], "Volume unmuted.", log)

    @classmethod
    def _volume_set(cls, level, log=None):
        ps = f'''
        Add-Type -TypeDefinition @"
        using System; using System.Runtime.InteropServices;
        [Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        interface IAudioEndpointVolume {{ int SetMasterVolumeLevelScalar(float fLevel, IntPtr pguidEventContext); }}
        [Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        interface IMMDevice {{ int Activate(ref Guid iid, int clsCtx, IntPtr activationParams, [MarshalAs(UnmanagedType.IUnknown)] out object interfacePtr); }}
        [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        interface IMMDeviceEnumerator {{ int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppEndpoint); }}
        [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class MMDeviceEnumerator {{ }}
        var enumerator = new MMDeviceEnumerator();
        IMMDevice device;
        enumerator.GetDefaultAudioEndpoint(0, 1, out device);
        object obj;
        var IID_IAudioEndpointVolume = new Guid("5CDF2C82-841E-4546-9722-0CF74078229A");
        device.Activate(ref IID_IAudioEndpointVolume, 0, IntPtr.Zero, out obj);
        var vol = (IAudioEndpointVolume)obj;
        vol.SetMasterVolumeLevelScalar({level / 100.0}f, IntPtr.Zero);
        "@ -Language CSharp -ReferencedAssemblies System.Runtime.InteropServices
        '''
        return cls._run(["powershell", "-c", ps], f"Volume diatur ke {level}%.", log)

    @classmethod
    def _brightness(cls, level, log=None):
        ps = f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})'
        return cls._run(["powershell", "-c", ps], f"Kecerahan diatur ke {level}%.", log)

    @classmethod
    def _wifi_list(cls, log=None):
        try:
            result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, timeout=10)
            if log:
                log("Daftar WiFi:\n" + result.stdout, "info")
            return True, result.stdout
        except Exception as e:
            return False, str(e)

    @classmethod
    def _wifi_connect(cls, ssid, log=None):
        if not ssid:
            return False, "SSID tidak disebutkan."
        try:
            result = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True, text=True, timeout=15)
            msg = result.stdout or result.stderr
            if log:
                log(msg, "success" if "success" in msg.lower() else "error")
            return True, msg
        except Exception as e:
            return False, str(e)

    @classmethod
    def _wifi_disconnect(cls, log=None):
        try:
            result = subprocess.run(["netsh", "wlan", "disconnect"], capture_output=True, text=True, timeout=10)
            if log:
                log("WiFi disconnected.", "success")
            return True, result.stdout
        except Exception as e:
            return False, str(e)

    @classmethod
    def _battery(cls, log=None):
        if HAS_PSUTIL:
            battery = psutil.sensors_battery()
            if battery:
                msg = f"🔋 Baterai: {battery.percent}% {'(Charging)' if battery.power_plugged else '(On Battery)'}"
                if log:
                    log(msg, "success")
                return True, msg
        try:
            subprocess.run(["powercfg", "/batteryreport"], capture_output=True, text=True, timeout=15)
            if log:
                log("Battery report dibuat.", "info")
            return True, "Battery report dibuat."
        except Exception as e:
            return False, str(e)

    @classmethod
    def _tasklist(cls, log=None):
        try:
            result = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().split("\n")[:30]
            preview = "\n".join(lines) + "\n..."
            if log:
                log(preview, "info")
            return True, result.stdout
        except Exception as e:
            return False, str(e)

    @classmethod
    def _kill(cls, proc_name, log=None):
        if not proc_name.endswith(".exe"):
            proc_name += ".exe"
        try:
            result = subprocess.run(["taskkill", "/im", proc_name, "/f"], capture_output=True, text=True, timeout=10)
            msg = result.stdout or result.stderr
            if log:
                log(msg, "success" if "success" in msg.lower() else "error")
            return True, msg
        except Exception as e:
            return False, str(e)

    @classmethod
    def _empty_recycle(cls, log=None):
        try:
            ps = "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"
            subprocess.run(["powershell", "-c", ps], capture_output=True, text=True, timeout=10)
            msg = "Recycle bin dikosongkan."
            if log:
                log(msg, "success")
            return True, msg
        except Exception as e:
            return False, str(e)

    @classmethod
    def _eject(cls, drive, log=None):
        try:
            ps = f'(New-Object -comObject Shell.Application).Namespace(17).ParseName(\"{drive}\").InvokeVerb(\"Eject\")'
            subprocess.run(["powershell", "-c", ps], capture_output=True, text=True, timeout=10)
            msg = f"Drive {drive} sedang di-eject."
            if log:
                log(msg, "success")
            return True, msg
        except Exception as e:
            return False, str(e)

    @classmethod
    def _ip_address(cls, log=None):
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            msg = f"Hostname: {hostname}\nIP Address: {ip}"
            if log:
                log(msg, "info")
            return True, msg
        except Exception as e:
            return False, str(e)


# ═══════════════════════════════════════════════════════
# API KEY FINDER  (search_apikeys → show_output)
# ═══════════════════════════════════════════════════════
APIKEY_RE = re.compile(r"sk-or-v1-[a-f0-9]{60,72}")


def show_output(text: str, log=None, tag="info"):
    """Tampilkan output ke log yang tersedia (system log / terminal)."""
    if log:
        try:
            log(text, tag)
        except TypeError:
            log(text)
    return text


def search_apikeys(log=None, scan_home=False):
    """Cari API key OpenRouter di environment variables & file konfigurasi umum."""
    hits = []

    # 1) Environment variables
    for k, v in os.environ.items():
        for m in APIKEY_RE.findall(str(v)):
            hits.append(f"[ENV] {k} = {m}")

    # 2) File konfigurasi umum (dangkal & cepat)
    home = Path.home()
    candidates = [
        home / ".firdhan_agent" / "config.json",
        home / ".env",
        home / ".openrouter",
        Path.cwd() / ".env",
        Path.cwd() / "config.json",
        Path.cwd() / "agent.py",
    ]
    if scan_home:
        try:
            for p in home.glob("*"):
                if p.is_file() and p.suffix.lower() in (".txt", ".json", ".env", ".cfg", ".ini"):
                    candidates.append(p)
        except Exception:
            pass

    seen = set()
    for path in candidates:
        try:
            rp = str(path.resolve())
            if rp in seen or not path.exists() or not path.is_file():
                continue
            seen.add(rp)
            text = path.read_text(encoding="utf-8", errors="ignore")
            for m in APIKEY_RE.findall(text):
                hits.append(f"[FILE] {path} -> {m}")
        except Exception:
            continue

    if hits:
        out = f"🔑 API KEYS DITEMUKAN ({len(hits)}):\n" + "\n".join(hits)
        return show_output(out, log=log, tag="success")
    out = "🔑 Tidak ada API key OpenRouter ditemukan di environment/file umum."
    return show_output(out, log=log, tag="warn")


# ═══════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════
# AI ACTION EXECUTOR
# ═══════════════════════════════════════════════════════
def execute_ai_action(text: str, log=None):
    """Check AI response for action commands and execute them."""
    t = text.lower().strip()
    # Patterns for opening apps
    if any(x in t for x in ["buka kalkulator", "open calculator", "jalankan kalkulator"]):
        return CommandEngine.execute("kalkulator", log)
    if any(x in t for x in ["buka notepad", "open notepad", "jalankan notepad"]):
        return CommandEngine.execute("notepad", log)
    if any(x in t for x in ["buka chrome", "open chrome", "jalankan chrome"]):
        return CommandEngine.execute("chrome", log)
    if any(x in t for x in ["buka vs code", "open vs code", "jalankan vs code", "buka vscode", "open vscode"]):
        return CommandEngine.execute("vscode", log)
    if any(x in t for x in ["buka explorer", "open explorer", "jalankan explorer"]):
        return CommandEngine.execute("explorer", log)
    if any(x in t for x in ["buka task manager", "open task manager", "jalankan task manager"]):
        return CommandEngine.execute("taskmanager", log)
    # Add more as needed
    return False, "No action detected"
# ═══════════════════════════════════════════════════════
# MULTI TASKING — deteksi aplikasi & embed jendela asli (win32)
# ═══════════════════════════════════════════════════════
def detect_installed_apps(max_items=36):
    """Deteksi aplikasi yang terinstall: preset umum + shortcut Start Menu (.lnk)."""
    apps = {}  # label -> perintah launch
    presets = [
        ("CMD (Terminal)", "cmd"), ("File Explorer", "explorer"),
        ("Notepad", "notepad"), ("Google Chrome", "chrome"),
        ("Kalkulator", "calc"), ("Paint", "mspaint"),
        ("Task Manager", "taskmgr"), ("Pengaturan", "ms-settings:"),
        ("VS Code", "code"), ("PowerShell", "powershell"),
    ]
    for label, exe in presets:
        try:
            if label == "Google Chrome":
                path = _find_chrome()
                if path:
                    apps[label] = path
            elif exe.endswith(":") or shutil.which(exe) or os.path.exists(exe):
                apps[label] = exe
        except Exception:
            pass
    # Scan Start Menu shortcuts
    start_dirs = [
        Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "Microsoft/Windows/Start Menu/Programs",
        Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    ]
    skip_words = ("uninstall", "unins", "remove", "help", "documentation")
    for sd in start_dirs:
        try:
            if not sd.exists():
                continue
            for lnk in sorted(sd.rglob("*.lnk")):
                name = lnk.stem.strip()
                if not name or len(apps) >= max_items:
                    continue
                if any(w in name.lower() for w in skip_words):
                    continue
                if name not in apps:
                    apps[name] = str(lnk)
        except Exception:
            continue
    return apps


def _find_chrome():
    """Cari chrome.exe di lokasi instalasi standar Windows."""
    cands = []
    for env in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        base = os.environ.get(env, "")
        if base:
            cands.append(os.path.join(base, r"Google\Chrome\Application\chrome.exe"))
    for c in cands:
        if os.path.exists(c):
            return c
    exe = shutil.which("chrome") or shutil.which("chrome.exe")
    return exe


# ── win32 helpers via ctypes (tanpa dependensi tambahan) ──
def _enum_windows():
    """Daftar semua window top-level: [(hwnd, title, pid)]."""
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    out = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def _cb(hwnd, lp):
        if user32.IsWindowVisible(hwnd):
            ln = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(ln + 1)
            user32.GetWindowTextW(hwnd, buf, ln + 1)
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if buf.value.strip():
                out.append((hwnd, buf.value, pid.value))
        return True

    user32.EnumWindows(_cb, 0)
    return out


def _embed_window(hwnd, parent_hwnd, width, height):
    """Reparent jendela aplikasi asli ke dalam frame tkinter.
    Style jendela dibersihkan (caption/thickframe/sysmenu dihapus) agar
    aplikasi seperti Notepad, Paint, bahkan Chrome MAU menyusut mengikuti
    ukuran cell saat di-resize.
    CATATAN: return value SetParent sengaja TIDAK dicek — fungsi itu
    mengembalikan PARENT LAMA (0 = desktop saat sukses), bukan status."""
    import ctypes
    user32 = ctypes.windll.user32
    GWL_STYLE = -16
    WS_CHILD = 0x40000000
    WS_POPUP = 0x80000000
    WS_CAPTION = 0x00C00000
    WS_THICKFRAME = 0x00040000
    WS_SYSMENU = 0x00080000
    WS_MINIMIZEBOX = 0x00020000
    WS_MAXIMIZEBOX = 0x00010000
    style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    style = (style & ~(WS_POPUP | WS_CAPTION | WS_THICKFRAME |
                       WS_SYSMENU | WS_MINIMIZEBOX | WS_MAXIMIZEBOX)) | WS_CHILD
    user32.SetWindowLongW(hwnd, GWL_STYLE, style)
    user32.SetParent(hwnd, parent_hwnd)
    # SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED
    user32.SetWindowPos(hwnd, 0, 0, 0, width, height, 0x0004 | 0x0010 | 0x0020)
    user32.MoveWindow(hwnd, 0, 0, width, height, True)
    return True


def _resize_embedded(hwnd, width, height):
    """Resize jendela yang sudah di-embed agar FILL PENUH area canvas,
    lalu paksa repaint total agar tidak ada bagian hitam/kosong."""
    import ctypes
    user32 = ctypes.windll.user32
    try:
        if hwnd and user32.IsWindow(hwnd):
            user32.MoveWindow(hwnd, 0, 0, max(60, int(width)),
                              max(40, int(height)), True)
            user32.InvalidateRect(hwnd, None, True)   # repaint penuh
            user32.UpdateWindow(hwnd)
            return True
    except Exception:
        pass
    return False


def _unembed_window(hwnd):
    """Lepas kembali jendela (kembalikan ke desktop)."""
    import ctypes
    user32 = ctypes.windll.user32
    GWL_STYLE = -16
    WS_POPUP = 0x80000000
    WS_CHILD = 0x40000000
    try:
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)
        user32.SetWindowLongW(hwnd, GWL_STYLE, (style & ~WS_CHILD) | WS_POPUP)
        user32.SetParent(hwnd, 0)
    except Exception:
        pass


def _focus_window(hwnd):
    """Bawa jendela ke depan agar bisa langsung diketik/dioperasikan."""
    import ctypes
    user32 = ctypes.windll.user32
    try:
        user32.keybd_event(0x12, 0, 0, 0)          # ALT down (bypass foreground lock)
        user32.SetForegroundWindow(hwnd)
        user32.keybd_event(0x12, 0, 2, 0)          # ALT up
        return True
    except Exception:
        return False


def _close_window(hwnd):
    import ctypes
    user32 = ctypes.windll.user32
    WM_CLOSE = 0x0010
    try:
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    except Exception:
        pass


WINDOW_KEY_HINTS = {
    "kalkulator": ["kalkulator", "calculator"],
    "google chrome": ["chrome"],
    "cmd (terminal)": ["cmd", "command prompt"],
    "file explorer": ["file explorer", "explorer"],
    "notepad": ["notepad"],
    "paint": ["paint"],
    "task manager": ["task manager"],
    "powershell": ["windows powershell", "powershell"],
    "vs code": ["visual studio code"],
    "pengaturan": ["settings", "pengaturan"],
}


def find_new_window(before_hwnds, keyword="", timeout=15.0):
    """Cari jendela baru yang muncul setelah launch. Return hwnd atau None.
    - keyword bisa str atau list keyword (cocok salah satu).
    - Jendela milik proses FIRDHAN & window bertitle 'firdhan' dilewati.
    - Setelah 60% timeout, keyword diabaikan (fase longgar): ambil jendela
      baru apa pun, supaya aplikasi UWP (Kalkulator/Calculator) yang
      judulnya beda-beda tetap ter-deteksi."""
    t0 = time.time()
    if isinstance(keyword, str):
        keywords = [keyword] if keyword else []
    else:
        keywords = list(keyword or [])
    keywords = [k.lower() for k in keywords if k]
    me = os.getpid()
    while time.time() - t0 < timeout:
        loose = (time.time() - t0) > timeout * 0.6   # fase longgar
        for hwnd, title, pid in _enum_windows():
            if hwnd in before_hwnds or pid == me:
                continue
            tl = title.lower()
            # hanya lewatkan jendela app utama kita sendiri, BUKAN semua
            # judul yang mengandung 'firdhan' (mis. jendela console
            # FIRDHAN_DEADLINE_XX yang sengaja dibuat untuk di-embed)
            if tl.startswith("firdhan agent"):
                continue
            if not keywords or loose or any(k in tl for k in keywords):
                return hwnd
        time.sleep(0.35)
    return None


def find_window_by_title(title, before_hwnds=None, timeout=20.0):
    """Cari window berdasarkan substring judul — deterministik, tidak
    mengandalkan keyword umum seperti 'cmd' yang bisa tertukar."""
    t0 = time.time()
    me = os.getpid()
    tl = title.lower()
    while time.time() - t0 < timeout:
        for hwnd, wtitle, pid in _enum_windows():
            if pid == me:
                continue
            if before_hwnds and hwnd in before_hwnds:
                continue
            if tl in wtitle.lower():
                return hwnd
        time.sleep(0.3)
    return None


class ScrollablePicker(tk.Frame):
    """Dropdown pengganti OptionMenu: ada entry filter + listbox + scrollbar,
    aman dipakai meski aplikasi terdeteksi ratusan (tidak overflow layar)."""

    def __init__(self, parent, options, var, command=None, font=("Consolas", 8)):
        super().__init__(parent, bg=Theme.PANEL)
        self.options = list(options)
        self.var = var
        self.command = command
        self._win = None
        self.btn = tk.Label(self, text="", bg=Theme.INPUT_BG, fg=Theme.CYAN,
                            font=font, anchor="w", padx=6, pady=2,
                            cursor="hand2", highlightthickness=1,
                            highlightbackground=Theme.BORDER)
        self.btn.pack(fill="x", expand=True)
        self.btn.bind("<Button-1>", self._open)
        self._sync_text()

    def _sync_text(self):
        try:
            self.btn.config(text=("\u25be " + self.var.get())[:44])
        except Exception:
            pass

    def set_options(self, options):
        self.options = list(options)
        if self._win is not None:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None

    def _close(self):
        if self._win is not None:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None

    def _open(self, _e=None):
        self._close()
        win = tk.Toplevel(self)
        self._win = win
        win.overrideredirect(True)
        win.configure(bg=Theme.BORDER)
        wpx = max(240, self.winfo_width())
        win.geometry("%dx260+%d+%d" % (wpx, self.winfo_rootx(),
                                       self.winfo_rooty() + self.winfo_height()))
        f = tk.Frame(win, bg=Theme.INPUT_BG)
        f.pack(fill="both", expand=True, padx=1, pady=1)
        ent = tk.Entry(f, bg=Theme.INPUT_BG, fg=Theme.TEXT,
                       insertbackground=Theme.ACCENT, relief="flat",
                       font=("Consolas", 8))
        ent.pack(fill="x", padx=4, pady=(4, 2))
        lb = tk.Listbox(f, bg=Theme.INPUT_BG, fg=Theme.TEXT,
                        selectbackground=Theme.ACCENT,
                        selectforeground=Theme.BG, relief="flat",
                        font=("Consolas", 8), activestyle="none")
        sb = tk.Scrollbar(f, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        lb.pack(fill="both", expand=True, padx=(4, 0), pady=(0, 4))

        def refresh(*_):
            q = ent.get().lower()
            lb.delete(0, "end")
            for o in self.options:
                if q in o.lower():
                    lb.insert("end", o)
        ent.bind("<KeyRelease>", refresh)
        refresh()

        def pick(_e=None):
            sel = lb.curselection()
            if sel:
                self.var.set(lb.get(sel[0]))
                self._sync_text()
                self._close()
                if self.command:
                    self.command(self.var.get())
        lb.bind("<Double-Button-1>", pick)
        lb.bind("<Return>", pick)
        lb.bind("<Escape>", lambda _e: self._close())
        ent.bind("<Escape>", lambda _e: self._close())

        def on_focus_out(_e=None):
            try:
                if win.focus_get() is None:
                    self._close()
            except Exception:
                pass
        win.bind("<FocusOut>", on_focus_out)
        ent.focus_set()


class TaskCell(tk.Frame):
    """Satu slot multi-tasking: pilih aplikasi → launch → window asli di-embed.
    Klik area jendela = langsung fokus, bisa ngetik & operasikan aplikasi."""

    CAM_OPTION = "📷 KAMERA DEPAN (webcam)"

    def __init__(self, parent, slot, app):
        super().__init__(parent, bg=Theme.PANEL,
                         highlightbackground=Theme.BORDER, highlightthickness=1)
        self.slot = slot
        self.app = app
        self.choice = tk.StringVar(value="— pilih aplikasi —")
        self.hwnd = None
        self.proc = None
        self.embedded = False
        self.cap = None
        self._photo = None
        self._blink = False
        self._cam_on = False
        self.W, self.H = 272, 158

        # ── header: dropdown aplikasi (scrollable + filter) ──
        top = tk.Frame(self, bg=Theme.PANEL)
        top.pack(fill="x", padx=4, pady=(4, 2))
        tk.Label(top, text=f"SLOT-{slot:02d}", bg=Theme.PANEL, fg=Theme.ACCENT_DIM,
                 font=("Consolas", 8, "bold")).pack(side="left")
        opts = ["— pilih aplikasi —", self.CAM_OPTION] + list(self.app.task_apps.keys())
        om = ScrollablePicker(top, opts, self.choice,
                              command=lambda _v: self._on_select())
        om.pack(side="left", fill="x", expand=True, padx=4)
        self.opt_menu = om

        # ── area jendela (FILL PENUH CELL — responsif) ──
        self.canvas = tk.Canvas(self, width=self.W, height=self.H,
                                bg="#000d00", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=4)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.create_text(self.W // 2, self.H // 2 - 12,
                                text="[ KOSONG ]", fill=Theme.MUTED,
                                font=("Consolas", 11, "bold"), tags="placeholder")
        self.canvas.create_text(self.W // 2, self.H // 2 + 10,
                                text="pilih aplikasi di atas / klik untuk akses",
                                fill=Theme.ACCENT_DIM, font=("Consolas", 8),
                                tags="placeholder")
        self._draw_overlay()

        # ── footer: status ──
        bot = tk.Frame(self, bg=Theme.PANEL)
        bot.pack(fill="x", padx=4, pady=(2, 4))
        self.status_lbl = tk.Label(bot, text="IDLE", bg=Theme.PANEL, fg=Theme.MUTED,
                                   font=("Consolas", 8, "bold"))
        self.status_lbl.pack(side="left")
        tk.Button(bot, text="▶ BUKA", command=self.launch,
                  bg=Theme.GREEN, fg=Theme.BG, relief="flat",
                  font=("Consolas", 8, "bold"), cursor="hand2").pack(side="right", padx=1)
        tk.Button(bot, text="✕ TUTUP", command=self.close,
                  bg=Theme.RED, fg=Theme.BG, relief="flat",
                  font=("Consolas", 8, "bold"), cursor="hand2").pack(side="right", padx=1)

        self._poll()

    def _draw_overlay(self):
        w, h = self.W, self.H
        L = 16
        for (x1, y1, x2, y2) in [
            (4, 4, 4 + L, 4), (4, 4, 4, 4 + L),
            (w - 4, 4, w - 4 - L, 4), (w - 4, 4, w - 4, 4 + L),
            (4, h - 4, 4 + L, h - 4), (4, h - 4, 4, h - 4 - L),
            (w - 4, h - 4, w - 4 - L, h - 4), (w - 4, h - 4, w - 4, h - 4 - L),
        ]:
            self.canvas.create_line(x1, y1, x2, y2, fill=Theme.CYAN, width=1)
        self.canvas.create_text(8, 8, text=f"WIN-{self.slot:02d}", fill=Theme.CYAN,
                                font=("Consolas", 7, "bold"), anchor="nw", tags="ov")
        self.rec_dot = self.canvas.create_oval(w - 34, 6, w - 26, 14, fill=Theme.RED,
                                               outline="", tags="ov")

    def _set_status(self, text, color):
        self.status_lbl.config(text=text, fg=color)

    def _on_canvas_configure(self, event=None):
        """Saat cell di-resize: overlay digambar ulang dan jendela yang
        sedang di-embed ikut menyusut (Notepad/Paint/Chrome ikut mengecil)."""
        try:
            w = max(80, self.canvas.winfo_width())
            h = max(60, self.canvas.winfo_height())
            if abs(w - self.W) < 2 and abs(h - self.H) < 2:
                return
            self.W, self.H = w, h
            self.canvas.delete("ov")
            self._draw_overlay()
            if self.hwnd:
                _resize_embedded(self.hwnd, w, h)
                self._set_status("EMBEDDED ✓ (responsif)", Theme.GREEN)
            elif self.cap is None:
                self.canvas.delete("placeholder")
                self.canvas.create_text(
                    w // 2, h // 2 - 12, text="[ KOSONG ]", fill=Theme.MUTED,
                    font=("Consolas", 11, "bold"), tags="placeholder")
                self.canvas.create_text(
                    w // 2, h // 2 + 10,
                    text="pilih aplikasi di atas / klik untuk akses",
                    fill=Theme.ACCENT_DIM, font=("Consolas", 8),
                    tags="placeholder")
        except Exception:
            pass

    def _on_select(self, *args):
        name = self.choice.get()
        if name == self.CAM_OPTION:
            self.launch()

    def set_apps(self, apps):
        """Rebuild daftar aplikasi di dropdown."""
        self.opt_menu.set_options(
            ["— pilih aplikasi —", self.CAM_OPTION] + list(apps.keys()))
        if self.choice.get() not in apps and self.choice.get() != self.CAM_OPTION:
            self.choice.set("— pilih aplikasi —")
            self.opt_menu._sync_text()

    # ── LAUNCH ──
    def launch(self):
        name = self.choice.get()
        if name.startswith("—"):
            self._set_status("PILIH APLIKASI DULU", Theme.ORANGE)
            return
        if name == self.CAM_OPTION:
            self._start_camera()
            return
        cmd = self.app.task_apps.get(name)
        if not cmd:
            return
        self._set_status("LAUNCHING...", Theme.ORANGE)
        threading.Thread(target=self._launch_worker, args=(name, cmd),
                         daemon=True).start()

    def _launch_worker(self, name, cmd):
        import ctypes
        user32 = ctypes.windll.user32
        try:
            before = {h for h, _t, _p in _enum_windows()}
            cmd = str(cmd)
            exe_base = os.path.basename(cmd).lower()
            is_console = exe_base.startswith(
                ("cmd", "powershell", "pwsh", "wsl", "bash", "ubuntu", "debian"))
            # Judul unik per slot. Filter 'firdhan' di find_new_window
            # sekarang hanya men-skip jendela app utama, jadi nama ini
            # aman dipakai sebagai identitas jendela console.
            title = f"FIRDHAN_DEADLINE_{self.slot:02d}"
            kw = [name.split("(")[0].strip()]

            if exe_base.startswith("chrome"):
                # Google Chrome: paksa jendela BARU tiap slot sehingga
                # 8 slot bisa menjalankan 8 Chrome sekaligus.
                self.proc = subprocess.Popen(
                    [cmd, "--new-window", "--no-first-run",
                     "--no-default-browser-check",
                     "--disable-session-crashed-bubble",
                     "--start-maximized",
                     "about:blank"])
                kw = ["chrome"]
            elif is_console:
                # Console app WAJIB dibuatkan konsol BARU.
                # Tanpa CREATE_NEW_CONSOLE, cmd attach ke konsol induk
                # (terminal VS Code) dan hilang -> "WINDOW DITUTUP".
                if exe_base.startswith("cmd"):
                    self.proc = subprocess.Popen(
                        ["cmd", "/k", f"title {title}"],
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    self.proc = subprocess.Popen(
                        cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif cmd.endswith(".lnk") or ":" in cmd[-2:]:
                os.startfile(cmd)
            else:
                self.proc = subprocess.Popen(cmd, shell=True)
            time.sleep(1.4)

            # ── DETECT ──
            if is_console:
                hwnd = find_window_by_title(title, before, timeout=20.0)
            else:
                hwnd = find_new_window(before, keyword=kw, timeout=15.0)
            if not hwnd:
                self.after(0, lambda: self._set_status(
                    "WINDOW TIDAK DITEMUKAN", Theme.RED))
                return
            self.hwnd = hwnd

            # ── EMBED DIPAKSA: 4x percobaan, 2 urutan berbeda ──
            # Urutan ganjil: SetParent dulu baru ubah style (beberapa
            # console window bandel kalau style diubah lebih dulu).
            cw = max(80, self.canvas.winfo_width())
            ch = max(60, self.canvas.winfo_height())
            self.W, self.H = cw, ch
            ok = False
            for attempt in range(4):
                if attempt % 2 == 1:
                    user32.SetParent(hwnd, self.canvas.winfo_id())
                _embed_window(hwnd, self.canvas.winfo_id(), cw, ch)
                _resize_embedded(hwnd, cw, ch)
                time.sleep(0.6)
                if not user32.IsWindow(hwnd):
                    break                      # window mati -> jangan lanjut
                ok = True
                break
            if ok:
                time.sleep(0.4)
                _resize_embedded(hwnd, self.canvas.winfo_width(),
                                 self.canvas.winfo_height())
            self.embedded = bool(ok)
            self.after(0, lambda: self._set_status(
                "EMBEDDED ✓ (klik utk operasikan)" if ok
                else "RUNNING (window terpisah)",
                Theme.GREEN if ok else Theme.YELLOW))
            self.after(0, lambda: self.canvas.delete("placeholder"))

            # verifikasi ulang 2 detik kemudian
            def _verify():
                if self.hwnd and not user32.IsWindow(self.hwnd):
                    self.hwnd = None
                    self.embedded = False
                    self._set_status("WINDOW DITUTUP", Theme.RED)
            self.after(2000, _verify)
        except Exception as e:
            self.after(0, lambda: self._set_status(f"ERROR: {e}", Theme.RED))

    # ── KLIK = AKSES ──
    def _on_click(self, event=None):
        name = self.choice.get()
        if name == self.CAM_OPTION or self.cap is not None:
            if not self.running_cam:
                self._start_camera()
            return
        if self.hwnd:
            _focus_window(self.hwnd)   # langsung bisa ngetik/operasikan
            self._set_status("FOCUSED ✓", Theme.ACCENT)
        else:
            self.launch()

    # ── KAMERA ──
    def _start_camera(self):
        if not HAS_CV2:
            self._set_status("INSTALL opencv-python", Theme.RED)
            return
        if self.cap is not None:
            return
        cap = cv2.VideoCapture(0)
        if cap is None or not cap.isOpened():
            self._set_status("KAMERA TIDAK TERDETEKSI", Theme.RED)
            return
        self.cap = cap
        self.running_cam = True
        self.canvas.delete("placeholder")
        self._set_status("KAMERA LIVE ✓", Theme.GREEN)

    def _cam_tick(self):
        if self.cap is not None and self.running_cam:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (self.W, self.H))
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = PILImage.fromarray(rgb)
                self._photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self._photo,
                                         anchor="nw", tags="feed")
                self.canvas.tag_lower("feed")
                self.canvas.tag_raise("ov")
                ts = datetime.now().strftime("%H:%M:%S")
                self.canvas.create_text(self.W - 44, 10, text=ts, fill=Theme.CYAN,
                                        font=("Consolas", 7), anchor="e", tags="ts")
        if self.cap is not None:
            self._blink = not self._blink
            try:
                self.canvas.itemconfig(self.rec_dot,
                                       fill=Theme.RED if self._blink else Theme.PANEL)
            except Exception:
                pass
            self.after(90, self._cam_tick)

    # ── CLOSE ──
    def close(self):
        if self.hwnd:
            _unembed_window(self.hwnd)
            _close_window(self.hwnd)
            self.hwnd = None
            self.embedded = False
        if self.proc:
            try:
                # paksa bunuh seluruh tree proses (cmd + anak-anaknya);
                # console window sering mengabaikan WM_CLOSE saja
                subprocess.run(
                    ["taskkill", "/pid", str(self.proc.pid),
                     "/f", "/t"], capture_output=True, timeout=8)
            except Exception:
                try:
                    self.proc.terminate()
                except Exception:
                    pass
            self.proc = None
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
            self.running_cam = False
        self.canvas.delete("feed")
        self.canvas.delete("ts")
        self.canvas.create_text(self.W // 2, self.H // 2, text="[ KOSONG ]",
                                fill=Theme.MUTED, font=("Consolas", 11, "bold"),
                                tags="placeholder")
        self._set_status("IDLE", Theme.MUTED)

    # ── poll status window ──
    def _poll(self):
        try:
            if self.hwnd:
                import ctypes
                if not ctypes.windll.user32.IsWindow(self.hwnd):
                    self.hwnd = None
                    self._set_status("WINDOW DITUTUP", Theme.RED)
                elif self.embedded and self.canvas.winfo_ismapped():
                    # FILL GUARD: jendela ter-embed dipaksa menutupi
                    # 100% area canvas setiap saat (anti black-bar).
                    # Hanya jalan jika cell sedang tampil (window kecil).
                    _resize_embedded(self.hwnd, self.canvas.winfo_width(),
                                     self.canvas.winfo_height())
            if self.cap is not None and self.running_cam and not self._cam_on:
                self._cam_on = True
                self._cam_tick()
        except Exception:
            pass
        self.after(600, self._poll)


class HackerButton(tk.Canvas):
    def __init__(self, parent, text, command, color=Theme.ACCENT, width=120, height=38, **kwargs):
        super().__init__(parent, width=width, height=height, bg=Theme.PANEL, highlightthickness=0, relief="flat", cursor="hand2", **kwargs)
        self.text = text
        self.command = command
        self.color = color
        self.width = width
        self.height = height
        self.hovered = False
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        glow = self.color if self.hovered else Theme.BORDER
        self.create_rectangle(2, 2, self.width - 2, self.height - 2, outline=glow, width=2 if self.hovered else 1)
        self.create_text(self.width // 2, self.height // 2, text=self.text, fill=self.color if self.hovered else Theme.TEXT, font=("Consolas", 9, "bold"))

    def _on_enter(self, e):
        self.hovered = True
        self._draw()

    def _on_leave(self, e):
        self.hovered = False
        self._draw()

    def _on_click(self, e):
        if self.command:
            self.command()


class TerminalLog(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.INPUT_BG, fg=Theme.TEXT, insertbackground=Theme.ACCENT, relief="flat", font=("Consolas", 10), wrap="word", padx=14, pady=14, highlightthickness=1, highlightbackground=Theme.BORDER, **kwargs)
        self.tag_config("success", foreground=Theme.GREEN)
        self.tag_config("error", foreground=Theme.RED)
        self.tag_config("info", foreground=Theme.ACCENT)
        self.tag_config("muted", foreground=Theme.MUTED)
        self.tag_config("prompt", foreground=Theme.PURPLE)
        self.tag_config("warn", foreground=Theme.ORANGE)
        self.config(state="disabled")

    def append(self, text, tag="info"):
        self.config(state="normal")
        self.insert("end", f"{text}\n", tag)
        self.see("end")
        self.config(state="disabled")


# ═══════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════
class FirdhanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FIRDHAN AGENT — AI + FULL WINDOWS ASSISTANT 2026")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.root.configure(bg=Theme.BG)

        self.chat_store = ChatStore()
        self.ai_client = OpenRouterClient()
        self.current_view = "assistant"  # assistant | system | config

        self._build_ui()
        self._show_assistant()  # AUTO OPEN ASSISTANT
        self._update_clock()
        self._start_pulse()
        self._start_glitch()    # hacker FX

    def _build_ui(self):
        # ═══ ROOT LAYOUT ═══
        self.main_container = tk.Frame(self.root, bg=Theme.BG)
        self.main_container.pack(fill="both", expand=True, padx=16, pady=12)

        # Bottom hex ticker bar
        tick = tk.Frame(self.root, bg=Theme.PANEL)
        tick.pack(fill="x", side="bottom")
        tk.Frame(tick, bg=Theme.ACCENT, height=1).pack(fill="x")
        self.ticker_label = tk.Label(tick, text="FIRDHAN AGENT // SYSTEM ONLINE",
                                     bg=Theme.PANEL, fg=Theme.ACCENT_DIM,
                                     font=("Consolas", 8))
        self.ticker_label.pack(anchor="w", padx=12, pady=2)

        # ═══ LEFT SIDEBAR ═══
        sidebar = tk.Frame(self.main_container, bg=Theme.PANEL, width=260)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)
        tk.Frame(sidebar, bg=Theme.ACCENT, height=2).pack(fill="x")

        # Header
        hdr = tk.Frame(sidebar, bg=Theme.PANEL)
        hdr.pack(fill="x", pady=(14, 10))
        tk.Label(hdr, text="◈", bg=Theme.PANEL, fg=Theme.ACCENT, font=("Consolas", 24, "bold")).pack(side="left", padx=12)
        tk.Label(hdr, text="FIRDHAN\nAGENT", bg=Theme.PANEL, fg=Theme.TEXT, font=("Consolas", 14, "bold"), justify="left").pack(side="left")

        # Menu
        tk.Label(sidebar, text="► MENU", bg=Theme.PANEL, fg=Theme.MUTED, font=("Consolas", 9, "bold")).pack(anchor="w", padx=12, pady=(8, 6))

        self.menu_assistant = self._menu_button(sidebar, "◉ ASSISTANT", Theme.ACCENT, self._show_assistant)
        self.menu_system = self._menu_button(sidebar, "◎ SYSTEM", Theme.TEXT, self._show_system)
        self.menu_config = self._menu_button(sidebar, "◎ AI CONFIG", Theme.PURPLE, self._show_config)
        self.menu_multitask = self._menu_button(sidebar, "◎ MULTI TASKING", Theme.CYAN, self._show_multitask)

        # Divider
        tk.Frame(sidebar, bg=Theme.BORDER, height=1).pack(fill="x", padx=12, pady=10)

        # Quick Apps
        tk.Label(sidebar, text="► APLIKASI CEPAT", bg=Theme.PANEL, fg=Theme.ACCENT, font=("Consolas", 10, "bold")).pack(anchor="w", padx=12, pady=(0, 8))
        apps_grid = tk.Frame(sidebar, bg=Theme.PANEL)
        apps_grid.pack(fill="x", padx=12)

        quick_apps = [
            ("📝 WORD", "word", Theme.GREEN), ("💻 VS CODE", "vscode", Theme.ACCENT),
            ("🌐 CHROME", "chrome", Theme.ORANGE), ("📊 EXCEL", "excel", Theme.GREEN),
            ("🎨 PAINT", "paint", Theme.PURPLE), ("📋 NOTEPAD", "notepad", Theme.TEXT),
            ("🧮 CALC", "calculator", Theme.YELLOW), ("📁 EXPLORER", "explorer", Theme.TEXT),
        ]
        for i, (label, key, color) in enumerate(quick_apps):
            btn = HackerButton(apps_grid, text=label, width=118, height=34, color=color,
                             command=lambda k=key: self._exec_system(f"buka {k}"))
            btn.grid(row=i // 2, column=i % 2, padx=2, pady=2)

        # System Quick
        tk.Label(sidebar, text="► SISTEM", bg=Theme.PANEL, fg=Theme.ACCENT, font=("Consolas", 10, "bold")).pack(anchor="w", padx=12, pady=(12, 8))
        sys_grid = tk.Frame(sidebar, bg=Theme.PANEL)
        sys_grid.pack(fill="x", padx=12)

        sys_btns = [
            ("📷 WEBCAM", "webcam", Theme.PURPLE), ("📸 SCREENSHOT", "screenshot", Theme.GREEN),
            ("🔇 MUTE", "mute", Theme.RED), ("🔊 VOL 50", "volume 50", Theme.ACCENT),
            ("☀ BRIGHT 70", "kecerahan 70", Theme.ORANGE), ("🔒 LOCK", "lock", Theme.YELLOW),
            ("🐧 WSL AUTO", "wsl", Theme.GREEN), ("⌨ CMD", "cmd", Theme.TEXT),
            ("🔑 APIKEYS", "__apikeys__", Theme.YELLOW), ("▣ APP GRID", "__cctv__", Theme.CYAN),
        ]
        for i, (label, cmd, color) in enumerate(sys_btns):
            btn = HackerButton(sys_grid, text=label, width=118, height=34, color=color,
                             command=lambda c=cmd: self._toolbar_action(c))
            btn.grid(row=i // 2, column=i % 2, padx=2, pady=2)

        # Power
        tk.Label(sidebar, text="► DAYA", bg=Theme.PANEL, fg=Theme.ACCENT, font=("Consolas", 10, "bold")).pack(anchor="w", padx=12, pady=(12, 8))
        power = tk.Frame(sidebar, bg=Theme.PANEL)
        power.pack(fill="x", padx=12)
        HackerButton(power, "⏻ SHUTDOWN", width=118, height=34, color=Theme.RED,
                    command=lambda: self._exec_system("matikan laptop")).pack(side="left", padx=2)
        HackerButton(power, "↻ RESTART", width=118, height=34, color=Theme.ORANGE,
                    command=lambda: self._exec_system("restart")).pack(side="left", padx=2)

        # Footer sidebar
        tk.Frame(sidebar, bg=Theme.BORDER, height=1).pack(fill="x", padx=12, pady=12)
        self.status_dot = tk.Label(sidebar, text="● ONLINE", bg=Theme.PANEL, fg=Theme.GREEN, font=("Consolas", 9, "bold"))
        self.status_dot.pack(anchor="w", padx=12)
        tk.Label(sidebar, text="AI: OpenRouter\nMode: Full Access", bg=Theme.PANEL, fg=Theme.MUTED, font=("Consolas", 8), justify="left").pack(anchor="w", padx=12, pady=(4, 0))

        # ═══ MAIN CONTENT AREA ═══
        self.content = tk.Frame(self.main_container, bg=Theme.BG)
        self.content.pack(side="left", fill="both", expand=True)

        # We will create three frames and raise them
        self.frame_assistant = tk.Frame(self.content, bg=Theme.BG)
        self.frame_system = tk.Frame(self.content, bg=Theme.BG)
        self.frame_config = tk.Frame(self.content, bg=Theme.BG)
        self.frame_multitask = tk.Frame(self.content, bg=Theme.BG)

        for f in (self.frame_assistant, self.frame_system, self.frame_config, self.frame_multitask):
            f.place(relwidth=1, relheight=1)

        self._build_assistant_view()
        self._build_system_view()
        self._build_config_view()
        self._build_multitask_view()

    # ═══════════════════════════════════════════════════════
    # TOOLBAR ACTIONS (WSL AUTO / APIKEYS / CCTV)
    # ═══════════════════════════════════════════════════════
    def _toolbar_action(self, key):
        if key == "__apikeys__":
            self._show_system()
            search_apikeys(log=self.sys_log.append, scan_home=True)
        elif key == "__cctv__":
            self._show_multitask()
            self._task_launch_all()
        elif key == "wsl":
            self._show_system()
            self._exec_system("wsl")
        else:
            self._exec_system(key)

    # ═══════════════════════════════════════════════════════
    # MULTI TASKING VIEW (CCTV GRID)
    # ═══════════════════════════════════════════════════════
    def _build_multitask_view(self):
        # deteksi aplikasi terinstall di perangkat
        self.task_apps = detect_installed_apps()
        try:
            self.task_apps_label = f"{len(self.task_apps)} aplikasi terdeteksi"
        except Exception:
            self.task_apps_label = ""

        hdr = tk.Frame(self.frame_multitask, bg=Theme.BG)
        hdr.pack(fill="x", pady=(0, 10))
        tk.Frame(hdr, bg=Theme.CYAN, height=2).pack(fill="x")
        tk.Label(hdr, text="◈ FIRDHAN // MULTI TASKING // APP GRID",
                 bg=Theme.BG, fg=Theme.CYAN,
                 font=("Consolas", 18, "bold")).pack(anchor="w", pady=8)
        tk.Label(hdr, text="Pilih aplikasi per slot → window asli di-embed → klik utk ngetik & operasikan",
                 bg=Theme.BG, fg=Theme.MUTED,
                 font=("Consolas", 9)).pack(anchor="w")

        bar = tk.Frame(self.frame_multitask, bg=Theme.BG)
        bar.pack(fill="x", pady=(0, 8))
        HackerButton(bar, "🚀 BUKA SEMUA", width=140, height=34,
                     color=Theme.GREEN,
                     command=self._task_launch_all).pack(side="left", padx=3)
        HackerButton(bar, "■ TUTUP SEMUA", width=140, height=34,
                     color=Theme.RED,
                     command=self._task_close_all).pack(side="left", padx=3)
        HackerButton(bar, "⟳ REFRESH APPS", width=140, height=34,
                     color=Theme.ORANGE,
                     command=self._task_refresh_apps).pack(side="left", padx=3)
        HackerButton(bar, "🐧 WSL", width=110, height=34,
                     color=Theme.GREEN,
                     command=lambda: self._exec_system("wsl")).pack(side="left", padx=3)
        tk.Label(bar, text="[ APP GRID v3.0 // EMBED ENGINE ]",
                 bg=Theme.BG, fg=Theme.ACCENT_DIM,
                 font=("Consolas", 9)).pack(side="right", padx=6)

        # ── baris pilihan jumlah jendela: 1 = fullscreen besar, maks 8 ──
        lay = tk.Frame(self.frame_multitask, bg=Theme.BG)
        lay.pack(fill="x", pady=(0, 8))
        tk.Label(lay, text="JENDELA \u25b8", bg=Theme.BG, fg=Theme.CYAN,
                 font=("Consolas", 10, "bold")).pack(side="left", padx=(3, 6))
        self.layout_buttons = {}
        for n in (1, 2, 3, 4, 6, 8):
            b = HackerButton(lay, text=str(n), width=46, height=30,
                             color=Theme.CYAN,
                             command=lambda n=n: self._task_set_layout(n))
            b.pack(side="left", padx=2)
            self.layout_buttons[n] = b
        self.task_layout = 8
        tk.Label(lay, text="1 = fullscreen besar \u00b7 semakin sedikit jendela = semakin lebar & tinggi",
                 bg=Theme.BG, fg=Theme.MUTED,
                 font=("Consolas", 9)).pack(side="left", padx=10)

        grid = tk.Frame(self.frame_multitask, bg=Theme.BG)
        grid.pack(fill="both", expand=True)
        self.task_grid = grid
        self.task_cells = []
        for i in range(8):
            cell = TaskCell(grid, i + 1, self)
            r, c = divmod(i, 4)
            cell.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            grid.rowconfigure(r, weight=1)
            grid.columnconfigure(c, weight=1)
            self.task_cells.append(cell)

        # default assignment: isi slot dengan aplikasi populer agar siap dipakai
        defaults = ["CMD (Terminal)", "File Explorer", "Notepad", "Google Chrome",
                    self.task_cells[4].CAM_OPTION, "Kalkulator", "Paint",
                    "Task Manager"]
        for cell, dname in zip(self.task_cells, defaults):
            if dname in self.task_apps or dname == cell.CAM_OPTION:
                cell.choice.set(dname)

        # terapkan layout awal: 8 jendela (tombol "8" menyala)
        self._task_set_layout(8)

    def _task_launch_all(self):
        for cell in getattr(self, "task_cells", []):
            try:
                cell.launch()
                time.sleep(0.6)   # jeda agar window terdeteksi benar
            except Exception:
                pass

    def _task_close_all(self):
        for cell in getattr(self, "task_cells", []):
            try:
                cell.close()
            except Exception:
                pass

    def _task_refresh_apps(self):
        self.task_apps = detect_installed_apps()
        for cell in getattr(self, "task_cells", []):
            try:
                cell.set_apps(self.task_apps)
            except Exception:
                pass
        self.sys_log and None

    # ── LAYOUT GRID: pilih berapa jendela yang tampil (1..8) ──
    TASK_LAYOUTS = {1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2),
                    5: (3, 2), 6: (3, 2), 7: (4, 2), 8: (4, 2)}

    def _task_set_layout(self, n):
        """Tampilkan n slot saja — slot yang tampil otomatis jadi jauh
        lebih besar (1 slot = praktis fullscreen). Slot yang disembunyikan:
        jendela aslinya dilepas kembali ke desktop (aplikasi TETAP HIDUP),
        dan akan di-embed lagi otomatis kalau slot ditampilkan lagi."""
        n = max(1, min(8, int(n)))
        self.task_layout = n
        cols, rows = self.TASK_LAYOUTS[n]
        grid = self.task_grid
        for r in range(4):
            grid.rowconfigure(r, weight=0)
        for c in range(4):
            grid.columnconfigure(c, weight=0)
        for r in range(rows):
            grid.rowconfigure(r, weight=1)
        for c in range(cols):
            grid.columnconfigure(c, weight=1)
        for i, cell in enumerate(self.task_cells):
            if i < n:
                r, c = divmod(i, cols)
                cell.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            else:
                if cell.hwnd and getattr(cell, "embedded", False):
                    _unembed_window(cell.hwnd)   # balik ke desktop, app tetap jalan
                    cell.embedded = False
                    cell._set_status("RUNNING (di desktop)", Theme.YELLOW)
                cell.grid_forget()
        self.frame_multitask.update_idletasks()
        # re-embed jendela yang tadi disembunyikan lalu ditampilkan lagi
        for cell in self.task_cells[:n]:
            if cell.hwnd and not cell.embedded:
                cw = max(80, cell.canvas.winfo_width())
                ch = max(60, cell.canvas.winfo_height())
                if _embed_window(cell.hwnd, cell.canvas.winfo_id(), cw, ch):
                    cell.embedded = True
                    _resize_embedded(cell.hwnd, cw, ch)
                    cell._set_status("EMBEDDED \u2713 (klik utk operasikan)", Theme.GREEN)
        # tandai tombol layout yang aktif
        for k, b in getattr(self, "layout_buttons", {}).items():
            b.color = Theme.GREEN if k == n else Theme.CYAN
            b._draw()

    def _show_multitask(self):
        self.current_view = "multitask"
        self.frame_multitask.lift()
        self._update_menu_colors()

    def _append_chat_msg_if_system(self, text, tag="info"):
        self._append_chat_msg("system", text)

    # ═══════════════════════════════════════════════════════
    # HACKER FX — glitch header + hex ticker
    # ═══════════════════════════════════════════════════════
    def _start_glitch(self):
        CH = "01<>/\\{}[]#@$%&*+=~ABCDEFX"

        def scramble():
            try:
                base = "◈ FIRDHAN // AI ASSISTANT // v2.0"
                txt = "".join(ch if random.random() > 0.10 else random.choice(CH)
                              for ch in base)
                if hasattr(self, "hdr_title"):
                    self.hdr_title.config(text=txt)
                ticker = " ".join("%02X" % random.getrandbits(8) for _ in range(30))
                if hasattr(self, "ticker_label"):
                    self.ticker_label.config(
                        text=f"RX> {ticker}  //  NODE: MAJA-PC  //  UPLINK: SECURE")
            except Exception:
                pass
            self.root.after(130, scramble)
        scramble()

    def _menu_button(self, parent, text, color, cmd):
        btn = tk.Label(parent, text=text, bg=Theme.PANEL, fg=color, font=("Consolas", 11, "bold"), cursor="hand2", anchor="w", padx=12, pady=8)
        btn.pack(fill="x")
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>", lambda e: btn.config(bg=Theme.PANEL2))
        btn.bind("<Leave>", lambda e: btn.config(bg=Theme.PANEL))
        return btn

    # ═══════════════════════════════════════════════════════
    # ASSISTANT VIEW (AI CHAT) — AUTO OPEN
    # ═══════════════════════════════════════════════════════
    def _build_assistant_view(self):
        # Header
        hdr = tk.Frame(self.frame_assistant, bg=Theme.BG)
        hdr.pack(fill="x", pady=(0, 10))
        tk.Frame(hdr, bg=Theme.ACCENT, height=2).pack(fill="x")
        self.hdr_title = tk.Label(hdr, text="◈ FIRDHAN // AI ASSISTANT // v2.0", bg=Theme.BG, fg=Theme.ACCENT, font=("Consolas", 18, "bold"))
        self.hdr_title.pack(anchor="w", pady=8)
        tk.Label(hdr, text="Powered by OpenRouter  |  Natural Language  |  Persona Enabled", bg=Theme.BG, fg=Theme.MUTED, font=("Consolas", 9)).pack(anchor="w")

        # Chat Area
        chat_frame = tk.Frame(self.frame_assistant, bg=Theme.BORDER)
        chat_frame.pack(fill="both", expand=True)
        tk.Frame(chat_frame, bg=Theme.ACCENT, height=2).pack(fill="x")

        self.chat_log = tk.Text(chat_frame, bg=Theme.INPUT_BG, fg=Theme.TEXT, insertbackground=Theme.ACCENT, relief="flat", font=("Consolas", 11), wrap="word", padx=16, pady=16, highlightthickness=0)
        self.chat_log.pack(fill="both", expand=True, padx=1, pady=1)
        self.chat_log.tag_config("user", foreground=Theme.USER_COLOR, font=("Consolas", 11, "bold"))
        self.chat_log.tag_config("ai", foreground=Theme.AI_COLOR, font=("Consolas", 11))
        self.chat_log.tag_config("sys", foreground=Theme.MUTED, font=("Consolas", 10))
        self.chat_log.tag_config("time", foreground=Theme.ACCENT_DIM, font=("Consolas", 8))
        self.chat_log.config(state="disabled")

        # Load previous chat
        self._load_chat_history()

        # Input Area
        input_frame = tk.Frame(self.frame_assistant, bg=Theme.BG)
        input_frame.pack(fill="x", pady=(12, 0))

        self.chat_input = tk.Entry(input_frame, bg=Theme.INPUT_BG, fg=Theme.TEXT, insertbackground=Theme.ACCENT, relief="flat", font=("Consolas", 12), highlightthickness=1, highlightcolor=Theme.ACCENT, highlightbackground=Theme.BORDER)
        self.chat_input.pack(side="left", fill="x", expand=True, ipady=12)
        self.chat_input.bind("<Return>", lambda e: self._send_chat())
        self.chat_input.focus_set()

        tk.Button(input_frame, text="▶ SEND", command=self._send_chat, bg=Theme.ACCENT, fg=Theme.BG, activebackground=Theme.ACCENT_DIM, activeforeground=Theme.TEXT, relief="flat", font=("Consolas", 10, "bold"), cursor="hand2", padx=20).pack(side="right", padx=(10, 0))
        tk.Button(input_frame, text="🗑 CLEAR", command=self._clear_chat, bg=Theme.RED, fg=Theme.BG, activebackground="#cc2244", relief="flat", font=("Consolas", 9, "bold"), cursor="hand2", padx=12).pack(side="right", padx=(6, 0))

        # Hint
        self.chat_hint = tk.Label(self.frame_assistant, text="Tanyakan apa saja, atau minta saya membuka aplikasi...", bg=Theme.BG, fg=Theme.ACCENT_DIM, font=("Consolas", 9), anchor="w")
        self.chat_hint.pack(fill="x", pady=(6, 0))

    def _load_chat_history(self):
        self.chat_log.config(state="normal")
        self.chat_log.delete("1.0", tk.END)
        if not self.chat_store.messages:
            self.chat_log.insert("end", "🤖 FIRDHAN AI ready.\n", "sys")
            self.chat_log.insert("end", "Saya bisa membantu menjawab pertanyaan, menjalankan perintah Windows, atau sekadar ngobrol.\n\n", "sys")
        else:
            for msg in self.chat_store.messages:
                self._append_chat_msg(msg["role"], msg["content"], save=False)
        self.chat_log.config(state="disabled")

    def _append_chat_msg(self, role, content, save=True):
        self.chat_log.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M")
        if role == "user":
            self.chat_log.insert("end", f"\n[{timestamp}] YOU > ", "time")
            self.chat_log.insert("end", f"{content}\n", "user")
        elif role == "assistant":
            self.chat_log.insert("end", f"[{timestamp}] AI > ", "time")
            self.chat_log.insert("end", f"{content}\n", "ai")
        else:
            self.chat_log.insert("end", f"{content}\n", "sys")
        self.chat_log.see("end")
        self.chat_log.config(state="disabled")
        if save:
            self.chat_store.add(role, content)

    def _send_chat(self):
        text = self.chat_input.get().strip()
        if not text:
            return

        # Check if it's a system command first
        sys_keywords = ["buka ", "jalankan ", "matikan", "restart", "sleep", "webcam", "screenshot", "volume", "kecerahan", "wifi", "battery", "tasklist", "kill ", "eject", "clipboard", "lock", "logoff", "hibernate", "shutdown"]
        is_system = any(text.lower().startswith(k) or k in text.lower() for k in sys_keywords)

        if is_system:
            # Execute system command and also inform AI
            self._append_chat_msg("user", text)
            self.chat_input.delete(0, tk.END)

            def run_sys():
                success, msg = CommandEngine.execute(text, log=None)
                # Log result to chat
                status = "✓" if success else "✗"
                self.root.after(0, lambda: self._append_chat_msg("system", f"[SYSTEM] {status} {msg}"))
                # Also notify AI about the action
                self._ask_ai(f"(User executed: {text}. Result: {msg})\nBeri respons singkat dalam bahasa yang sama dengan user.")

            threading.Thread(target=run_sys, daemon=True).start()
            return

        # Normal chat
        self._append_chat_msg("user", text)
        self.chat_input.delete(0, tk.END)
        self.chat_hint.config(text="AI sedang berpikir...", fg=Theme.ORANGE)

        def run_ai():
            messages = self.chat_store.build_prompt(text)
            success, response = self.ai_client.chat(messages)
            self.root.after(0, lambda: self._handle_ai_response(success, response))

        threading.Thread(target=run_ai, daemon=True).start()

    def _handle_ai_response(self, success, response):
        self.chat_hint.config(text="Tanyakan apa saja, atau minta saya membuka aplikasi...", fg=Theme.ACCENT_DIM)
        if success:
            self._append_chat_msg("assistant", response)
            # Try to execute any action detected in AI response
            executed, msg = execute_ai_action(response, log=self._append_chat_msg_if_system)
            if executed:
                self._append_chat_msg("system", f"[ACTION] {msg}")
        else:
            self._append_chat_msg("system", f"[AI ERROR] {response}")
    def _clear_chat(self):
        self.chat_store.clear()
        self.chat_log.config(state="normal")
        self.chat_log.delete("1.0", tk.END)
        self.chat_log.insert("end", "🤖 Chat history dibersihkan.\n\n", "sys")
        self.chat_log.config(state="disabled")

    # ═══════════════════════════════════════════════════════
    # SYSTEM VIEW (TERMINAL)
    # ═══════════════════════════════════════════════════════
    def _build_system_view(self):
        hdr = tk.Frame(self.frame_system, bg=Theme.BG)
        hdr.pack(fill="x", pady=(0, 10))
        tk.Frame(hdr, bg=Theme.GREEN, height=2).pack(fill="x")
        tk.Label(hdr, text="◈ FIRDHAN // SYSTEM TERMINAL", bg=Theme.BG, fg=Theme.GREEN, font=("Consolas", 18, "bold")).pack(anchor="w", pady=8)

        term_frame = tk.Frame(self.frame_system, bg=Theme.BORDER)
        term_frame.pack(fill="both", expand=True)
        tk.Frame(term_frame, bg=Theme.GREEN, height=2).pack(fill="x")

        self.sys_log = TerminalLog(term_frame)
        self.sys_log.pack(fill="both", expand=True, padx=1, pady=1)

        input_frame = tk.Frame(self.frame_system, bg=Theme.BG)
        input_frame.pack(fill="x", pady=(12, 0))

        self.sys_input = tk.Entry(input_frame, bg=Theme.INPUT_BG, fg=Theme.TEXT, insertbackground=Theme.GREEN, relief="flat", font=("Consolas", 12), highlightthickness=1, highlightcolor=Theme.GREEN, highlightbackground=Theme.BORDER)
        self.sys_input.pack(side="left", fill="x", expand=True, ipady=12)
        self.sys_input.bind("<Return>", lambda e: self._exec_system_entry())

        tk.Button(input_frame, text="▶ EXECUTE", command=self._exec_system_entry, bg=Theme.GREEN, fg=Theme.BG, activebackground="#2acc6e", relief="flat", font=("Consolas", 10, "bold"), cursor="hand2", padx=20).pack(side="right", padx=(10, 0))

    def _exec_system_entry(self):
        text = self.sys_input.get().strip()
        if text:
            self._exec_system(text)
            self.sys_input.delete(0, tk.END)

    def _exec_system(self, text):
        self.sys_log.append(f"> {text}", "prompt")

        def worker():
            success, msg = CommandEngine.execute(text, log=self.sys_log.append)
            if not success:
                self.sys_log.append(msg, "error")

        threading.Thread(target=worker, daemon=True).start()

    # ═══════════════════════════════════════════════════════
    # CONFIG VIEW (AI SETTINGS + PERSONA)
    # ═══════════════════════════════════════════════════════
    def _build_config_view(self):
        hdr = tk.Frame(self.frame_config, bg=Theme.BG)
        hdr.pack(fill="x", pady=(0, 10))
        tk.Frame(hdr, bg=Theme.PURPLE, height=2).pack(fill="x")
        tk.Label(hdr, text="◈ FIRDHAN // AI CONFIGURATION", bg=Theme.BG, fg=Theme.PURPLE, font=("Consolas", 18, "bold")).pack(anchor="w", pady=8)

        form = tk.Frame(self.frame_config, bg=Theme.PANEL)
        form.pack(fill="both", expand=True, padx=2, pady=2)
        tk.Frame(form, bg=Theme.PURPLE, height=2).pack(fill="x")

        # API Key
        tk.Label(form, text="OPENROUTER API KEY", bg=Theme.PANEL, fg=Theme.MUTED, font=("Consolas", 10, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        self.api_key_entry = tk.Entry(form, bg=Theme.INPUT_BG, fg=Theme.TEXT, insertbackground=Theme.ACCENT, relief="flat", font=("Consolas", 10), highlightthickness=1, highlightcolor=Theme.ACCENT, highlightbackground=Theme.BORDER)
        self.api_key_entry.pack(fill="x", padx=16, ipady=8)
        self.api_key_entry.insert(0, CONFIG.get("OPENROUTER_API_KEY", ""))

        # Model
        tk.Label(form, text="MODEL", bg=Theme.PANEL, fg=Theme.MUTED, font=("Consolas", 10, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        model_frame = tk.Frame(form, bg=Theme.PANEL)
        model_frame.pack(fill="x", padx=16)

        self.model_var = tk.StringVar(value=CONFIG.get("OPENROUTER_MODEL", "google/gemma-4-31b-it:free"))
        models = load_free_models() + FALLBACK_FREE_MODELS
        models = list(dict.fromkeys(models))  # unik
        model_menu = tk.OptionMenu(model_frame, self.model_var, *models)
        model_menu.config(bg=Theme.INPUT_BG, fg=Theme.TEXT, activebackground=Theme.PANEL2, activeforeground=Theme.ACCENT, highlightthickness=0, font=("Consolas", 10))
        model_menu["menu"].config(bg=Theme.INPUT_BG, fg=Theme.TEXT, activebackground=Theme.ACCENT, activeforeground=Theme.BG, font=("Consolas", 10))
        model_menu.pack(side="left", fill="x", expand=True, ipady=4)

        # System Prompt
        tk.Label(form, text="SYSTEM PROMPT (CORE)", bg=Theme.PANEL, fg=Theme.MUTED, font=("Consolas", 10, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        self.sys_prompt_box = tk.Text(form, bg=Theme.INPUT_BG, fg=Theme.TEXT, insertbackground=Theme.ACCENT, relief="flat", font=("Consolas", 10), height=4, highlightthickness=1, highlightcolor=Theme.ACCENT, highlightbackground=Theme.BORDER, padx=10, pady=10)
        self.sys_prompt_box.pack(fill="x", padx=16)
        self.sys_prompt_box.insert("1.0", CONFIG.get("SYSTEM_PROMPT", DEFAULT_CONFIG["SYSTEM_PROMPT"]))

        # PERSONA (KOSONG DEFAULT)
        tk.Label(form, text="PERSONA (KOSONGKAN JIKA TIDAK PERLU)", bg=Theme.PANEL, fg=Theme.ACCENT, font=("Consolas", 10, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        tk.Label(form, text="Tambahkan karakter, gaya bicara, atau instruksi khusus di sini.", bg=Theme.PANEL, fg=Theme.MUTED, font=("Consolas", 9)).pack(anchor="w", padx=16)

        self.persona_box = tk.Text(form, bg=Theme.INPUT_BG, fg=Theme.TEXT, insertbackground=Theme.ACCENT, relief="flat", font=("Consolas", 10), height=6, highlightthickness=1, highlightcolor=Theme.ACCENT, highlightbackground=Theme.BORDER, padx=10, pady=10)
        self.persona_box.pack(fill="x", padx=16, pady=(4, 0))
        self.persona_box.insert("1.0", CONFIG.get("PERSONA", ""))

        # Buttons
        btn_frame = tk.Frame(form, bg=Theme.PANEL)
        btn_frame.pack(fill="x", padx=16, pady=20)

        tk.Button(btn_frame, text="💾 SAVE CONFIG", command=self._save_ai_config, bg=Theme.GREEN, fg=Theme.BG, activebackground="#2acc6e", relief="flat", font=("Consolas", 10, "bold"), cursor="hand2", padx=20).pack(side="left", padx=(0, 8))
        tk.Button(btn_frame, text="🗑 CLEAR PERSONA", command=self._clear_persona, bg=Theme.RED, fg=Theme.BG, activebackground="#cc2244", relief="flat", font=("Consolas", 10, "bold"), cursor="hand2", padx=20).pack(side="left")

        # Info
        tk.Label(form, text="Persona akan digabungkan dengan System Prompt saat chat.\nKosongkan Persona untuk menggunakan default assistant.", bg=Theme.PANEL, fg=Theme.MUTED, font=("Consolas", 9), justify="left").pack(anchor="w", padx=16, pady=(0, 16))

    def _save_ai_config(self):
        CONFIG["OPENROUTER_API_KEY"] = self.api_key_entry.get().strip()
        CONFIG["OPENROUTER_MODEL"] = self.model_var.get()
        CONFIG["SYSTEM_PROMPT"] = self.sys_prompt_box.get("1.0", "end").strip()
        CONFIG["PERSONA"] = self.persona_box.get("1.0", "end").strip()
        save_config()
        # Update client
        self.ai_client = OpenRouterClient()
        messagebox.showinfo("Config Saved", "Konfigurasi AI disimpan.")

    def _clear_persona(self):
        self.persona_box.delete("1.0", tk.END)

    # ═══════════════════════════════════════════════════════
    # VIEW SWITCHER
    # ═══════════════════════════════════════════════════════
    def _show_assistant(self):
        self.current_view = "assistant"
        self.frame_assistant.lift()
        self._update_menu_colors()

    def _show_system(self):
        self.current_view = "system"
        self.frame_system.lift()
        self._update_menu_colors()

    def _show_config(self):
        self.current_view = "config"
        self.frame_config.lift()
        self._update_menu_colors()

    def _update_menu_colors(self):
        colors = {
            "assistant": (Theme.ACCENT, "◉ ASSISTANT"),
            "system": (Theme.GREEN, "◉ SYSTEM"),
            "config": (Theme.PURPLE, "◉ AI CONFIG"),
            "multitask": (Theme.CYAN, "◉ MULTI TASKING")
        }
        defaults = {
            "assistant": (Theme.TEXT, "◎ ASSISTANT"),
            "system": (Theme.TEXT, "◎ SYSTEM"),
            "config": (Theme.TEXT, "◎ AI CONFIG"),
            "multitask": (Theme.TEXT, "◎ MULTI TASKING")
        }
        menus = [self.menu_assistant, self.menu_system, self.menu_config, self.menu_multitask]
        views = ["assistant", "system", "config", "multitask"]
        for menu, view in zip(menus, views):
            if view == self.current_view:
                menu.config(fg=colors[view][0], text=colors[view][1])
            else:
                menu.config(fg=defaults[view][0], text=defaults[view][1])

    def _update_clock(self):
        if hasattr(self, 'status_dot'):
            now = datetime.now().strftime("%H:%M:%S")
            # We don't have time label in sidebar, skip
            pass
        self.root.after(1000, self._update_clock)

    def _start_pulse(self):
        def blink():
            if hasattr(self, 'status_dot'):
                c = self.status_dot.cget("fg")
                self.status_dot.config(fg=Theme.GREEN if c == Theme.ACCENT_DIM else Theme.ACCENT_DIM)
            self.root.after(1000, blink)
        blink()


def main():
    root = tk.Tk()
    FirdhanApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
