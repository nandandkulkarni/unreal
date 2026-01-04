"""
Character Height Measurement Tool via Remote Control

Usage:
    python measure_character.py [CharacterName|AssetPath]
    
    Examples:
        python measure_character.py Belica
        python measure_character.py /Game/MyChar/SK_MyChar
"""

import requests
import sys
import os
import json

# Add motion_includes to path if possible (optional, just for cleaner imports if needed)
sys.path.append(os.path.dirname(__file__))
try:
    from motion_includes.assets import Characters
except ImportError:
    Characters = None

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

HEADER = """
import unreal
import sys

def measure_character(path):
    actor = None
    try:
        # Check if asset exists
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            return f"ERROR: Asset not found: {path}"
            
        # Spawn logic
        # 1. Try generic actor load
        # 2. Try Blueprint load
        
        # Determine if BP
        is_blueprint = False
        spawn_class = None
        
        if "BP_" in path or "_C" in path:
            is_blueprint = True
            c_path = path
            if not c_path.endswith("_C"):
                c_path += "_C"
            spawn_class = unreal.load_class(None, c_path)
        else:
            # Assume SkeletalMesh, create SkeletalMeshActor
            spawn_class = unreal.SkeletalMeshActor
        
        if not spawn_class:
             return f"ERROR: Could not load class for {path}"
             
        # Spawn at 0,0,0
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(spawn_class, unreal.Vector(0,0,10000)) # Far up/away
        
        if not actor:
             return f"ERROR: Failed to spawn actor for {path}"
             
        # Attempt to set mesh if SkeletalMeshActor
        if not is_blueprint and isinstance(actor, unreal.SkeletalMeshActor):
            mesh = unreal.load_asset(path)
            if mesh:
                 actor.skeletal_mesh_component.set_skeletal_mesh_asset(mesh)
        
        # MEASURE
        # 1. Try Capsule
        capsule = actor.get_component_by_class(unreal.CapsuleComponent)
        height = 0.0
        source = "None"
        
        if capsule:
            height = capsule.get_scaled_capsule_half_height() * 2
            source = "Capsule"
        else:
            # 2. Try Mesh Bounds
            # Use Actor Bounds (Origin, BoxExtent)
            # get_actor_bounds(bOnlyCollidingComponents, bIncludeFromChildActors)
            # Returns tuple (origin_vector, box_extent_vector)
            result = actor.get_actor_bounds(False, False)
            if result and len(result) == 2:
                origin, extent = result
                height = extent.z * 2
                source = "ActorBounds"
            else:
                height = 0.0
                source = "Unknown"
                
        # Clean up
        unreal.EditorLevelLibrary.destroy_actor(actor)
        
        return f"Height: {height:.2f} cm (Source: {source})"
        
    except Exception as e:
        if actor:
            unreal.EditorLevelLibrary.destroy_actor(actor)
        return f"EXCEPTION: {e}"

"""

def run_measurement(char_input):
    # Resolve path
    path = char_input
    if Characters:
        path = Characters.get_path(char_input)
    
    print(f"Measuring Character: {char_input}")
    print(f"Asset Path: {path}")
    
    full_command = HEADER + f"\nresult = measure_character(r'{path}')\nprint(result)"
    
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": full_command}
    }
    
    try:
        response = requests.put(REMOTE_CONTROL_URL, json=payload, timeout=30)
        
        # Parse output? 
        # The return value of ExecutePythonCommand is boolean.
        # But printed output shows up in Output Log. 
        # We can't easily capture stdout via Remote Control without a custom wrapper that returns it.
        # Workaround: Raising an error with the message? Or just assume user looks at log? 
        # User requested: "spit out the height".
        # If I can't return string, I should probably write to a temp file or just log it.
        # Actually Unreal Python Remote Control usually returns the result if the python code returns a value?
        # No, ExecutePythonCommand returns bool.
        
        # Better approach: Use "ExecutePythonCommandEx" or similar if available? No.
        # Standard hack: Write to a file, read the file.
        
        # Let's modify the script to write to a file in this dir.
        temp_file = os.path.abspath("measurement_result.txt").replace("\\", "/")
        full_command = HEADER + f"\nresult = measure_character(r'{path}')\nwith open(r'{temp_file}', 'w') as f: f.write(str(result))"
        payload["parameters"]["PythonCommand"] = full_command
        
        requests.put(REMOTE_CONTROL_URL, json=payload, timeout=30)
        
        # Read file
        if os.path.exists("measurement_result.txt"):
            with open("measurement_result.txt", "r") as f:
                print(f.read())
            os.remove("measurement_result.txt")
        else:
            print("No result file generated. Check Unreal Output Log.")

    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Interactive mode
        print("Available Characters in Assets:")
        if Characters:
            for k, v in vars(Characters).items():
                if k.isupper():
                    print(f"  - {k}")
        
        val = input("\nEnter character name or path: ")
        if val:
            run_measurement(val)
    else:
        run_measurement(sys.argv[1])
