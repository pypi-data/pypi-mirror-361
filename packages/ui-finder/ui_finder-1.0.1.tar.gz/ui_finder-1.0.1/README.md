# 📱 Android UI Inspector

**Android UI Inspector** is a Python-based visual tool that helps you inspect and analyze the UI hierarchy of Android apps directly from a real Android phone.

It allows you to:

- Load a screenshot and corresponding `uiautomator dump` XML from your device
- Visually click on any UI element to inspect its attributes
- Highlight the clicked element on the UI
- Copy key attributes like `class`, `resource-id`, `text`, and `bounds`

> Ideal for testers, automation engineers, and Android developers working with real devices.

---

## 🚀 Features

✅ Uses real Android phone (no emulator needed)  
✅ Visualizes UI using actual screenshots  
✅ Click to highlight any UI element  
✅ Attribute panel with dropdown filter  
✅ One-click copy to clipboard  
✅ Works offline (pure Python, no server)  
✅ Cross-platform (Windows, Linux, macOS)

---

## 📲 Requirements

- **A real Android phone** with:
  - USB debugging enabled
  - `adb` installed and accessible in terminal
- Python 3.7+
- Screenshot (`Image.jpg`) and UI XML (`uiautomator dump`) from the phone

---

## 📸 How to Prepare Your Device

1. **Enable Developer Mode** on your phone  
2. **Enable USB Debugging**
3. Connect phone via USB and run:

```bash
adb devices         # To verify connection
adb shell uiautomator dump
adb pull /sdcard/window_dump.xml
adb exec-out screencap -p > Image.jpg









