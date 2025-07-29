# File: ui_finder/device_utils.py
import subprocess

def is_device_connected(adb_path):
    try:
        result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()
        connected = [line for line in lines[1:] if 'device' in line and not 'unauthorized' in line]
        return connected[0].split('\t')[0] if connected else None
    except Exception as e:
        print(f"ADB check error: {e}")
        return None

def check_usb_debugging(adb_path):
    try:
        result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True)
        return 'unauthorized' not in result.stdout
    except:
        return False

def enable_wifi_debugging(adb_path):
    subprocess.run([adb_path, 'tcpip', '5555'])
    print("Now connect over Wi-Fi using: adb connect <device-ip>:5555")


# File: ui_finder/parser.py
def parse_bounds(bounds_str):
    return [int(x) for x in bounds_str.replace('[', '').replace(']', ',').split(',') if x]

def is_within_bounds(x, y, bounds):
    return bounds[0] <= x <= bounds[2] and bounds[1] <= y <= bounds[3]
