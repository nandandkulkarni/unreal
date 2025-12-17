"""
Cinematic Pipeline Control Panel v2
Enhanced UI with Remote + In-Unreal Actions

GREEN buttons = Execute remotely from here
BLUE buttons = Copy script to clipboard → Run in Unreal console
"""

import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import pyperclip
import os

class CinematicControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Cinematic Pipeline Control Panel v2")
        self.root.geometry("900x700")
        
        # Title
        title = tk.Label(root, text="Cinematic Pipeline Control Panel", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        subtitle = tk.Label(root, text="Green = Remote | Blue = Copy for Unreal Console",
                           font=("Arial", 10), fg="gray")
        subtitle.pack()
        
        # Button Frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10, fill="x", padx=20)
        
        # Section 1: Cleanup
        cleanup_label = tk.Label(button_frame, text="CLEANUP", font=("Arial", 12, "bold"))
        cleanup_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        self.btn_delete_actors = tk.Button(button_frame, text="Delete All Actors\n(Remote)", 
                                          bg="#4CAF50", fg="white", width=25, height=3,
                                          command=self.delete_actors_remote)
        self.btn_delete_actors.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_delete_sequences = tk.Button(button_frame, text="Delete All Sequences\n(Copy Script)", 
                                              bg="#2196F3", fg="white", width=25, height=3,
                                              command=self.copy_delete_sequences_script)
        self.btn_delete_sequences.grid(row=1, column=1, padx=5, pady=5)
        
        # Section 2: Creation
        create_label = tk.Label(button_frame, text="CREATION", font=("Arial", 12, "bold"))
        create_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        self.btn_create_sequence = tk.Button(button_frame, text="Create New Sequence\n(Copy Script)", 
                                            bg="#2196F3", fg="white", width=25, height=3,
                                            command=self.copy_create_sequence_script)
        self.btn_create_sequence.grid(row=3, column=0, padx=5, pady=5)
        
        self.btn_spawn_actors = tk.Button(button_frame, text="Spawn 2 Characters\n(Remote)", 
                                         bg="#4CAF50", fg="white", width=25, height=3,
                                         command=self.spawn_actors_remote)
        self.btn_spawn_actors.grid(row=3, column=1, padx=5, pady=5)
        
        # Section 3: Animation
        animate_label = tk.Label(button_frame, text="ANIMATION", font=("Arial", 12, "bold"))
        animate_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.btn_add_animation = tk.Button(button_frame, text="Add Animation Keyframes\n(Remote)", 
                                          bg="#4CAF50", fg="white", width=25, height=3,
                                          command=self.add_animation_remote)
        self.btn_add_animation.grid(row=5, column=0, padx=5, pady=5)
        
        self.btn_play_sequence = tk.Button(button_frame, text="Play in Editor\n(Remote)", 
                                          bg="#4CAF50", fg="white", width=25, height=3,
                                          command=self.play_sequence_remote)
        self.btn_play_sequence.grid(row=5, column=1, padx=5, pady=5)
        
        # Section 4: Render
        render_label = tk.Label(button_frame, text="RENDER", font=("Arial", 12, "bold"))
        render_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        self.btn_render = tk.Button(button_frame, text="Render Video\n(Copy Script)", 
                                   bg="#2196F3", fg="white", width=25, height=3,
                                   command=self.copy_render_script)
        self.btn_render.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
        # Console Output
        console_label = tk.Label(root, text="Console Output:", font=("Arial", 10, "bold"))
        console_label.pack(pady=(10,0))
        
        self.console = scrolledtext.ScrolledText(root, height=15, width=100, 
                                                font=("Consolas", 9))
        self.console.pack(pady=10, padx=20)
        
    def log(self, message, color="black"):
        """Add message to console with color"""
        self.console.insert(tk.END, message + "\n")
        if color != "black":
            start_idx = self.console.index(f"end-{len(message)+1}c")
            end_idx = self.console.index("end-1c")
            self.console.tag_add(color, start_idx, end_idx)
            self.console.tag_config(color, foreground=color)
        self.console.see(tk.END)
        self.console.update()
    
    # ============ REMOTE ACTIONS (GREEN) ============
    
    def delete_actors_remote(self):
        """Delete all actors remotely"""
        self.log("=" * 70, "blue")
        self.log("[REMOTE] Deleting all actors...", "blue")
        
        def run():
            script_path = r"C:\U\CinematicPipeline_Scripts\external_control\remote_delete_actors.py"
            result = subprocess.run(["python", script_path], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    if "[OK]" in line or "Deleted" in line:
                        self.log(line, "green")
                    elif "[X]" in line or "Error" in line:
                        self.log(line, "red")
                    else:
                        self.log(line)
        
        threading.Thread(target=run, daemon=True).start()
    
    def spawn_actors_remote(self):
        """Spawn 2 characters remotely"""
        self.log("=" * 70, "blue")
        self.log("[REMOTE] Spawning 2 characters...", "blue")
        
        def run():
            script_path = r"C:\U\CinematicPipeline_Scripts\external_control\remote_spawn_actors.py"
            result = subprocess.run(["python", script_path], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    if "[OK]" in line:
                        self.log(line, "green")
                    elif "[X]" in line:
                        self.log(line, "red")
                    else:
                        self.log(line)
        
        threading.Thread(target=run, daemon=True).start()
    
    def play_sequence_remote(self):
        """Play sequence in editor remotely"""
        self.log("=" * 70, "blue")
        self.log("[REMOTE] Playing sequence...", "blue")
        
        def run():
            script_path = r"C:\U\CinematicPipeline_Scripts\external_control\remote_camera_fix_and_test.py"
            result = subprocess.run(["python", script_path], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    if "[OK]" in line or "passed" in line.lower():
                        self.log(line, "green")
                    elif "[X]" in line or "failed" in line.lower():
                        self.log(line, "red")
                    else:
                        self.log(line)
        
        threading.Thread(target=run, daemon=True).start()
    
    # ============ IN-UNREAL ACTIONS (BLUE) ============
    
    def copy_delete_sequences_script(self):
        """Copy delete sequences script to clipboard"""
        script = """import unreal
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
editor_asset_lib = unreal.EditorAssetLibrary
filter = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/LevelSequence", "LevelSequence")], package_paths=["/Game"], recursive_paths=True)
assets = asset_registry.get_assets(filter)
deleted = 0
for asset_data in assets:
    package_path = asset_data.package_name
    current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    if current_seq and str(package_path) in current_seq.get_path_name():
        unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
    if editor_asset_lib.delete_asset(str(package_path)):
        print(f"Deleted: {package_path}")
        deleted += 1
print(f"Total deleted: {deleted} sequence(s)")"""
        
        pyperclip.copy(script)
        self.log("=" * 70, "blue")
        self.log("[COPIED] Delete sequences script copied to clipboard!", "green")
        self.log("", "black")
        self.log("Next steps:", "blue")
        self.log("1. Open Unreal Editor", "black")
        self.log("2. Press Ctrl+Shift+X (or Window → Developer Tools → Output Log)", "black")
        self.log("3. Click Python console tab at bottom", "black")
        self.log("4. Paste (Ctrl+V) and press Enter", "black")
    
    def copy_create_sequence_script(self):
        """Copy create sequence script to clipboard"""
        script = """import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.LevelSequenceFactoryNew()
sequence = asset_tools.create_asset("NewSequence", "/Game/Sequences", unreal.LevelSequence, factory)
if sequence:
    sequence.set_display_rate(unreal.FrameRate(30, 1))
    sequence.set_playback_start(0)
    sequence.set_playback_end(300)
    print(f"Created: {sequence.get_path_name()}")
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
else:
    print("Failed to create sequence")"""
        
        pyperclip.copy(script)
        self.log("=" * 70, "blue")
        self.log("[COPIED] Create sequence script copied to clipboard!", "green")
        self.log("", "black")
        self.log("Paste in Unreal Python console (Ctrl+Shift+X)", "blue")
    
    def add_animation_remote(self):
        """Add animation keyframes remotely"""
        self.log("=" * 70, "blue")
        self.log("[REMOTE] Adding animation keyframes...", "blue")
        
        def run():
            script_path = r"C:\U\CinematicPipeline_Scripts\external_control\remote_add_animation_full.py"
            result = subprocess.run(["python", script_path], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    if "[OK]" in line or "Success" in line:
                        self.log(line, "green")
                    elif "[X]" in line or "Error" in line:
                        self.log(line, "red")
                    else:
                        self.log(line)
        
        threading.Thread(target=run, daemon=True).start()
    
    def copy_render_script(self):
        """Copy render script to clipboard"""
        script = """import unreal
sequence_path = "/Game/Sequences/CharacterWalkSequence"
sequence = unreal.load_asset(sequence_path)
if not sequence:
    print("Sequence not found!")
else:
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.sequence = unreal.SoftObjectPath(sequence_path)
    job.map = unreal.SoftObjectPath("/Game/Main")
    config = job.get_configuration()
    output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    output_setting.output_directory = unreal.DirectoryPath("C:/U/Rendered")
    output_setting.file_name_format = "{sequence_name}.{frame_number}"
    image_output = config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    executor = subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
    print("Rendering started...")"""
        
        pyperclip.copy(script)
        self.log("=" * 70, "blue")
        self.log("[COPIED] Render script copied to clipboard!", "green")
        self.log("", "black")
        self.log("Paste in Unreal Python console (Ctrl+Shift+X)", "blue")

def main():
    root = tk.Tk()
    app = CinematicControlPanel(root)
    root.mainloop()

if __name__ == "__main__":
    main()
