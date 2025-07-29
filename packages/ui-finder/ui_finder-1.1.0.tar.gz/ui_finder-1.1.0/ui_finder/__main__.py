# File: ui_finder/__main__.py

# from ui_finder.startup_check import startup_procedure
# from ui_finder.viewer import start_ui_inspector  # Your main app logic entry point


# def main():
#     startup_procedure()
#     start_ui_inspector()  # This should load the image and XML, and start the GUI


# if __name__ == "__main__":
#     main()


from ui_finder.viewer import start_ui_inspector
print("🔍 Starting UI Finder...")
from ui_finder.viewer import start_ui_inspector
from ui_finder.adb_utils import ensure_device_connected
from ui_finder.dep_check import check_and_install_dependencies

def main():
    check_and_install_dependencies()
    device_id = ensure_device_connected()
    if not device_id:
        print("❌ Could not connect to device.")
        return
    start_ui_inspector()

if __name__ == "__main__":
    main()
