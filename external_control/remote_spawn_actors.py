"""
Remote Spawn Actors
Spawns 2 characters in the level
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

def spawn_actors():
    """Spawn 2 characters"""
    print("=" * 60)
    print("SPAWNING 2 CHARACTERS (REMOTE)")
    print("=" * 60)
    
    actor_subsystem = "/Script/UnrealEd.Default__EditorActorSubsystem"
    
    # Spawn Character 1
    print("\nSpawning Character 1 (left side)...")
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
        print(f"[OK] Character 1: {char1_path}")
    else:
        print("[X] Failed to spawn Character 1")
        return
    
    # Spawn Character 2
    print("\nSpawning Character 2 (right side)...")
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
        print(f"[OK] Character 2: {char2_path}")
    else:
        print("[X] Failed to spawn Character 2")
        return
    
    print(f"\n{'=' * 60}")
    print("[OK] 2 Characters spawned successfully")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    spawn_actors()
