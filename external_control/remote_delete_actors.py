"""
Remote Delete All Actors
Deletes all Character and Camera actors from the level
"""

import requests
import json

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
            return response.json()
        return None
    except:
        return None

def delete_all_actors():
    """Delete all Character and Camera actors"""
    print("=" * 60)
    print("DELETING ALL ACTORS (REMOTE)")
    print("=" * 60)
    
    actor_subsystem = "/Script/UnrealEd.Default__EditorActorSubsystem"
    editor_library = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary"
    
    # Close sequences first
    print("\nClosing open sequences...")
    call_function(editor_library, "CloseLevelSequence")
    print("[OK] Sequences closed")
    
    # Get all actors
    print("\nFinding actors...")
    result = call_function(actor_subsystem, "GetAllLevelActors")
    
    if not result or not result.get("ReturnValue"):
        print("[X] Could not get level actors")
        return
    
    actors = result.get("ReturnValue")
    character_count = 0
    camera_count = 0
    
    for actor_path in actors:
        # Delete Characters
        if "Character_" in actor_path or "/Script/Engine.Character" in actor_path:
            character_count += 1
            print(f"Deleting Character: {actor_path}")
            delete_result = call_function(
                actor_subsystem,
                "DestroyActor",
                {"ActorToDestroy": actor_path}
            )
            if delete_result:
                print("  [OK] Deleted")
            else:
                print("  [X] Failed")
        
        # Delete Cameras
        elif "CineCameraActor" in actor_path or "CinematicCamera" in actor_path:
            camera_count += 1
            print(f"Deleting Camera: {actor_path}")
            delete_result = call_function(
                actor_subsystem,
                "DestroyActor",
                {"ActorToDestroy": actor_path}
            )
            if delete_result:
                print("  [OK] Deleted")
            else:
                print("  [X] Failed")
    
    print(f"\n{'=' * 60}")
    if character_count == 0 and camera_count == 0:
        print("No actors found to delete")
    else:
        print(f"[OK] Deleted {character_count} Character(s) and {camera_count} Camera(s)")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    delete_all_actors()
