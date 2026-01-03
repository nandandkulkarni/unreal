"""
Movie Launcher UI - Native Python (Tkinter)
A utility to select and run movie scripts from the movies/ folder.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import subprocess
import threading
import sys
import datetime

# Constants
CONFIG_FILE = "launcher_config.jsonx"
MOVIES_DIR = "movies"
LOGS_DIR = "launcher_logs"

class MovieLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unreal Movie Launcher")
        self.root.geometry("550x500")
        self.root.configure(bg="#1e1e1e")  # Dark theme
        
        self.last_log_file = None
        
        # Ensure logs dir exists
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TCombobox", fieldbackground="#2d2d2d", background="#1e1e1e", foreground="white")
        self.style.configure("TButton", background="#3e3e3e", foreground="white", borderwidth=0)
        self.style.map("TButton", background=[('active', '#505050')])

        # Header
        header = tk.Label(root, text="MOVIEMAKER CONTROL", font=("Segoe UI", 16, "bold"), bg="#1e1e1e", fg="#3498db")
        header.pack(pady=20)

        # Dropdown Label
        lbl = tk.Label(root, text="Select Movie Script:", font=("Segoe UI", 10), bg="#1e1e1e", fg="#bbbbbb")
        lbl.pack(pady=(10, 5))

        # Movie List
        self.movies = self.get_movie_list()
        self.selected_movie = tk.StringVar()
        
        self.combo = ttk.Combobox(root, textvariable=self.selected_movie, values=self.movies, state="readonly", width=40)
        self.combo.pack(pady=5)
        
        # Load Last Selection
        self.load_config()

        # Button Frame
        btn_frame = tk.Frame(root, bg="#1e1e1e")
        btn_frame.pack(pady=20)

        # Run Button
        self.run_btn = tk.Button(btn_frame, text="RUN SEQUENCE", font=("Segoe UI", 12, "bold"), 
                               bg="#27ae60", fg="white", activebackground="#2ecc71", 
                               activeforeground="white", bd=0, padx=20, pady=10, command=self.run_movie)
        self.run_btn.pack(side=tk.LEFT, padx=10)

        # View Log Button
        self.log_btn = tk.Button(btn_frame, text="VIEW LAST LOG", font=("Segoe UI", 10), 
                               bg="#34495e", fg="white", activebackground="#2c3e50", 
                               activeforeground="white", bd=0, padx=15, pady=10, state=tk.DISABLED, command=self.open_last_log)
        self.log_btn.pack(side=tk.LEFT, padx=10)

        # Cleanup Button
        self.clear_btn = tk.Button(root, text="CLEANUP WORKSPACE (Delete Tracks/Logs)", font=("Segoe UI", 9), 
                                 bg="#c0392b", fg="white", activebackground="#e74c3c", 
                                 activeforeground="white", bd=0, padx=10, pady=5, command=self.cleanup_files)
        self.clear_btn.pack(pady=5)

        # Status/Log Area
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                                 bg="#2d2d2d", fg="#888888", font=("Consolas", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.console = tk.Text(root, height=12, bg="#121212", fg="#00ff00", font=("Consolas", 8), borderwidth=0)
        self.console.pack(fill=tk.X, padx=20, pady=10)

    def get_movie_list(self):
        """Scans the movies/ folder for .py files"""
        if not os.path.exists(MOVIES_DIR):
            return []
        return [f for f in os.listdir(MOVIES_DIR) if f.endswith(".py") and not f.startswith("__")]

    def load_config(self):
        """Loads last selected movie from jsonx file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    last_movie = data.get("last_selected")
                    if last_movie in self.movies:
                        self.selected_movie.set(last_movie)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        """Saves current selection to jsonx file"""
        data = {"last_selected": self.selected_movie.get()}
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def log_to_console(self, text):
        self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)

    def run_movie(self):
        movie = self.selected_movie.get()
        if not movie:
            messagebox.showwarning("Warning", "Please select a movie script first!")
            return

        self.save_config()
        self.run_btn.config(state=tk.DISABLED, bg="#555555", text="EXECUTING...")
        self.log_btn.config(state=tk.DISABLED)
        
        self.status_var.set(f"Running {movie}...")
        self.console.delete(1.0, tk.END)
        
        # Create unique log file for this run
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.last_log_file = os.path.join(LOGS_DIR, f"launcher_{movie}_{timestamp}.log")
        
        self.log_to_console(f">>> STARTING: {movie}")
        self.log_to_console(f">>> LOG FILE: {self.last_log_file}")
        
        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=self.execute_script, args=(movie, self.last_log_file))
        thread.start()

    def execute_script(self, movie_name, log_file_path):
        script_path = os.path.join(MOVIES_DIR, movie_name)
        try:
            with open(log_file_path, 'w', encoding='utf-8') as log_file:
                # Use same python interpreter as current process
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=os.getcwd(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in iter(process.stdout.readline, ""):
                    stripped_line = line.strip()
                    self.log_to_console(stripped_line)
                    log_file.write(line)
                    log_file.flush()
                
                process.stdout.close()
                return_code = process.wait()
            
            if return_code == 0:
                self.root.after(0, lambda: self.on_execution_complete(True))
            else:
                self.root.after(0, lambda: self.on_execution_complete(False, f"Exited with code {return_code}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.on_execution_complete(False, str(e)))

    def open_last_log(self):
        """Opens the last log file in the default text editor"""
        if self.last_log_file and os.path.exists(self.last_log_file):
            if sys.platform == "win32":
                os.startfile(self.last_log_file)
            else:
                # Fallback for other OSes
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, self.last_log_file])

    def cleanup_files(self):
        """Deletes all generated data and logs"""
        if not messagebox.askyesno("Confirm Cleanup", "This will delete all generated track files (dist/) and launcher logs. Proceed?"):
            return
            
        import shutil
        count = 0
        
        # Cleanup dist/ (more thorough than just json)
        dist_dir = "dist"
        if os.path.exists(dist_dir):
            try:
                # Count files first for logging
                for root, dirs, files in os.walk(dist_dir):
                    count += len(files)
                shutil.rmtree(dist_dir)
                os.makedirs(dist_dir, exist_ok=True)
            except Exception as e:
                self.log_to_console(f"[WARN] Failed to clear dist/: {e}")
        
        # Cleanup launcher_logs/
        if os.path.exists(LOGS_DIR):
            try:
                for file in os.listdir(LOGS_DIR):
                    file_path = os.path.join(LOGS_DIR, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        count += 1
            except Exception as e:
                self.log_to_console(f"[WARN] Failed to clear logs/: {e}")
        
        self.log_to_console(f">>> WORKSPACE CLEANED: Removed ~{count} files/folders")
        self.status_var.set(f"Cleanup Success: {count} items removed")
        self.log_btn.config(state=tk.DISABLED)
        self.last_log_file = None

    def on_execution_complete(self, success, error_msg=""):
        self.run_btn.config(state=tk.NORMAL, bg="#27ae60", text="RUN SEQUENCE")
        self.log_btn.config(state=tk.NORMAL)
        
        if success:
            self.status_var.set("Execution Complete - Success")
            self.log_to_console(">>> SUCCESS")
        else:
            self.status_var.set(f"Execution Failed: {error_msg}")
            self.log_to_console(f">>> FAILED: {error_msg}")
            messagebox.showerror("Error", f"Movie execution failed:\n{error_msg}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLauncherApp(root)
    root.mainloop()
