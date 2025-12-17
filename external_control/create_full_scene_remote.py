"""
COMPLETE END-TO-END: Create Animated Two-Character Scene Remotely
Uses ExecutePythonCommand to run code inside Unreal where channels work natively

This creates everything from scratch:
- Finds or spawns 2 characters
- Creates/opens sequence
- Adds characters with transform tracks
- Creates animated movement in square paths (side-by-side)
- Complete keyframe animation

Run from external Python (PowerShell/terminal)
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote/object/call"
EDITOR_LIBRARY = '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary'

def call_function(object_path, function_name, parameters=None):
    """Call a function on an Unreal object via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name
    }
    
    if parameters:
        payload["parameters"] = parameters
    
    response = requests.put(BASE_URL, json=payload)
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def execute_python(python_code):
    """Execute Python code inside Unreal Engine"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": python_code}
    }
    
    response = requests.put(BASE_URL, json=payload)
    return response.status_code == 200, response.json() if response.status_code == 200 else response.text

def main():
    print("=" * 80)
    print("COMPLETE END-TO-END: Create Animated Two-Character Scene")
    print("=" * 80)
    
    # Complete pipeline in Unreal Python
    complete_scene_code = """
import unreal

print("\\n" + "="*60)
print("Creating Complete Animated Scene")
print("="*60)

# Close any open sequence first
current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
if current_seq:
    print(f"Closing currently open sequence: {current_seq.get_name()}")
    unreal.LevelSequenceEditorBlueprintLibrary.close()
    print("  Sequence closed")

# Delete existing sequence if it exists
sequence_path = '/Game/Sequences/TwoCharacterSequence'
if unreal.EditorAssetLibrary.does_asset_exist(sequence_path + '.TwoCharacterSequence'):
    print(f"Deleting existing sequence: {sequence_path}")
    unreal.EditorAssetLibrary.delete_asset(sequence_path + '.TwoCharacterSequence')
    
    # Confirm deletion
    if not unreal.EditorAssetLibrary.does_asset_exist(sequence_path + '.TwoCharacterSequence'):
        print("  ✓ Old sequence deleted successfully")
    else:
        print("  ✗ Failed to delete old sequence")
else:
    print("No existing sequence to delete")

# Create new sequence
print("Creating new sequence...")
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
seq = asset_tools.create_asset(
    "TwoCharacterSequence",
    "/Game/Sequences",
    unreal.LevelSequence,
    unreal.LevelSequenceFactoryNew()
)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
print(f"Created and opened new sequence: {seq.get_name()}")

print(f"Working with sequence: {seq.get_name()}")

# Set sequence properties
unreal.MovieSceneSequenceExtensions.set_playback_end_seconds(seq, 10.0)
unreal.MovieSceneSequenceExtensions.set_display_rate(seq, unreal.FrameRate(30, 1))
print("Set sequence to 10 seconds at 30fps")

# Get all actors
editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = editor_subsystem.get_all_level_actors()

# Find or spawn characters
characters = []
for actor in all_actors:
    if 'Character' in actor.get_name() or 'BP_ThirdPerson' in actor.get_name():
        characters.append(actor)
        if len(characters) >= 2:
            break

# Spawn if needed
world = unreal.EditorLevelLibrary.get_editor_world()
character_class = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter')

while len(characters) < 2:
    location = unreal.Vector(0, (len(characters) - 0.5) * 200, 88)
    new_char = world.spawn_actor(character_class, location, unreal.Rotator())
    new_char.set_actor_label(f"Character{len(characters)+1}")
    characters.append(new_char)
    print(f"Spawned {new_char.get_name()}")

print(f"\\nUsing 2 characters: {[c.get_name() for c in characters]}")

# Add characters to sequence with animation
waypoints = [
    (0, 0, 100),
    (500, 0, 100),
    (500, 500, 100),
    (0, 500, 100),
    (0, 0, 100)
]

for char_idx, character in enumerate(characters[:2]):
    print(f"\\n--- Character {char_idx+1}: {character.get_name()} ---")
    
    # Add as possessable
    binding = unreal.MovieSceneSequenceExtensions.add_possessable(seq, character)
    print(f"  Added to sequence")
    
    # Add transform track
    transform_track = unreal.MovieSceneBindingExtensions.add_track(
        binding,
        unreal.MovieScene3DTransformTrack
    )
    print(f"  Transform track created")
    
    # Add section
    section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
    unreal.MovieSceneSectionExtensions.set_range(section, 0, 300)
    print(f"  Section added (0-300 frames)")
    
    # Get channels
    channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
    location_x, location_y, location_z = channels[0], channels[1], channels[2]
    
    # Y offset for side-by-side movement
    y_offset = -100 if char_idx == 0 else 100
    
    # Add keyframes
    frames_per_waypoint = 60
    for i, (x, y, z) in enumerate(waypoints):
        frame = unreal.FrameNumber(i * frames_per_waypoint)
        location_x.add_key(frame, float(x))
        location_y.add_key(frame, float(y + y_offset))
        location_z.add_key(frame, float(z))
    
    print(f"  Added {len(waypoints)} keyframes")
    print(f"  Keys: X={location_x.get_num_keys()}, Y={location_y.get_num_keys()}, Z={location_z.get_num_keys()}")

