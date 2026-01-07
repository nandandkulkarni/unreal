"""
Diagnostic script to check what actors exist in the scene
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\diagnose_scene.log"

class FileLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = FileLogger(LOG_FILE_PATH)

print("=" * 80)
print("SCENE DIAGNOSTIC")
print("=" * 80)

all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

print(f"\nTotal actors in scene: {len(all_actors)}")

# Find PCG-related actors
pcg_actors = []
stadium_actors = []

for actor in all_actors:
    label = actor.get_actor_label()
    class_name = actor.get_class().get_name()
    
    if "PCG" in label or "PCG" in class_name:
        pcg_actors.append((label, class_name))
    
    if "Stadium" in label:
        stadium_actors.append((label, class_name))

print(f"\nPCG-related actors ({len(pcg_actors)}):")
for label, cls in pcg_actors:
    print(f"  - {label} ({cls})")

print(f"\nStadium actors ({len(stadium_actors)}):")
for label, cls in stadium_actors:
    print(f"  - {label} ({cls})")

# Check for PCG assets
print("\nChecking PCG assets...")
if unreal.EditorAssetLibrary.does_asset_exist("/Game/PCG"):
    assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG")
    print(f"Assets in /Game/PCG: {len(assets)}")
    for asset_path in assets:
        print(f"  - {asset_path}")
else:
    print("  /Game/PCG directory doesn't exist")
