import os
import time

def cleanup_old_files(folder='.', prefixes=('screenshot_', 'dump_'), age_limit_minutes=10):
    """
    Deletes files starting with specified prefixes and older than `age_limit_minutes`.
    """
    now = time.time()
    age_limit_seconds = age_limit_minutes * 60

    for filename in os.listdir(folder):
        for prefix in prefixes:
            if filename.startswith(prefix) and (filename.endswith('.png') or filename.endswith('.xml')):
                filepath = os.path.join(folder, filename)
                try:
                    if os.path.isfile(filepath):
                        file_age = now - os.path.getmtime(filepath)
                        if file_age > age_limit_seconds:
                            os.remove(filepath)
                            print(f"Deleted old file: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

if __name__ == "__main__":
    print("🧹 Cleaning up old files...")
    cleanup_old_files(folder='.', prefixes=('screenshot_', 'dump_'), age_limit_minutes=10)
    print("Cleanup complete.")