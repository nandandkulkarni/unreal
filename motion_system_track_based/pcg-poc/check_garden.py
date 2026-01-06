import unreal
import sys
import os
import datetime

# Logging Setup
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\check_garden.log"

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

def check_garden_state():
    print(f"[{datetime.datetime.now()}] Checking Garden Actors...")
    world = unreal.EditorLevelLibrary.get_editor_world()
    all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    
    garden_actors = [a for a in all_actors if "Garden" in a.get_actor_label()]
    
    print(f"Found {len(garden_actors)} actors with 'Garden' in label.")
    
    if len(garden_actors) == 0:
        print("✗ No Garden actors found!")
        return
        
    print("\nSample Actors:")
    for i, actor in enumerate(garden_actors[:5]):
        print(f"  [{i}] {actor.get_actor_label()}")
        print(f"      Location: {actor.get_actor_location()}")
        print(f"      Hidden: {actor.is_hidden_ed()}")
        if isinstance(actor, unreal.StaticMeshActor):
            mesh = actor.static_mesh_component.static_mesh
            print(f"      Mesh: {mesh.get_name() if mesh else 'None'}")
            print(f"      Scale: {actor.get_actor_scale3d()}")

    # Force Viewport Update
    unreal.EditorLevelLibrary.editor_invalidate_viewports()
    print("\n✓ Viewports invalidated (forced refresh)")

if __name__ == "__main__":
    check_garden_state()
