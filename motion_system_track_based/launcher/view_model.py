
import tkinter as tk
from tkinter import messagebox
import threading
import sys
import subprocess
import os

from launcher.model import LauncherModel
from motion_includes.assets import Characters

class LauncherViewModel:
    def __init__(self, model: LauncherModel, view_callback_interface):
        self.model = model
        self.view = view_callback_interface # Callbacks for UI updates (e.g. log_to_console)
        
        # Observable State
        self.status_var = tk.StringVar(value="Ready")
        self.selected_movie = tk.StringVar()
        self.focal_val = tk.DoubleVar(value=85.0)
        self.set_height_val = tk.StringVar(value="1.8")
        self.actual_height_val = tk.StringVar(value="1.8")
        self.char_name_var = tk.StringVar(value="BELICA")
        
        # Lists
        self.movie_list = self.model.get_movie_list()
        
    def start(self):
        """Called after View is fully ready"""
        # Setup Triggers
        self.selected_movie.trace_add("write", self.on_movie_selected)
        
        # Load Initial State
        last = self.model.load_last_selection()
        if last and last in self.movie_list:
            self.selected_movie.set(last)
        else:
             # Default selection to trigger UI update even if None
             if self.movie_list:
                  self.selected_movie.set(self.movie_list[0])

    def on_movie_selected(self, *args):
        movie = self.selected_movie.get()
        # Notify view to toggle exploration controls
        self.view.toggle_exploration_controls(movie == "camera_settings_exploration.py")
        
        if movie == "camera_settings_exploration.py":
            settings = self.model.read_exploration_settings()
            if "focal_length" in settings:
                self.focal_val.set(float(settings["focal_length"]))
            if "set_height" in settings:
                self.set_height_val.set(settings["set_height"])
            if "actual_height" in settings:
                self.actual_height_val.set(settings["actual_height"])

    def update_script(self):
        focal = self.focal_val.get()
        set_h = self.set_height_val.get()
        act_h = self.actual_height_val.get()
        
        success, msg = self.model.update_exploration_script(focal, set_h, act_h)
        if success:
            self.status_var.set("Updated script settings")
            self.view.log(f">>> {msg}")
        else:
            self.view.show_error(msg)

    def run_movie(self):
        movie = self.selected_movie.get()
        if not movie:
            self.view.show_warn("Please select a movie script first!")
            return

        self.model.save_selection(movie)
        
        self.view.set_running_state(True)
        self.status_var.set(f"Running {movie}...")
        self.view.clear_console()
        
        log_file = self.model.prepare_log_file(movie)
        self.view.log(f">>> STARTING: {movie}")
        self.view.log(f">>> LOG FILE: {log_file}")
        
        # Run in thread
        threading.Thread(target=self._execute_script_thread, args=(movie, log_file)).start()

    def _execute_script_thread(self, movie, log_file_path):
        script_path = os.path.join(self.model.movies_dir, movie)
        try:
            with open(log_file_path, 'w', encoding='utf-8') as log_file:
                # Use sys.executable to ensure same python env
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=self.model.root_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in iter(process.stdout.readline, ""):
                     self.view.log(line.strip())
                     log_file.write(line)
                     log_file.flush()
                
                process.stdout.close()
                rc = process.wait()
            
            self.view.on_execution_finished(rc == 0, log_file_path)

        except Exception as e:
            self.view.log(f"Error: {e}")
            self.view.on_execution_finished(False, log_file_path)

    def run_measure_tool(self):
        char_name = self.char_name_var.get().strip()
        if not char_name:
            self.view.show_warn("Please select a character!")
            return

        self.view.log(f">>> MEASURING: {char_name}")
        self.view.set_measure_state(True)
        
        def _run():
            try:
                # Assuming measure_character.py is in root
                script = os.path.join(self.model.root_dir, "measure_character.py")
                process = subprocess.Popen(
                    [sys.executable, script, char_name],
                    cwd=self.model.root_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                out, _ = process.communicate()
                
                height_val = None
                for line in out.splitlines():
                    self.view.log(line)
                    if "Height:" in line:
                         height_val = line
                
                self.view.on_measure_finished(height_val)
                
            except Exception as e:
                self.view.log(f"Error: {e}")
                self.view.on_measure_finished(None)

        threading.Thread(target=_run).start()

    def process_measure_result(self, result_line):
        """Parses output line from measure tool"""
        if result_line:
             try:
                 # "Height: 180.00 cm ..."
                 parts = result_line.split()
                 val_cm = float(parts[1])
                 val_m = val_cm / 100.0
                 self.actual_height_val.set(f"{val_m:.2f}")
                 
                 # Check if update allowed
                 name = self.char_name_var.get().strip()
                 if hasattr(Characters, name):
                     self.view.enable_update_asset(True)
                     self.view.log(f">>> ENABLED UPDATE for {name}")
                 else:
                     self.view.enable_update_asset(False)
                     self.view.log(f">>> CANNOT UPDATE: {name} unknown")
                     
                 self.view.show_info(f"Measurement Complete:\n{result_line}")
             except Exception as e:
                 self.view.show_warn(f"Parse Error: {e}")
        else:
            self.view.show_warn("Measurement inconclusive.")

    def update_asset(self):
        name = self.char_name_var.get().strip()
        try:
             height = float(self.actual_height_val.get())
             success, msg = self.model.update_asset_file(name, height)
             if success:
                 self.view.log(f">>> {msg}")
                 self.view.show_info(msg)
                 self.view.enable_update_asset(False)
             else:
                 self.view.show_warn(msg)
        except ValueError:
            self.view.show_error("Invalid height value")

    def cleanup(self):
        if self.view.ask_confirm("Confirm Cleanup", "Delete dist/ and logs?"):
            count = self.model.cleanup_workspace()
            self.view.log(f">>> CLEANUP: Removed {count} items")
            self.status_var.set(f"Cleaned {count} items")