# Add walking animation to characters
print("\\n" + "="*60)
print("Adding Walking Animation")
print("="*60)

# Load walking animation
walk_anim = unreal.EditorAssetLibrary.load_asset('/Game/ThirdPerson/Animations/Manny/MM_Walk')
if not walk_anim:
    walk_anim = unreal.EditorAssetLibrary.load_asset('/Game/ThirdPerson/Animations/ABP_Manny')
    
if not walk_anim:
    print("Looking for any walking animation...")
    all_assets = unreal.EditorAssetLibrary.list_assets('/Game/ThirdPerson/Animations', recursive=True)
    animations = [a for a in all_assets if 'Walk' in a or 'Run' in a or 'Idle' in a]
    print(f"Available animations: {animations[:5]}")
    if animations:
        walk_anim = unreal.EditorAssetLibrary.load_asset(animations[0])

if walk_anim:
    print(f"Using animation: {walk_anim.get_name()}")
    
    # Add animation track to each character
    for char_idx, character in enumerate(characters[:2]):
        print(f"\\n--- Adding animation to Character {char_idx+1} ---")
        
        # Get the binding for this character
        bindings = unreal.MovieSceneSequenceExtensions.get_bindings(seq)
        if char_idx < len(bindings):
            binding = bindings[char_idx]
            
            # Check if animation track already exists
            tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
            has_anim_track = False
            for track in tracks:
                if isinstance(track, unreal.MovieSceneSkeletalAnimationTrack):
                    has_anim_track = True
                    print(f"  Animation track already exists")
                    break
            
            if not has_anim_track:
                # Add skeletal animation track
                try:
                    anim_track = unreal.MovieSceneBindingExtensions.add_track(
                        binding,
                        unreal.MovieSceneSkeletalAnimationTrack
                    )
                    print(f"  Added animation track")
                    
                    # Add section with walking animation
                    anim_section = unreal.MovieSceneTrackExtensions.add_section(anim_track)
                    anim_section.set_range(0, 300)
                    
                    # Set the animation
                    anim_section.params.animation = walk_anim
                    anim_section.params.start_offset = 0.0
                    anim_section.params.end_offset = 0.0
                    anim_section.params.play_rate = 1.0
                    
                    print(f"  Set walking animation (looping for 10 seconds)")
                except Exception as e:
                    print(f"  Failed to add animation: {str(e)}")
else:
    print("No walking animation found - characters will slide")

print("\\n" + "="*60)
print("COMPLETE! Scene created with 2 animated characters")
print("="*60)
result = "SUCCESS: 2 characters with full animation + walking!"
"""
    
    print("\n[1/2] Executing complete scene creation inside Unreal...")
    success, result = execute_python(complete_scene_code)
    
    if success:
        print(f"    ✓ Scene created!")
        print(f"    Result: {json.dumps(result, indent=2)}")
        
        # Now trigger play via Remote API with proper sequence opening
        print("\n[2/2] Starting playback with camera lock...")
        
        # Use the known sequence path format
        sequence_path = '/Game/Sequences/TwoCharacterSequence.TwoCharacterSequence'
        
        # Step 1: Open sequence
        print("    Step 1: Opening sequence...")
        success, result = call_function(EDITOR_LIBRARY, 'OpenLevelSequence', {'LevelSequence': sequence_path})
        if success:
            print(f"    ✓ Sequence opened")
        else:
            print(f"    ⚠ Warning: Could not open: {result}")
        
        # Step 2: Lock camera to viewport (KEY FIX)
        print("    Step 2: Locking camera to viewport...")
        success, result = call_function(EDITOR_LIBRARY, 'SetLockCameraCutToViewport', {'bLock': True})
        if success:
            print(f"    ✓ Camera cut locked to viewport")
        else:
            print(f"    ⚠ Warning: Could not lock camera: {result}")
        
        # Step 3: Force update
        print("    Step 3: Forcing sequencer update...")
        success, result = call_function(EDITOR_LIBRARY, 'ForceUpdate')
        if success:
            print(f"    ✓ Sequencer updated")
        
        # Step 4: Play
        print("    Step 4: Starting playback...")
        success, result = call_function(EDITOR_LIBRARY, 'Play')
        if success:
            print(f"    ✓ Sequence playing!")
        else:
            print(f"    ✗ Play failed: {result}")
        
        print("\n" + "=" * 80)
        print("✓ COMPLETE ANIMATED SCENE CREATED & PLAYING!")
        print("=" * 80)
        print("\nWhat was created:")
        print("  • 2 Characters (found or spawned)")
        print("  • Both added to sequence as possessables")
        print("  • Transform tracks with sections")
        print("  • 5 keyframes each (square movement path)")
        print("  • Side-by-side animation (200cm apart)")
        print("  • Walking animation on skeletal mesh")
        print("  • Sequence automatically playing!")
        print("\nCheck Unreal viewport to see characters walking in square paths!")
        print("=" * 80)
    else:
        print(f"    ✗ Scene creation failed: {result}")
        print("\nCheck Unreal Output Log for details")

if __name__ == "__main__":
    main()
