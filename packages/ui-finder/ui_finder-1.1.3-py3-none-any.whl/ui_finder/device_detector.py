# File: ui_finder/device_detector.py

import subprocess
import time
from ui_finder.adb_utils import get_adb_path

def list_connected_devices():
    adb_path = get_adb_path()
    try:
        output = subprocess.check_output([adb_path, "devices"], encoding="utf-8")
        lines = output.strip().splitlines()
        devices = [line.split('\t')[0] for line in lines[1:] if '\tdevice' in line]
        return devices
    except subprocess.CalledProcessError as e:
        print("Failed to list devices:", e)
        return []

def is_developer_mode_ready():
    devices = list_connected_devices()
    if not devices:
        print(" No devices found. Ensure:")
        print("   - USB cable is connected")
        print("   - Developer mode is enabled")
        print("   - USB debugging is turned ON")
        return False
    print(" Device connected:", devices[0])
    return True

def try_connect_over_wifi(ip):
    adb_path = get_adb_path()
    try:
        subprocess.check_call([adb_path, "connect", ip])
        print(f"Connected to {ip} via Wi-Fi")
        return True
    except subprocess.CalledProcessError as e:
        print("Wi-Fi ADB connection failed:", e)
        return False

if __name__ == "__main__":
    print("🔍 Checking ADB setup...")
    
    for i in range(3):
        if is_developer_mode_ready():
            break
        print(f"Retrying in 5 seconds ({i+1}/3)...")
        time.sleep(5)
    else:
        # Optional Wi-Fi fallback
        user_ip = input("Enter phone IP (for Wi-Fi ADB): ")
        try_connect_over_wifi(user_ip)
