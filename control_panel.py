"""
Cinematic Pipeline Control Panel
Simple UI for the 3-stage workflow

Stage 1: Create Scene (in Unreal)
Stage 2: Play in Editor (remote)
Stage 3: Render Video (in Unreal)
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import threading

class CinematicControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Cinematic Pipeline Control Panel")
        self.root.geometry("800x600")
        
        # Title
        title = tk.Label(root, text="Unreal Cinematic Pipeline", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Subtitle
        subtitle = tk.Label(root, text="Two Character Scene Workflow (Stage 1: REMOTE!)", font=("Arial", 10))
        subtitle.pack()
        
        # Button Frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        
        # Stage 1: Create Scene
        btn1 = tk.Button(
            button_frame, 
            text="Stage 1: Create Scene\n(Remote API)", 
            command=self.create_scene,
            width=20,
            height=3,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold")
        )
        btn1.grid(row=0, column=0, padx=10)
        
        # Stage 2: Play in Editor
        btn2 = tk.Button(
            button_frame, 
            text="Stage 2: Play in Editor\n(Remote Control)", 
            command=self.play_in_editor,
            width=20,
            height=3,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold")
        )
        btn2.grid(row=0, column=1, padx=10)
        
        # Stage 3: Render Video
        btn3 = tk.Button(
            button_frame, 
            text="Stage 3: Render Video\n(Run in Unreal)", 
            command=self.render_video,
            width=20,
            height=3,
            bg="#FF9800",
            fg="white",
            font=("Arial", 11, "bold")
        )
        btn3.grid(row=0, column=2, padx=10)
        
        # Status label
        self.status_label = tk.Label(root, text="Ready", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Output console
        console_label = tk.Label(root, text="Output Console:", font=("Arial", 10, "bold"))
        console_label.pack()
        
        self.console = scrolledtext.ScrolledText(root, width=90, height=20, font=("Consolas", 9))
        self.console.pack(padx=10, pady=5)
        
        # Configure text tags for colors
        self.console.tag_config("error", foreground="red", font=("Consolas", 9, "bold"))
        self.console.tag_config("success", foreground="green", font=("Consolas", 9, "bold"))
        self.console.tag_config("warning", foreground="orange", font=("Consolas", 9))
        self.console.tag_config("info", foreground="blue", font=("Consolas", 9))
        
        # Script paths
        self.scripts_dir = "C:/U/CinematicPipeline_Scripts"
        self.external_dir = os.path.join(self.scripts_dir, "external_control")
        
        self.log("Cinematic Pipeline Control Panel Ready")
        self.log("=" * 70)
    
    def log(self, message, tag=None):
        """Add message to console with optional color tag"""
        # Auto-detect error/success patterns
        if tag is None:
            if "[X]" in message or "Error" in message or "error" in message or "failed" in message:
                tag = "error"
            elif "[OK]" in message or "Success" in message or "success" in message or "✓" in message:
                tag = "success"
            elif "WARNING" in message or "Warning" in message:
                tag = "warning"
            elif "STAGE" in message or "Step" in message:
                tag = "info"
        
        if tag:
            self.console.insert(tk.END, message + "\n", tag)
        else:
            self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.root.update()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update()
    
    def create_scene(self):
        """Stage 1: Create scene with 2 characters REMOTELY"""
        self.log("\n" + "=" * 70)
        self.log("STAGE 1: CREATE SCENE (Remote)", "info")
        self.log("=" * 70)
        
        self.update_status("Creating scene remotely...")
        
        def run():
            script_path = os.path.join(self.external_dir, "remote_create_scene.py")
            
            self.log("\nCreating scene via Remote Control API...")
            self.log("This will:")
            self.log("  - Spawn 2 characters in the level")
            self.log("  - Create camera for sequence")
            self.log("  - Add spawnables to sequence")
            self.log("  - Set up basic animation")
            self.log("")
            
            try:
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    cwd=self.external_dir
                )
                
                # Log output line by line for proper color coding
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log(line)
                
                if result.stderr:
                    self.log("ERRORS:", "error")
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            self.log(line, "error")
                
                if result.returncode == 0:
                    self.update_status("[OK] Scene created remotely!")
                    self.log("\n[OK] Scene created successfully!", "success")
                    self.log("\nNext: Use Stage 2 to play the sequence", "info")
                else:
                    self.update_status("[X] Scene creation failed")
                    self.log("\n[X] Scene creation failed.", "error")
                    self.log("\nFallback: Run create_two_characters.py in Unreal Editor", "warning")
            except Exception as e:
                self.log(f"Error: {e}", "error")
                self.update_status("[X] Scene creation error")
        
        threading.Thread(target=run, daemon=True).start()
    
    def play_in_editor(self):
        """Stage 2: Play sequence in editor remotely"""
        self.log("\n" + "=" * 70)
        self.log("STAGE 2: PLAY IN EDITOR (Remote)")
        self.log("=" * 70)
        
        self.log("\nIMPORTANT: For animated playback, run create_two_characters.py in Unreal first!", "warning")
        self.log("(Stage 1 creates structure, but animation needs full script)", "warning")
        self.log("")
        
        self.update_status("Playing sequence remotely...")
        
        def run():
            script_path = os.path.join(self.external_dir, "remote_camera_fix_and_test.py")
            
            self.log("\nRunning remote playback test...")
            self.log("This will:")
            self.log("  - Open TwoCharacterSequence")
            self.log("  - Lock camera to viewport")
            self.log("  - Play the sequence")
            self.log("  - Verify playback")
            self.log("")
            
            try:
                # Update the script to use TwoCharacterSequence
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    cwd=self.external_dir
                )
                
                # Log output line by line for proper color coding
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log(line)
                
                if result.stderr:
                    self.log("ERRORS:", "error")
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            self.log(line, "error")
                
                if result.returncode == 0:
                    self.update_status("✓ Playback successful")
                    self.log("\n✓ Sequence played successfully!", "success")
                else:
                    self.update_status("✗ Playback failed")
                    self.log("\n✗ Playback failed. Check Remote Control server is running.", "error")
            except Exception as e:
                self.log(f"Error: {e}", "error")
                self.update_status("✗ Playback error")
        
        threading.Thread(target=run, daemon=True).start()
    
    def render_video(self):
        """Stage 3: Render video"""
        self.log("\n" + "=" * 70)
        self.log("STAGE 3: RENDER VIDEO")
        self.log("=" * 70)
        
        script_path = os.path.join(self.scripts_dir, "render_two_characters.py")
        
        self.log("\nTo render the video:")
        self.log("1. Open Unreal Editor")
        self.log("2. Go to: Tools → Execute Python Script")
        self.log(f"3. Select: {script_path}")
        self.log("4. Click Execute")
        self.log("5. Wait for render preview window to complete")
        self.log("\nOutput will be saved to:")
        self.log("  C:\\U\\CinematicPipeline\\Saved\\VideoCaptures")
        self.log("  TwoCharacters_TwoCharacterSequence.mov")
        self.log("\nFormat: Apple ProRes, 1920x1080, 30fps")
        self.log("Size: ~300-400MB for 10 seconds")
        
        messagebox.showinfo(
            "Render Video",
            "Please run render_two_characters.py in Unreal Editor:\n\n"
            "Tools → Execute Python Script → render_two_characters.py\n\n"
            "Wait for render preview window to complete.\n"
            "Video will be saved to Saved/VideoCaptures/"
        )
        
        self.update_status("Waiting for manual render in Unreal")

def main():
    root = tk.Tk()
    app = CinematicControlPanel(root)
    root.mainloop()

if __name__ == "__main__":
    main()
