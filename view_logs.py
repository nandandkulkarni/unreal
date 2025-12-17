"""
View the camera binding fix log file
Run this in PowerShell to see the latest log:
    python view_logs.py
"""

import os
from datetime import datetime

LOG_FILE = r"C:\U\CinematicPipeline_Scripts\logs\camera_binding_fix.log"

def view_log():
    if not os.path.exists(LOG_FILE):
        print(f"Log file not found: {LOG_FILE}")
        print("Run fix_camera_binding.py in Unreal first.")
        return
    
    print("=" * 70)
    print("CAMERA BINDING FIX LOG")
    print("=" * 70)
    print(f"File: {LOG_FILE}")
    print(f"Size: {os.path.getsize(LOG_FILE)} bytes")
    print(f"Last modified: {datetime.fromtimestamp(os.path.getmtime(LOG_FILE))}")
    print("=" * 70)
    print()
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    print("\n" + "=" * 70)
    print("END OF LOG")
    print("=" * 70)

if __name__ == "__main__":
    view_log()
