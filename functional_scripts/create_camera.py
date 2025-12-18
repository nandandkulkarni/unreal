"""
Create a Cine Camera Actor in Unreal Engine

This script deletes all cameras starting with "TestCamera" and creates a new one.
Run from PowerShell - it will execute the code inside Unreal Engine.

Usage:
    python create_camera.py
"""

from unreal_connection import UnrealRemote


def create_camera(camera_name="TestCamera1", location=(0, -500, 200)):
    """
    Create a new Cine Camera Actor in Unreal
    
    Args:
        camera_name: Name for the camera
        location: (X, Y, Z) position tuple
    """
    
    # Python code to execute inside Unreal
    code = f"""
import unreal

print("=" * 60)
print("Creating Cine Camera: {camera_name}")
print("=" * 60)

# Delete all cameras starting with "TestCamera"
print("\\nCleaning up old test cameras...")
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
deleted_count = 0

for actor in all_actors:
    if isinstance(actor, unreal.CineCameraActor):
        actor_name = actor.get_actor_label()
        if actor_name.startswith("TestCamera"):
            print(f"  Deleting: {{actor_name}}")
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted_count += 1

if deleted_count > 0:
    print(f"✓ Deleted {{deleted_count}} old test camera(s)")
else:
    print("  No old test cameras found")

# Create new camera
print("\\nCreating new Cine Camera Actor...")
camera_location = unreal.Vector({location[0]}, {location[1]}, {location[2]})
camera_rotation = unreal.Rotator(0, 0, 0)

camera_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.CineCameraActor,
    camera_location,
    camera_rotation
)

if not camera_actor:
    print("✗ Failed to spawn camera actor")
else:
    # Set the camera name
    camera_actor.set_actor_label("{camera_name}")
    
    print(f"✓ Camera created: {{camera_actor.get_actor_label()}}")
    print(f"  Location: {{camera_location}}")
    print(f"  Class: {{camera_actor.get_class().get_name()}}")
    
    # Get camera component and log some properties
    camera_component = camera_actor.get_cine_camera_component()
    if camera_component:
        print(f"  Focal Length: {{camera_component.current_focal_length}}mm")
        print(f"  Aperture: f/{{camera_component.current_aperture}}")
    
    print("=" * 60)
    print("✓ Camera creation complete!")
    print(f"  Name: {{camera_actor.get_actor_label()}}")
    print(f"  Path: {{camera_actor.get_path_name()}}")
    print("=" * 60)
"""
    
    # Connect to Unreal and execute
    unreal = UnrealRemote()
    
    if not unreal.is_connected():
        print("✗ Cannot connect to Unreal Engine!")
        print("Make sure Unreal is running and WebControl.StartServer has been executed.")
        return False
    
    print(f"Creating camera '{camera_name}' at {location}...")
    success, result = unreal.execute_python(code)
    
    if success:
        print("\\n✓ Camera created successfully!")
        print("Check Unreal Engine's viewport and outliner.")
        return True
    else:
        print(f"\\n✗ Failed to create camera: {result}")
        return False


def main():
    """Main entry point"""
    import sys
    
    # Get camera name from command line or use default
    camera_name = sys.argv[1] if len(sys.argv) > 1 else "TestCamera1"
    
    # Parse location if provided
    if len(sys.argv) >= 4:
        location = (float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
    else:
        location = (0, -500, 200)  # Default: behind and above origin
    
    create_camera(camera_name, location)


if __name__ == "__main__":
    main()
