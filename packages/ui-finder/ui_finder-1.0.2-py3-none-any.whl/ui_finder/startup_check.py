# File: ui_finder/startup_check.py

import sys
try:
    from ui_finder.dep_check import check_and_install_dependencies
    from ui_finder.adb_utils import get_adb_path
    from ui_finder.device_detector import is_developer_mode_ready
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you have installed the ui_finder package correctly.")
    sys.exit(1)


def startup_procedure():
    print("\nStarting UI Finder...\n")

    # Step 1: Check Python dependencies
    check_and_install_dependencies()

    # Step 2: Verify ADB installation
    adb_path = get_adb_path()
    if not adb_path:
        print("ADB not found and failed to download.")
        sys.exit(1)

    # Step 3: Check device connection & developer mode
    if not is_developer_mode_ready(adb_path):
        print("\nNo Android device ready. Please:")
        print("1. Connect your phone via USB or set up Wi-Fi debugging")
        print("2. Enable Developer Mode")
        print("3. Enable USB Debugging")
        input("\nPress Enter once ready...")
        if not is_developer_mode_ready(adb_path):
            print("Still no device found. Exiting.")
            sys.exit(1)

    print("\nEnvironment ready! Launching the UI Inspector tool...\n")
