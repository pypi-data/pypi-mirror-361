# File: ui_finder/adb_handler.py

import os
import subprocess
import zipfile
import platform
import urllib.request
import shutil

ADB_URL = "https://github.com/kdiitg/ui_finder_adb/releases/download/v1.0.0/platform-tools-latest-windows.zip"
TOOLS_DIR = os.path.join(os.path.expanduser("~"), ".ui_finder", "platform-tools")
ADB_EXEC = os.path.join(TOOLS_DIR, "adb.exe") if platform.system() == "Windows" else os.path.join(TOOLS_DIR, "adb")

def download_and_extract_platform_tools():
    print("🌐 Downloading platform-tools...")
    zip_path = os.path.join(os.path.expanduser("~"), "platform-tools.zip")

    try:
        urllib.request.urlretrieve(ADB_URL, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(TOOLS_DIR))
        os.remove(zip_path)
        print("platform-tools downloaded and extracted.")
    except Exception as e:
        print("Failed to download platform-tools:", e)
        input("Press Enter to exit...")
        exit(1)

def ensure_adb():
    # Check system PATH first
    try:
        subprocess.check_output(["adb", "version"], stderr=subprocess.STDOUT)
        print("ADB found in system PATH.")
        return "adb"
    except Exception:
        pass

    # Fallback: Download and setup local ADB
    if not os.path.exists(ADB_EXEC):
        download_and_extract_platform_tools()

    # Check again
    if os.path.exists(ADB_EXEC):
        return ADB_EXEC
    else:
        print("❌ ADB not found and could not be downloaded.")
        input("Press Enter to exit...")
        exit(1)

def list_connected_devices():
    adb_path = ensure_adb()
    try:
        result = subprocess.check_output([adb_path, "devices"], stderr=subprocess.STDOUT, text=True)
        lines = result.strip().split("\n")[1:]  # Skip header
        devices = [line.split("\t")[0] for line in lines if "device" in line]
        return devices
    except subprocess.CalledProcessError as e:
        print("Error checking devices:", e.output)
        return []

def check_usb_debugging():
    devices = list_connected_devices()
    if devices:
        print(f"📱 Connected Android device(s): {devices}")
        return devices[0]  # Use the first device
    else:
        print("⚠️ No device found. Please enable Developer Options and USB Debugging, then reconnect.")
        return None

def start_wifi_debugging():
    adb_path = ensure_adb()
    try:
        subprocess.check_call([adb_path, "tcpip", "5555"])
        print("📡 ADB over Wi-Fi started. Now connect to the device IP using: adb connect <device_ip>")
    except subprocess.CalledProcessError:
        print("❌ Failed to start ADB over Wi-Fi.")
