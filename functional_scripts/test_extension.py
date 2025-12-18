"""
Quick Test - Execute this with Ctrl+Enter to test the Unreal Python extension!

Make sure Unreal Engine is running with WebControl.StartServer enabled.
"""
import unreal

# Simple test: Print Unreal Engine version
print("=" * 60)
print("Testing Unreal Python Extension")
print("=" * 60)

# Get editor subsystem
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
print("Editor Subsystem:", editor_subsystem)

# Count actors in the level
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = actor_subsystem.get_all_level_actors()
print(f"Total actors in level: {len(all_actors)}")

# List first 5 actors
print("\nFirst 5 actors:")
for i, actor in enumerate(all_actors[:5], 1):
    print(f"  {i}. {actor.get_actor_label()} - {actor.get_class().get_name()}")

print("=" * 60)
print("✓ Extension test successful!")
print("=" * 60)

# TIP: You can select just a few lines and press Ctrl+Enter to execute only that part!
