"""
=============================================================================
ADHYAKSH AI // Configuration & System Environment Settings
Autonomous Multi-Lingual AI Executive & System Operating Engine
=============================================================================
"""

import os
import platform

# Base Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Data Persistence File Paths
MEMORY_FILE = os.path.join(DATA_DIR, "memory_bank.json")
LEARNED_INTENTS_FILE = os.path.join(DATA_DIR, "learned_intents.json")
EXECUTION_LOGS_FILE = os.path.join(DATA_DIR, "execution_logs.json")
LEGACY_MEMORY_FILE = os.path.join(BASE_DIR, "memory_bank.json")

# Branding & Identity (Strictly Full Professional English)
APP_NAME = "ADHYAKSH AI"
APP_SUBTITLE = "Autonomous Multi-Lingual AI Executive & System Operating Engine"
APP_VERSION = "3.2.0 Executive Enterprise"
APP_CREATOR = "Neelkanth (Lead Engineer)"
APP_ICON = "⚡"

# Multi-Language Voice & NLP Configuration
SUPPORTED_LANGUAGES = {
    "auto": "🌐 Auto-Detect Multilingual",
    "en-IN": "🇬🇧 English (India / Global)",
    "hi-IN": "🇮🇳 Hindi (हिन्दी)",
    "gu-IN": "🇮🇳 Gujarati (ગુજરાતી)",
    "en-US": "🇺🇸 English (US Standard)",
}

DEFAULT_LANGUAGE = "auto"

# Speech Recognition Engine Tunables (Calibrated for High Sensitivity & Noise Cancellation)
STT_ENERGY_THRESHOLD = 180
STT_DYNAMIC_ENERGY = True
STT_PAUSE_THRESHOLD = 0.8
STT_PHRASE_TIME_LIMIT = 15

# System Drives Auto-Discovery & Dynamic Hardware Scanning
def get_available_drives():
    """Dynamically enumerates all mounted physical, external, and logical drives on the laptop."""
    drives = []
    if platform.system() == "Windows":
        try:
            import psutil
            for p in psutil.disk_partitions(all=False):
                mp = p.mountpoint
                if not mp.endswith("\\"):
                    mp += "\\"
                if mp.upper() not in [d.upper() for d in drives]:
                    drives.append(mp.upper())
        except Exception:
            pass

        # Fallback / augment with Windows letter scan A-Z
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive_path = f"{letter}:\\"
            if drive_path not in drives and os.path.exists(drive_path):
                drives.append(drive_path)

    if not drives:
        drives.append(BASE_DIR)
    return sorted(drives)

AVAILABLE_DRIVES = get_available_drives()
DEFAULT_WORK_DRIVE = "D:\\" if "D:\\" in AVAILABLE_DRIVES else ("C:\\" if "C:\\" in AVAILABLE_DRIVES else BASE_DIR)

# Common Application Registry for Universal App Control
COMMON_APPS = {
    "chrome": {"exe": "chrome", "label": "Google Chrome", "type": "Browser"},
    "browser": {"exe": "chrome", "label": "Default Browser", "type": "Browser"},
    "code": {"exe": "code", "label": "Visual Studio Code", "type": "IDE"},
    "vscode": {"exe": "code", "label": "Visual Studio Code", "type": "IDE"},
    "vs code": {"exe": "code", "label": "Visual Studio Code", "type": "IDE"},
    "spotify": {"exe": "spotify", "label": "Spotify Music", "type": "Media"},
    "notepad": {"exe": "notepad", "label": "Notepad", "type": "Editor"},
    "calculator": {"exe": "calc", "label": "Calculator", "type": "Utility"},
    "calc": {"exe": "calc", "label": "Calculator", "type": "Utility"},
    "task manager": {"exe": "taskmgr", "label": "Task Manager", "type": "System"},
    "taskmgr": {"exe": "taskmgr", "label": "Task Manager", "type": "System"},
    "explorer": {"exe": "explorer", "label": "File Explorer", "type": "System"},
    "cmd": {"exe": "cmd", "label": "Command Prompt", "type": "Terminal"},
    "terminal": {"exe": "wt", "fallback": "cmd", "label": "Windows Terminal", "type": "Terminal"},
    "powershell": {"exe": "powershell", "label": "PowerShell", "type": "Terminal"},
    "word": {"exe": "winword", "label": "Microsoft Word", "type": "Office"},
    "excel": {"exe": "excel", "label": "Microsoft Excel", "type": "Office"},
    "powerpoint": {"exe": "powerpnt", "label": "PowerPoint", "type": "Office"},
    "settings": {"uri": "ms-settings:", "label": "Windows Settings", "type": "System"},
}
