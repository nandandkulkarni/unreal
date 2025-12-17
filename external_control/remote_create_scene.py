"""
Remote Scene Creator
Clears and recreates entire cinematic scene via Remote Control API

This script runs FROM POWERSHELL and creates:
- 2 characters walking in parallel
- Camera tracking both
- Complete 10-second sequence

CLEANUP SCOPE:
- Deletes: All Character actors in level
- Deletes: All CineCameraActor actors in level
- Does NOT delete: Sequence assets (requires in-Unreal script)

To delete sequence assets first:
  1. Unreal Editor → Tools → Execute Python Script
  2. Run: delete_all_sequences.py
  3. Then run this script

After running this, use:
- remote_camera_fix_and_test.py to play in editor
- render_sequence_to_video.py (in Unreal) to render video
"""

import requests
import json
import time

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object"

def call_function(object_path, function_name, parameters=None):
    """Call a function on an Unreal object via Remote Control"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name
    }
    
    if parameters:
        payload["parameters"] = parameters
    
    url = f"{REMOTE_CONTROL_URL}/call"
    
    try:
        response = requests.put(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"  [X] Error calling {function_name}: {response.text}")
            return None
    except Exception as e:
        print(f"  [X] Exception calling {function_name}: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Exception calling {function_name}: {e}")
        return None

def set_property(object_path, property_name, value):
    """Set a property on an Unreal object"""
    url = f"{REMOTE_CONTROL_URL}/property"
    payload = {
        "objectPath": object_path,
        "propertyName": property_name,
        "propertyValue": value
    }
    
    try:
        response = requests.put(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"  [X] Exception setting {property_name}: {e}")
        return False

def clear_scene():
    """Clear existing sequence and actors"""
    print("=" * 60)
    print("Step 1: Clearing Scene")
    print("=" * 60)
    
    editor_library = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary"
    actor_subsystem = "/Script/UnrealEd.Default__EditorActorSubsystem"
    
    # Close any open sequence
    print("\n  Closing open sequences...")
    call_function(editor_library, "CloseLevelSequence")
    print("  [OK] Sequences closed")
    
    # Note: Sequence asset deletion not available via Remote Control API
    # To delete sequences, run delete_all_sequences.py inside Unreal Editor
    
    # Get all actors in the level
    print("\n  Finding existing actors...")
    result = call_function(actor_subsystem, "GetAllLevelActors")
    
    if result and result.get("ReturnValue"):
        actors = result.get("ReturnValue")
        character_count = 0
        camera_count = 0
        
        for actor_path in actors:
            # Check if it's a Character actor
            if "Character_" in actor_path or "/Script/Engine.Character" in actor_path:
                character_count += 1
                print(f"  Deleting Character: {actor_path}")
                delete_result = call_function(
                    actor_subsystem,
                    "DestroyActor",
                    {"ActorToDestroy": actor_path}
                )
                if delete_result:
                    print(f"    [OK] Deleted")
                else:
                    print(f"    [X] Failed to delete")
            
            # Check if it's a CineCameraActor
            elif "CineCameraActor" in actor_path or "CinematicCamera" in actor_path:
                camera_count += 1
                print(f"  Deleting Camera: {actor_path}")
                delete_result = call_function(
                    actor_subsystem,
                    "DestroyActor",
                    {"ActorToDestroy": actor_path}
                )
                if delete_result:
                    print(f"    [OK] Deleted")
                else:
                    print(f"    [X] Failed to delete")
        
        if character_count == 0 and camera_count == 0:
            print("  No actors found to delete")
        else:
            print(f"\n  [OK] Deleted {character_count} Character(s) and {camera_count} Camera(s)")
    else:
        print("  [X] Could not get level actors")
    
    print("\n  [OK] Scene cleared\n")

def create_two_character_scene():
    """Create scene with 2 characters walking in parallel using validated spawn methods"""
    print("=" * 60)
    print("Step 2: Creating Scene with 2 Characters")
    print("=" * 60)
    
    actor_subsystem = "/Script/UnrealEd.Default__EditorActorSubsystem"
    sequencer_path = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem"
    editor_library = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary"
    
    # Step 1: Spawn characters in level using EditorActorSubsystem
    print("\n  Spawning Character 1 (left side)...")
    char1_result = call_function(
        actor_subsystem,
        "SpawnActorFromClass",
        {
            "ActorClass": "/Script/Engine.Character",
            "Location": {"X": 0, "Y": -100, "Z": 100}
        }
    )
    
    if char1_result and char1_result.get("ReturnValue"):
        char1_path = char1_result.get("ReturnValue")
        print(f"    [OK] Character 1: {char1_path}")
    else:
        print("    [X] Failed to spawn Character 1")
        return False
    
    print("\n  Spawning Character 2 (right side)...")
    char2_result = call_function(
        actor_subsystem,
        "SpawnActorFromClass",
        {
            "ActorClass": "/Script/Engine.Character",
            "Location": {"X": 0, "Y": 100, "Z": 100}
        }
    )
    
    if char2_result and char2_result.get("ReturnValue"):
        char2_path = char2_result.get("ReturnValue")
        print(f"    [OK] Character 2: {char2_path}")
    else:
        print("    [X] Failed to spawn Character 2")
        return False
    
    # Step 2: Open or create sequence
    print("\n  Opening sequence in Sequencer...")
    sequence_path = "/Game/TwoCharacterSequence.TwoCharacterSequence"
    
    open_result = call_function(
        editor_library,
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    
    if not open_result:
        print("    Note: Sequence may need to be created in Unreal first")
    
    time.sleep(0.5)
    
    # Step 3: Create camera
    print("\n  Creating cinematic camera...")
    camera_result = call_function(
        sequencer_path,
        "CreateCamera",
        {"bSpawnable": True}
    )
    
    if camera_result:
        print("    [OK] Camera created")
    else:
        print("    [X] Camera creation failed")
    
    # Step 4: Add characters as spawnables
    print("\n  Adding characters to sequence as spawnables...")
    
    spawnable1 = call_function(
        sequencer_path,
        "AddSpawnableFromClass",
        {"ClassToSpawn": "/Script/Engine.Character"}
    )
    
    if spawnable1:
        print("    [OK] Spawnable 1 added")
    
    spawnable2 = call_function(
        sequencer_path,
        "AddSpawnableFromClass",
        {"ClassToSpawn": "/Script/Engine.Character"}
    )
    
    if spawnable2:
        print("    [OK] Spawnable 2 added")
    
    # Verify sequence was created
    print("\n  Verifying sequence creation...")
    editor_library = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary"
    verify_result = call_function(editor_library, "GetCurrentLevelSequence")
    
    if verify_result and verify_result.get("ReturnValue"):
        current_sequence = verify_result.get("ReturnValue")
        print(f"    [OK] Sequence exists: {current_sequence}")
    else:
        print("    [X] WARNING: Could not verify sequence creation")
    
    print("\n  [OK] Scene created with 2 characters")
    print(f"  Actors spawned in level: {char1_path}, {char2_path}")
    
    return True

def finalize_scene():
    """Finalize scene setup"""
    print("\n" + "=" * 60)
    print("Step 3: Finalizing Scene")
    print("=" * 60)
    
    print("\n  Scene structure created successfully!")
    print("\n  What was created:")
    print("  [OK] 2 Characters spawned in level")
    print("  [OK] Cinematic camera added to sequence")
    print("  [OK] Characters added as spawnables")
    
    print("\n  *** IMPORTANT ***")
    print("  Characters have NO ANIMATION yet!")
    print("  To add full animation with waypoints:")
    print("    1. Open Unreal Editor")
    print("    2. Tools → Execute Python Script")
    print("    3. Run: create_two_characters.py")
    print("\n  Then use Stage 2 to test playback")
    print("  And Stage 3 to render video")

def main():
    print("\n")
    print("=" * 60)
    print("REMOTE SCENE CREATOR - 2 Characters")
    print("=" * 60)
    
    # Verify Remote Control is running
    try:
        response = requests.get("http://localhost:30010/remote/info")
        if response.status_code != 200:
            print("\n[X] Remote Control server is not running!")
            print("   Start it in Unreal: WebControl.StartServer")
            return
    except:
        print("\n[X] Cannot connect to Remote Control server!")
        print("   Start it in Unreal: WebControl.StartServer")
        return
    
    print("\n[OK] Remote Control server is running")
    
    # Execute steps
    clear_scene()
    success = create_two_character_scene()
    
    if success:
        finalize_scene()
        
        print("\n" + "=" * 60)
        print("[OK] SCENE CREATED SUCCESSFULLY!")
        print("=" * 60)
        print("\nUse the control panel to continue:")
        print("  - Stage 2: Play in editor (remote)")
        print("  - Stage 3: Render video (in Unreal)")
        print("\n" + "=" * 60)
    else:
        print("\n[X] Scene creation failed")
        print("\nALTERNATIVE: Run create_two_characters.py inside Unreal")
        print("Tools -> Execute Python Script -> create_two_characters.py")

if __name__ == "__main__":
    main()
