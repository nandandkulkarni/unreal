import json
import os

DIST_DIR = r"c:\UnrealProjects\coding\unreal\motion_system\dist"
JSON_FILE = os.path.join(DIST_DIR, "sprint_with_camera.json") # Use the main plan file, or pass 1 if needed. 
# Actually, the user asked about "pass 1" data initially, but let's check the FINAL plan first.
# Wait, the final plan is a list of commands. Pass 1 is the calculated state.
# Let's check Pass 1 file first.
PASS1_FILE = os.path.join(DIST_DIR, "Sprint With Camera_1_base_command_processing.json")

def inspect_animations(file_path):
    print(f"--- Inspecting {os.path.basename(file_path)} ---")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    # Structure check
    actors = data.get("actors", {})
    if not actors: 
        print("No actors found.")
        return

    for actor_name, actor_data in actors.items():
        print(f"\nActor: {actor_name}")
        anims = actor_data.get("keyframes", {}).get("animations", [])
        if not anims:
            print("  No animations.")
            continue
        
        for i, anim in enumerate(anims):
            name = anim.get("name", "Unknown")
            start = anim.get("start_frame")
            end = anim.get("end_frame")
            print(f"  Anim {i+1}: '{name}' | Start: {start} -> End: {end}")

if __name__ == "__main__":
    inspect_animations(PASS1_FILE)
