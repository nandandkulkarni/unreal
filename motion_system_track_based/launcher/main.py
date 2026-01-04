
import tkinter as tk
from tkinter import messagebox
import os
import sys

# Add parent directory to sys.path so we can import motion_includes
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from launcher.model import LauncherModel
from launcher.view_model import LauncherViewModel
from launcher.view import LauncherView

def main():
    root = tk.Tk()
    
    # Init Model
    model = LauncherModel(parent_dir)
    
    # Check Single Instance
    lock = model.acquire_lock()
    if not lock:
        root.withdraw()
        messagebox.showwarning("Launcher Running", "Another instance is already running!")
        root.destroy()
        return

    # Keep lock check active? 
    # In original it held the file handle open.
    # Here model.acquire_lock() returns the handle. We must keep it.
    
    # Create View (Injects Model + VM)
    app = LauncherView(root, LauncherModel, LauncherViewModel)
    
    try:
        root.mainloop()
    finally:
        model.release_lock(lock)

if __name__ == "__main__":
    main()
