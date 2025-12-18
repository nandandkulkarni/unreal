"""
Create a Mannequin Character in Unreal Engine

This script deletes all mannequins starting with "TestMannequin" and creates a new one.
Run from PowerShell - it will execute the code inside Unreal Engine.

Usage:
    python create_mannequin.py
"""

from unreal_connection import UnrealRemote


def create_mannequin(mannequin_name="TestMannequin1", location=(0, 0, 88)):
    """
    Create a new Mannequin character in Unreal
    
    Args:
        mannequin_name: Name for the mannequin
        location: (X, Y, Z) position tuple
    """
    
    # Python code to execute inside Unreal
    code = f"""
import unreal

print("=" * 60)
print("Creating Mannequin: {mannequin_name}")
print("=" * 60)

# Delete all mannequins starting with "TestMannequin"
print("\\nCleaning up old test mannequins...")
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = editor_actor_subsystem.get_all_level_actors()
deleted_count = 0

for actor in all_actors:
    actor_label = actor.get_actor_label()
    if actor_label.startswith("TestMannequin"):
        print(f"  Deleting: {{actor_label}}")
        unreal.EditorLevelLibrary.destroy_actor(actor)
        deleted_count += 1

if deleted_count > 0:
    print(f"✓ Deleted {{deleted_count}} old test mannequin(s)")
else:
    print("  No old test mannequins found")

# Create new mannequin
print("\\nCreating new Mannequin character...")

# Load the ThirdPerson Character blueprint
character_class = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter')

if not character_class:
    print("✗ Failed to load BP_ThirdPersonCharacter blueprint")
    print("  Make sure you have the ThirdPerson template content in your project")
else:
    # Spawn character using EditorLevelLibrary
    spawn_location = unreal.Vector({location[0]}, {location[1]}, {location[2]})
    spawn_rotation = unreal.Rotator(0, 0, 0)
    
    character = unreal.EditorLevelLibrary.spawn_actor_from_class(
        character_class,
        spawn_location,
        spawn_rotation
    )
    
    if not character:
        print("✗ Failed to spawn character actor")
    else:
        # Set the character name
        character.set_actor_label("{mannequin_name}")
        
        print(f"✓ Mannequin created: {{character.get_actor_label()}}")
        print(f"  Location: {{spawn_location}}")
        print(f"  Class: {{character.get_class().get_name()}}")
        
        # Get skeletal mesh component info
        components = character.get_components_by_class(unreal.SkeletalMeshComponent)
        if len(components) > 0:
            mesh_comp = components[0]
            skeletal_mesh = mesh_comp.get_skeletal_mesh_asset()
            if skeletal_mesh:
                print(f"  Skeletal Mesh: {{skeletal_mesh.get_name()}}")
        
        print("=" * 60)
        print("✓ Mannequin creation complete!")
        print(f"  Name: {{character.get_actor_label()}}")
        print(f"  Path: {{character.get_path_name()}}")
        print("=" * 60)
        
        # Verify by querying the world
        print("\\nVerifying creation...")
        editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors_after = editor_actor_subsystem.get_all_level_actors()
        found = False
        for actor in all_actors_after:
            if actor.get_actor_label() == "{mannequin_name}":
                found = True
                print(f"✓ Verified: Found '{{actor.get_actor_label()}}' in world")
                print(f"  Actor type: {{actor.get_class().get_name()}}")
                print(f"  Location: {{actor.get_actor_location()}}")
                break
        
        if not found:
            print(f"✗ ERROR: Could not find '{{character.get_actor_label()}}' in world query!")
            print(f"  Expected name: {mannequin_name}")
            print(f"  Total actors in world: {{len(all_actors_after)}}")
"""
    
    # Connect to Unreal and execute
    unreal = UnrealRemote()
    
    if not unreal.is_connected():
        print("✗ Cannot connect to Unreal Engine!")
        print("Make sure Unreal is running and WebControl.StartServer has been executed.")
        return False
    
    print(f"Creating mannequin '{mannequin_name}' at {location}...")
    success, result = unreal.execute_python(code)
    
    if success:
        print("\\n✓ Mannequin created successfully!")
        print("Check Unreal Engine's viewport and outliner.")
        return True
    else:
        print(f"\\n✗ Failed to create mannequin: {result}")
        return False


def main():
    """Main entry point"""
    import sys
    
    # Get mannequin name from command line or use default
    mannequin_name = sys.argv[1] if len(sys.argv) > 1 else "TestMannequin1"
    
    # Parse location if provided
    if len(sys.argv) >= 4:
        location = (float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
    else:
        location = (0, 0, 88)  # Default: at origin, 88cm above ground (character capsule height)
    
    create_mannequin(mannequin_name, location)


if __name__ == "__main__":
    main()
