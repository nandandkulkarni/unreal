"""
Movie Launcher UI - Native Python (Tkinter)
A utility to select and run movie scripts from the movies/ folder.
Features single-instance enforcement and dynamic focal length controls for exploration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import subprocess
import threading
import sys
import datetime
import re
from motion_includes.assets import Characters

# Constants
CONFIG_FILE = "launcher_config.jsonx"
MOVIES_DIR = "movies"
LOGS_DIR = "launcher_logs"
LOCK_FILE = "launcher.lock"
EXPLORATION_SCRIPT = "camera_settings_exploration.py"
FOCAL_LENGTH_TAG = "[EDITABLE_FOCAL_LENGTH]"
SET_HEIGHT_TAG = "[EDITABLE_SET_HEIGHT]"
ACTUAL_HEIGHT_TAG = "[EDITABLE_ACTUAL_HEIGHT]"

class MovieLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unreal Movie Launcher")
        self.root.geometry("600x650")
        self.root.configure(bg="#1e1e1e")  # Dark theme
        
        # Single Instance Check
        self.lock_file_handle = None
        if not self.acquire_lock():
            sys.exit(0)

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
        self.combo.bind("<<ComboboxSelected>>", self.on_movie_selected)
        
        # --- Focal Length Controls (Conditional) ---
        self.focal_frame = tk.Frame(root, bg="#2a2a2a", padx=15, pady=15, highlightbackground="#3d3d3d", highlightthickness=1)
        
        foc_lbl = tk.Label(self.focal_frame, text="EXPLORATION FOCAL LENGTH (mm):", bg="#2a2a2a", fg="#3498db", font=("Segoe UI", 9, "bold"))
        foc_lbl.pack(anchor=tk.W)
        
        slider_frame = tk.Frame(self.focal_frame, bg="#2a2a2a")
        slider_frame.pack(fill=tk.X, pady=5)
        
        self.focal_val = tk.DoubleVar(value=85.0)
        self.focal_slider = tk.Scale(slider_frame, from_=5, to=5000, orient=tk.HORIZONTAL, 
                                     variable=self.focal_val, bg="#2a2a2a", fg="white", 
                                     highlightthickness=0, troughcolor="#3e3e3e", showvalue=0)
        self.focal_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.focal_entry = tk.Entry(slider_frame, width=6, bg="#1e1e1e", fg="white", borderwidth=0, font=("Consolas", 10), justify=tk.CENTER)
        self.focal_entry.pack(side=tk.LEFT)
        self.focal_entry.insert(0, "85.0")
        
        # --- Height Controls ---
        height_frame = tk.Frame(self.focal_frame, bg="#2a2a2a")
        height_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Set Height (Intended)
        set_h_frame = tk.Frame(height_frame, bg="#2a2a2a")
        set_h_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(set_h_frame, text="SET HEIGHT (m):", bg="#2a2a2a", fg="#bbbbbb", font=("Segoe UI", 8, "bold")).pack()
        self.set_height_val = tk.StringVar(value="1.8")
        self.set_height_entry = tk.Entry(set_h_frame, width=8, bg="#1e1e1e", fg="white", borderwidth=0, font=("Consolas", 10), justify=tk.CENTER, textvariable=self.set_height_val)
        self.set_height_entry.pack(pady=2)
        
        # Actual Height (Measured)
        act_h_frame = tk.Frame(height_frame, bg="#2a2a2a")
        act_h_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(act_h_frame, text="ACTUAL HEIGHT (m):", bg="#2a2a2a", fg="#bbbbbb", font=("Segoe UI", 8, "bold")).pack()
        self.actual_height_val = tk.StringVar(value="1.8")
        self.actual_height_entry = tk.Entry(act_h_frame, width=8, bg="#1e1e1e", fg="white", borderwidth=0, font=("Consolas", 10), justify=tk.CENTER, textvariable=self.actual_height_val)
        self.actual_height_entry.pack(pady=2)
        
        self.update_script_btn = tk.Button(self.focal_frame, text="UPDATE EXPLORATION SCRIPT", 
                                         bg="#d35400", fg="white", font=("Segoe UI", 9, "bold"), 
                                         activebackground="#e67e22", activeforeground="white", 
                                         bd=0, padx=15, pady=8, command=self.update_script_settings)
        self.update_script_btn.pack(pady=(15, 0))

        # Sync slider -> entry
        self.focal_val.trace_add("write", lambda *args: self.sync_val_to_entry())
        # Sync entry -> slider
        self.focal_entry.bind("<Return>", lambda e: self.sync_entry_to_val())
        self.focal_entry.bind("<FocusOut>", lambda e: self.sync_entry_to_val())

        # Load Last Selection
        self.load_config()
        self.on_movie_selected() # Trigger visibility check

        # Button Frame
        btn_frame = tk.Frame(root, bg="#1e1e1e")
        btn_frame.pack(pady=10)

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

        # --- UTILITIES SECTION ---
        util_frame = tk.LabelFrame(root, text="UTILITIES", bg="#1e1e1e", fg="#3498db", font=("Segoe UI", 10, "bold"), labelanchor="n")
        util_frame.pack(fill=tk.X, padx=20, pady=15)

        # Character Height Tool
        h_frame = tk.Frame(util_frame, bg="#1e1e1e", pady=10)
        h_frame.pack(fill=tk.X)
        
        
        tk.Label(h_frame, text="Measure Character Height:", bg="#1e1e1e", fg="#bbbbbb").pack(side=tk.LEFT, padx=10)
        
        # Get character names from Assets
        char_names = sorted([k for k in dir(Characters) if k.isupper() and not k.startswith("_")])
        
        self.char_name_var = tk.StringVar(value="BELICA")
        self.char_entry = ttk.Combobox(h_frame, textvariable=self.char_name_var, values=char_names, width=20)
        self.char_entry.pack(side=tk.LEFT, padx=5)
        
        self.measure_btn = tk.Button(h_frame, text="MEASURE", font=("Segoe UI", 8, "bold"),
                                   bg="#8e44ad", fg="white", activebackground="#9b59b6", activeforeground="white",
                                   bd=0, padx=10, pady=2, command=self.run_measure_tool)
        self.measure_btn.pack(side=tk.LEFT, padx=10)
        
        self.update_asset_btn = tk.Button(h_frame, text="UPDATE ASSET", font=("Segoe UI", 8, "bold"),
                                   bg="#2980b9", fg="white", activebackground="#3498db", activeforeground="white",
                                   bd=0, padx=10, pady=2, state=tk.DISABLED, command=self.update_asset_file)
        self.update_asset_btn.pack(side=tk.LEFT, padx=10)


        # Cleanup Button (Moved to bottom)
        self.clear_btn = tk.Button(root, text="CLEANUP WORKSPACE", font=("Segoe UI", 8), 
                                 bg="#c0392b", fg="white", activebackground="#e74c3c", 
                                 activeforeground="white", bd=0, padx=10, pady=5, command=self.cleanup_files)
        self.clear_btn.pack(pady=5)

        # Status/Log Area
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                                 bg="#2d2d2d", fg="#888888", font=("Consolas", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.console = tk.Text(root, height=12, bg="#121212", fg="#00ff00", font=("Consolas", 8), borderwidth=0)
        self.console.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Ensure lock is released on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_asset_file(self):
        """Updates the height in assets.py for the selected character"""
        new_height_str = self.actual_height_val.get()
        
        if not char_name or not new_height_str:
            return
            
        try:
            new_height = float(new_height_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid height value")
            return

        # Path to assets.py
        assets_path = os.path.join("motion_includes", "assets.py")
        if not os.path.exists(assets_path):
             messagebox.showerror("Error", "assets.py not found")
             return
             
        try:
            with open(assets_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Regex to find: NAME = CharacterData("...", HEIGHT, ...)
            # We want to match explicitly the NAME = part to be sure.
            # Pattern: (NAME\s*=\s*CharacterData\s*\()(?:[^,]+,\s*)([\d.]+)(.*?\))
            # Wait, arguments inside parenthesis: Path (string), Height (float), Yaw (float, optional)
            
            # More robust pattern:
            # 1. Start with name: \s+NAME\s*=\s*CharacterData\(
            # 2. Path arg: [^,]+,\s*
            # 3. Height arg (capture group): ([\d.]+)
            
            pattern = rf"(\s+{re.escape(char_name)}\s*=\s*CharacterData\s*\(\s*[^,]+,\s*)([\d.]+)"
            
            match = re.search(pattern, content)
            if match:
                # check if change needed
                current_val = float(match.group(2))
                if abs(current_val - new_height) < 0.001:
                    messagebox.showinfo("Info", f"Height for {char_name} is already {new_height}")
                    return
                
                # Replace
                new_content = re.sub(pattern, rf"\g<1>{new_height}", content, count=1)
                
                with open(assets_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                self.log_to_console(f">>> UPDATED {char_name} HEIGHT: {current_val} -> {new_height}")
                messagebox.showinfo("Success", f"Updated {char_name} height to {new_height} in assets.py")
                self.update_asset_btn.config(state=tk.DISABLED)
            else:
                messagebox.showwarning("Not Found", f"Could not find definition for {char_name} in assets.py")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update asset: {e}")

    
    def on_measure_complete(self, result, error=None):
        self.measure_btn.config(state=tk.NORMAL, text="MEASURE")
        if error:
            # ... error handling ...
            self.log_to_console(f">>> ERROR: {error}")
            messagebox.showerror("Measurement Failed", error)
        else:
            self.log_to_console(f">>> RESULT: {result}")
            if result and "Height:" in result:
                # Try to parse the numeric value
                try:
                    # format: "Height: 180.00 cm (Source: Capsule)"
                    parts = result.split() # ["Height:", "180.00", "cm", ...]
                    val_cm = float(parts[1])
                    val_m = val_cm / 100.0
                    self.actual_height_val.set(f"{val_m:.2f}") # Auto-fill Actual Height field
                    
                    # Enable Update Button if it's a known character
                    selected_name = self.char_name_var.get().strip()
                    is_known = hasattr(Characters, selected_name)
                    if is_known:
                         self.log_to_console(f">>> ENABLED UPDATE for {selected_name}")
                         self.update_asset_btn.config(state=tk.NORMAL)
                    else:
                         self.log_to_console(f">>> CANNOT UPDATE: {selected_name} not in Assets")
                    
                    messagebox.showinfo("Measurement Complete", f"{result}\n\nValue copied to Actual Height field.")
                except Exception as e:
                    print(e)
                    messagebox.showinfo("Measurement Complete", result)
            else:
                 messagebox.showwarning("Measurement Inconclusive", "Could not find valid height in output.\nCheck console log.")

    def sync_val_to_entry(self):
        val = self.focal_val.get()
        self.focal_entry.delete(0, tk.END)
        self.focal_entry.insert(0, f"{val:.1f}")

    def sync_entry_to_val(self):
        try:
            val = float(self.focal_entry.get())
            self.focal_val.set(val)
        except ValueError:
            self.sync_val_to_entry()

    def on_movie_selected(self, event=None):
        movie = self.selected_movie.get()
        if movie == EXPLORATION_SCRIPT:
            self.focal_frame.pack(pady=10, fill=tk.X, padx=20)
            self.read_settings_from_script()
        else:
            self.focal_frame.pack_forget()

    def read_settings_from_script(self):
        script_path = os.path.join(MOVIES_DIR, EXPLORATION_SCRIPT)
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Focal Length
                    foc_pattern = rf"FOCAL_LENGTH\s*=\s*([\d.]+)\s*#\s*{re.escape(FOCAL_LENGTH_TAG)}"
                    foc_match = re.search(foc_pattern, content)
                    if foc_match:
                        self.focal_val.set(float(foc_match.group(1)))
                    
                    # Set Height
                    set_h_pattern = rf"SET_HEIGHT\s*=\s*([\d.]+)\s*#\s*{re.escape(SET_HEIGHT_TAG)}"
                    set_h_match = re.search(set_h_pattern, content)
                    if set_h_match:
                        self.set_height_val.set(set_h_match.group(1))
                    
                    # Actual Height
                    act_h_pattern = rf"ACTUAL_HEIGHT\s*=\s*([\d.]+)\s*#\s*{re.escape(ACTUAL_HEIGHT_TAG)}"
                    act_h_match = re.search(act_h_pattern, content)
                    if act_h_match:
                        self.actual_height_val.set(act_h_match.group(1))
                        
            except Exception as e:
                print(f"Error reading script settings: {e}")

    def update_script_settings(self):
        script_path = os.path.join(MOVIES_DIR, EXPLORATION_SCRIPT)
        
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"Script not found: {script_path}")
            return

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            updates = [
                (rf"FOCAL_LENGTH\s*=\s*([\d.]+)\s*#\s*{re.escape(FOCAL_LENGTH_TAG)}", 
                 f"FOCAL_LENGTH = {self.focal_val.get():.1f}  # {FOCAL_LENGTH_TAG}"),
                
                (rf"SET_HEIGHT\s*=\s*([\d.]+)\s*#\s*{re.escape(SET_HEIGHT_TAG)}", 
                 f"SET_HEIGHT = {self.set_height_val.get()}  # {SET_HEIGHT_TAG}"),
                
                (rf"ACTUAL_HEIGHT\s*=\s*([\d.]+)\s*#\s*{re.escape(ACTUAL_HEIGHT_TAG)}", 
                 f"ACTUAL_HEIGHT = {self.actual_height_val.get()}  # {ACTUAL_HEIGHT_TAG}")
            ]
            
            new_content = content
            changed = False
            for pattern, replacement in updates:
                if re.search(pattern, new_content):
                    new_content = re.sub(pattern, replacement, new_content)
                    changed = True
            
            if changed:
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.status_var.set("Updated script settings")
                self.log_to_console(f">>> UPDATED SCRIPT: {EXPLORATION_SCRIPT}")
            else:
                # Only show error if NO markers were found at all
                pass 
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update script: {e}")

    def acquire_lock(self):
        """Tries to acquire an exclusive lock on the lock file"""
        try:
            if os.path.exists(LOCK_FILE):
                try:
                    os.remove(LOCK_FILE)
                except OSError:
                    return False
            self.lock_file_handle = open(LOCK_FILE, 'w')
            self.lock_file_handle.write(str(os.getpid()))
            self.lock_file_handle.flush()
            return True
        except Exception:
            return False

    def on_closing(self):
        """Cleanup before exiting"""
        if self.lock_file_handle:
            self.lock_file_handle.close()
            try:
                os.remove(LOCK_FILE)
            except Exception:
                pass
        self.root.destroy()

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
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=os.getcwd(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in iter(process.stdout.readline, ""):
                    self.log_to_console(line.strip())
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
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, self.last_log_file])

    def cleanup_files(self):
        """Deletes all generated data and logs"""
        if not messagebox.askyesno("Confirm Cleanup", "This will delete all generated track files (dist/) and launcher logs. Proceed?"):
            return
            
        import shutil
        count = 0
        
        # Cleanup dist/
        dist_dir = "dist"
        if os.path.exists(dist_dir):
            try:
                for root_dir, dirs, files in os.walk(dist_dir):
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

    def run_measure_tool(self):
        """Runs the measure_character.py script"""
        char_name = self.char_name_var.get().strip()
        if not char_name:
            messagebox.showwarning("Input Required", "Please enter a character name or path.")
            return

        self.log_to_console(f">>> MEASURING CHARACTER: {char_name}")
        self.measure_btn.config(state=tk.DISABLED, text="WAIT...")
        
        # Use subprocess to run the tool
        script_path = "measure_character.py"
        
        def _run():
            try:
                process = subprocess.Popen(
                    [sys.executable, script_path, char_name],
                    cwd=os.getcwd(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                output, _ = process.communicate()
                
                # Check output for "Height:" line
                height_val = "Unknown"
                for line in output.splitlines():
                    self.log_to_console(line)
                    if "Height:" in line:
                        height_val = line.strip()
                
                self.root.after(0, lambda: self.on_measure_complete(height_val))
                
            except Exception as e:
                self.root.after(0, lambda: self.on_measure_complete(None, str(e)))

        threading.Thread(target=_run).start()

    def on_measure_complete(self, result, error=None):
        self.measure_btn.config(state=tk.NORMAL, text="MEASURE")
        if error:
            self.log_to_console(f">>> ERROR: {error}")
            messagebox.showerror("Measurement Failed", error)
        else:
            self.log_to_console(f">>> RESULT: {result}")
            if result and "Height:" in result:
                # Try to parse the numeric value
                try:
                    # format: "Height: 180.00 cm (Source: Capsule)"
                    parts = result.split() # ["Height:", "180.00", "cm", ...]
                    val = parts[1]
                    self.actual_height_val.set(val) # Auto-fill Actual Height field
                    messagebox.showinfo("Measurement Complete", f"{result}\n\nValue copied to Actual Height field.")
                except:
                    messagebox.showinfo("Measurement Complete", result)
            else:
                 messagebox.showwarning("Measurement Inconclusive", "Could not find valid height in output.\nCheck console log.")

def check_single_instance():
    """Independent check for single instance before launching UI"""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            return True
        except OSError:
            return False
    return True

if __name__ == "__main__":
    if not check_single_instance():
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showwarning("Launcher Running", "Another instance of the Movie Launcher is already running!")
        temp_root.destroy()
        sys.exit(0)

    root = tk.Tk()
    app = MovieLauncherApp(root)
    root.mainloop()
