
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Ensure this matches where main.py runs
from motion_includes.assets import Characters

class LauncherView:
    def __init__(self, root, model_class, vm_class):
        self.root = root
        self.root.title("Unreal Movie Launcher (MVVM)")
        self.root.geometry("600x700")
        self.root.configure(bg="#1e1e1e")
        
        # Initialize MVVM
        self.model = model_class(os.getcwd())
        self.vm = vm_class(self.model, self)
        
        # Setup UI
        self._setup_styles()
        self._build_ui()
        
        # On Close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TCombobox", fieldbackground="#2d2d2d", background="#1e1e1e", foreground="white")
        self.style.configure("TButton", background="#3e3e3e", foreground="white", borderwidth=0)
        self.style.map("TButton", background=[('active', '#505050')])

    def _build_ui(self):
        # Header
        tk.Label(self.root, text="MOVIEMAKER CONTROL", font=("Segoe UI", 16, "bold"), bg="#1e1e1e", fg="#3498db").pack(pady=20)

        # Movie Selection
        tk.Label(self.root, text="Select Movie Script:", font=("Segoe UI", 10), bg="#1e1e1e", fg="#bbbbbb").pack(pady=(10, 5))
        
        self.combo = ttk.Combobox(self.root, textvariable=self.vm.selected_movie, values=self.vm.movie_list, state="readonly", width=40)
        self.combo.pack(pady=5)
        
        # Exploration Controls (Dynamic Frame)
        self.focal_frame = tk.Frame(self.root, bg="#2a2a2a", padx=15, pady=15, highlightbackground="#3d3d3d", highlightthickness=1)
        # Content built once, hidden/shown dynamically
        self._build_exploration_ui()

        # Run Button
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=10)
        
        self.run_btn = tk.Button(btn_frame, text="RUN SEQUENCE", font=("Segoe UI", 12, "bold"), 
                               bg="#27ae60", fg="white", activebackground="#2ecc71", bd=0, padx=20, pady=10, 
                               command=self.vm.run_movie)
        self.run_btn.pack(side=tk.LEFT, padx=10)

        self.log_btn = tk.Button(btn_frame, text="VIEW LOG", font=("Segoe UI", 10), 
                               bg="#34495e", fg="white", bd=0, padx=15, pady=10, state=tk.DISABLED,
                               command=self.open_last_log)
        self.log_btn.pack(side=tk.LEFT, padx=10)
        
        # Utilities
        self._build_utilities_ui()

        # Console & Status
        self.status_bar = tk.Label(self.root, textvariable=self.vm.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                                 bg="#2d2d2d", fg="#888888", font=("Consolas", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.console = tk.Text(self.root, height=12, bg="#121212", fg="#00ff00", font=("Consolas", 8), borderwidth=0)
        self.console.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Start ViewModel (Trigger initial loads now that UI exists)
        self.vm.start()

    def _build_exploration_ui(self):
        # Focal Length
        foc_lbl = tk.Label(self.focal_frame, text="EXPLORATION FOCAL LENGTH (mm):", bg="#2a2a2a", fg="#3498db", font=("Segoe UI", 9, "bold"))
        foc_lbl.pack(anchor=tk.W)
        
        sl_frame = tk.Frame(self.focal_frame, bg="#2a2a2a")
        sl_frame.pack(fill=tk.X, pady=5)
        
        tk.Scale(sl_frame, from_=5, to=5000, orient=tk.HORIZONTAL, variable=self.vm.focal_val, bg="#2a2a2a", fg="white", showvalue=0).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Entry(sl_frame, width=6, bg="#1e1e1e", fg="white", textvariable=self.vm.focal_val).pack(side=tk.LEFT)
        
        # Heights
        h_frame = tk.Frame(self.focal_frame, bg="#2a2a2a")
        h_frame.pack(fill=tk.X, pady=10)
        
        # Set
        f1 = tk.Frame(h_frame, bg="#2a2a2a")
        f1.pack(side=tk.LEFT, expand=True)
        tk.Label(f1, text="SET HEIGHT (m):", bg="#2a2a2a", fg="#bbbbbb", font=("Segoe UI", 8)).pack()
        tk.Entry(f1, width=8, bg="#1e1e1e", fg="white", justify=tk.CENTER, textvariable=self.vm.set_height_val).pack()
        
        # Actual
        f2 = tk.Frame(h_frame, bg="#2a2a2a")
        f2.pack(side=tk.LEFT, expand=True)
        tk.Label(f2, text="ACTUAL HEIGHT (m):", bg="#2a2a2a", fg="#bbbbbb", font=("Segoe UI", 8)).pack()
        tk.Entry(f2, width=8, bg="#1e1e1e", fg="white", justify=tk.CENTER, textvariable=self.vm.actual_height_val).pack()
        
        # Update Script Button
        tk.Button(self.focal_frame, text="UPDATE SCRIPT", bg="#d35400", fg="white", font=("Segoe UI", 9, "bold"),
                  command=self.vm.update_script).pack(pady=10)

    def _build_utilities_ui(self):
        frm = tk.LabelFrame(self.root, text="UTILITIES", bg="#1e1e1e", fg="#3498db", font=("Segoe UI", 10, "bold"))
        frm.pack(fill=tk.X, padx=20, pady=15)
        
        inner = tk.Frame(frm, bg="#1e1e1e", pady=10)
        inner.pack(fill=tk.X)
        
        tk.Label(inner, text="Measure Height:", bg="#1e1e1e", fg="#bbbbbb").pack(side=tk.LEFT, padx=10)
        
        char_names = sorted([k for k in dir(Characters) if k.isupper() and not k.startswith("_")])
        ttk.Combobox(inner, textvariable=self.vm.char_name_var, values=char_names, width=15).pack(side=tk.LEFT, padx=5)
        
        self.measure_btn = tk.Button(inner, text="MEASURE", bg="#8e44ad", fg="white", font=("Segoe UI", 8, "bold"),
                                   command=self.vm.run_measure_tool)
        self.measure_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_asset_btn = tk.Button(inner, text="UPDATE ASSET", bg="#2980b9", fg="white", font=("Segoe UI", 8, "bold"),
                                        state=tk.DISABLED, command=self.vm.update_asset)
        self.update_asset_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(self.root, text="CLEANUP WORKSPACE", bg="#c0392b", fg="white", font=("Segoe UI", 8),
                  command=self.vm.cleanup).pack(pady=5)

    # --- Interface Implementation ---
    def toggle_exploration_controls(self, show):
        if show:
            self.focal_frame.pack(pady=10, fill=tk.X, padx=20)
        else:
            self.focal_frame.pack_forget()

    def log(self, text):
        self.root.after(0, lambda: self._log_safe(text))
        
    def _log_safe(self, text):
        self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)

    def clear_console(self):
        self.console.delete(1.0, tk.END)

    def set_running_state(self, running):
        state = tk.DISABLED if running else tk.NORMAL
        self.run_btn.config(state=state)

    def set_measure_state(self, measuring):
        if measuring:
            self.measure_btn.config(state=tk.DISABLED, text="WAIT...")
        else:
            self.measure_btn.config(state=tk.NORMAL, text="MEASURE")

    def on_execution_finished(self, success, log_path):
        self.root.after(0, lambda: self._finish_exec(success, log_path))

    def _finish_exec(self, success, log_path):
        self.last_log = log_path
        self.log_btn.config(state=tk.NORMAL)
        self.set_running_state(False)
        self.vm.status_var.set("Execution Complete" if success else "Execution Failed")
        if not success:
            messagebox.showerror("Error", "Execution Failed. Check log.")

    def on_measure_finished(self, result_line):
        self.root.after(0, lambda: self._finish_measure(result_line))

    def _finish_measure(self, result_line):
        self.set_measure_state(False)
        self.vm.process_measure_result(result_line)

    def enable_update_asset(self, enable):
        state = tk.NORMAL if enable else tk.DISABLED
        self.update_asset_btn.config(state=state)

    def show_info(self, msg):
        messagebox.showinfo("Info", msg)

    def show_warn(self, msg):
        messagebox.showwarning("Warning", msg)

    def show_error(self, msg):
        messagebox.showerror("Error", msg)

    def ask_confirm(self, title, msg):
        return messagebox.askyesno(title, msg)

    def open_last_log(self):
        if hasattr(self, 'last_log') and os.path.exists(self.last_log):
            os.startfile(self.last_log)

    def on_closing(self):
        self.model.release_lock(self.model.acquire_lock()) # Hacky way to release? Model should hold handle.
        # Actually Model.__init__ doesn't hold handle persistently in this design? 
        # Logic mismatch. Let's fix in Model.
        self.root.destroy()
