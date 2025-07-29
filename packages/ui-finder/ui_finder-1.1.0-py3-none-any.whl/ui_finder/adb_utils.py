import os
import sys
import platform
import zipfile
import shutil
import subprocess
from urllib.request import urlretrieve

def get_platform_tools_url():
    system = platform.system().lower()
    if 'windows' in system:
        return "https://github.com/kdiitg/ui_finder_adb/releases/download/v1.0.0/platform-tools-latest-windows.zip"
    elif 'linux' in system:
        return "https://github.com/kdiitg/ui_finder_adb/releases/download/v1.0.0/platform-tools-latest-linux.zip"
    elif 'darwin' in system:  # macOS
        return "https://github.com/kdiitg/ui_finder_adb/releases/download/v1.0.0/platform-tools-latest-darwin.zip"
    else:
        raise RuntimeError("Unsupported OS. Only Windows, Linux, and macOS are supported.")

def get_adb_path():
    tools_dir = os.path.join(os.path.expanduser("~"), ".ui_finder_tools")
    adb_path = os.path.join(tools_dir, "platform-tools", "adb")

    if platform.system().lower().startswith("win"):
        adb_path += ".exe"

    if not os.path.exists(adb_path):
        print("Downloading ADB (platform-tools)...")
        url = get_platform_tools_url()
        zip_path = os.path.join(tools_dir, "platform-tools.zip")

        os.makedirs(tools_dir, exist_ok=True)
        urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tools_dir)
        os.remove(zip_path)

    return adb_path

def get_connected_devices(adb_path):
    try:
        result = subprocess.check_output([adb_path, 'devices'], encoding='utf-8')
        lines = result.strip().split("\n")
        devices = [line.split()[0] for line in lines[1:] if 'device' in line]
        return devices
    except subprocess.CalledProcessError:
        return []


def ensure_device_connected(adb_path):
    print("\nChecking for connected devices...")
    devices = get_connected_devices(adb_path)

    if devices:
        print(f"✅ Device connected: {devices[0]}")
        return devices[0]

    print("❌ No device found.\n📲 Please check:")
    print("  1. USB cable is properly connected")
    print("  2. Developer Mode is enabled")
    print("  3. USB Debugging is turned ON")
    print("\n📡 Option: Connect over Wi-Fi (experimental)")

    ip = input("Enter device IP address (or leave blank to skip): ").strip()
    if ip:
        try:
            subprocess.run([adb_path, "connect", ip], check=True)
            devices = get_connected_devices(adb_path)
            if devices:
                print(f"✅ Connected via Wi-Fi: {devices[0]}")
                return devices[0]
            else:
                print("❌ Still no device found.")
        except subprocess.CalledProcessError as e:
            print("❌ Failed to connect via Wi-Fi:", e)

    input("Press Enter to exit...")
    sys.exit(1)
