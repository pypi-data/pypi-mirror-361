# File: ui_finder/main.py
import os
import subprocess
from . import adb_utils, device_utils, viewer

def run():
    # adb_path = adb_utils.download_and_extract_adb()
    adb_path = adb_utils.get_adb_path()
    if not adb_path:
        print("ADB not found. Please ensure it is installed and in your PATH.")
        return
    device = device_utils.is_device_connected(adb_path)

    if not device:
        print("\nNo device connected or USB debugging not enabled.")
        print("Please connect a device and enable USB Debugging from Developer Options.")
        return

    print(f"\n📱 Device connected: {device}")

    # Dump UI XML
    subprocess.run([adb_path, 'shell', 'uiautomator', 'dump'])
    subprocess.run([adb_path, 'pull', '/sdcard/window_dump.xml', 'dump.xml'])

    # Capture screenshot
    with open("screenshot.png", "wb") as f:
        subprocess.run([adb_path, "exec-out", "screencap", "-p"], stdout=f)

    # Launch viewer
    viewer.start("screenshot.png", "dump.xml")
    # viewer.start("screenshot.png", "dump.xml", adb_path)



# This function is the CLI entry point
def main():
    run()