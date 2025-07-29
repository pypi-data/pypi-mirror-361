# 📱 Android UI Inspector

**Android UI Inspector** is a plug-and-play Python-based visual tool to inspect and analyze the UI of Android apps directly from your phone.

🔧 No manual setup needed — it installs `ADB`, `matplotlib`, and `pyperclip` automatically and works across **Windows**, **Linux**, and **macOS**.

---

## 🚀 Features

✅ Auto-installs ADB (platform-tools) for your OS  
✅ Installs Python dependencies automatically  
✅ Connects to real Android devices via USB or Wi-Fi  
✅ Live UI screenshot + hierarchy dump  
✅ Click on UI elements to highlight and inspect them  
✅ Dropdown filter: `class`, `resource-id`, `text`, `bounds`  
✅ One-click **Copy to Clipboard**  
✅ Press `n` to cycle overlapping elements  
✅ Press `r` or click "Refresh Screen" to reload live UI  
✅ Cleans up old screenshots/XML files (older than 10 minutes)  
✅ Cross-platform (Windows, macOS, Linux)  
✅ Works offline after first run

---

## 📲 Requirements

- Android phone with:
  - Developer Mode enabled
  - USB Debugging turned ON
- Python 3.7 or higher
- Internet connection (for first run only)

---

## 🖥 How to Use (All OS)

1. **Clone the repo**
   ```bash
   git clone https://github.com/kdiitg/ui-finder.git
   cd ui_finder
   

2. **In Windows**
   ```
   pip install ui_finder
   In cmd or powershell just type either ui_finder or android_inspector or uif or adr
   ui_finder

3. **In Linux/MacOS**
   ```
   pip3 install ui_finder
   ui_finder