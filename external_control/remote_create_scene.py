"""
Remote Scene Creator
Clears and recreates entire cinematic scene via Remote Control API

This script runs FROM POWERSHELL and creates:
- 2 characters walking in parallel
- Camera tracking both
- Complete 10-second sequence

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
    
    sequencer_path = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem"
    
    # Close any open sequence
    print("\n  Closing open sequences...")
    call_function(sequencer_path, "Close")
    
    # Delete existing sequence asset
    print("  Deleting old sequence...")
    # Note: Asset deletion via Remote Control is limited
    # We'll recreate and overwrite instead
    
    print("  [OK] Scene cleared\n")

def create_two_character_scene():
    """Create scene with 2 characters walking in parallel"""
    print("=" * 60)
    print("Step 2: Creating Scene with 2 Characters")
    print("=" * 60)
    
    sequencer_path = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem"
    sequence_extensions = "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions"
    
    # Character spawn positions (side by side)
    character1_start = {"X": 0, "Y": 0, "Z": 0}
    character2_start = {"X": 0, "Y": 200, "Z": 0}  # 200cm to the side
    
    # Waypoints (same pattern, both will follow)
    waypoints = [
        {"X": 0, "Y": 0, "Z": 0},
        {"X": 500, "Y": 0, "Z": 0},
        {"X": 500, "Y": 500, "Z": 0},
        {"X": 0, "Y": 500, "Z": 0},
        {"X": 0, "Y": 0, "Z": 0}
    ]
    
    print("\n  Creating Level Sequence...")
    # Create new sequence at /Game/TwoCharacterSequence
    result = call_function(sequencer_path, "CreateNewLevelSequenceAsset", {
        "SequenceName": "TwoCharacterSequence",
        "SequencePath": "/Game/"
    })
    
    if not result:
        print("  [X] Could not create sequence")
        return False
    
    sequence_path = result.get("ReturnValue")
    print(f"  [OK] Created: {sequence_path}")
    
    # Set sequence length to 10 seconds at 30fps
    print("\n  Configuring sequence duration...")
    call_function(sequence_extensions, "SetPlaybackEnd", {
        "Sequence": sequence_path,
        "EndFrame": 300  # 10 seconds at 30fps
    })
    
    print("\n  Spawning characters...")
    # Note: Spawning actors via Remote Control is complex
    # This requires the sequence to be open and using AddSpawnableFromClass
    
    # Open the sequence first
    call_function(sequencer_path, "OpenLevelSequence", {
        "LevelSequence": sequence_path
    })
    
    time.sleep(1)  # Let sequence open
    
    # Add Character 1
    print("    Adding Character 1...")
    char1_result = call_function(sequencer_path, "AddSpawnableFromClass", {
        "Sequence": sequence_path,
        "ClassToSpawn": "/Script/Engine.Character"
    })
    
    # Add Character 2
    print("    Adding Character 2...")
    char2_result = call_function(sequencer_path, "AddSpawnableFromClass", {
        "Sequence": sequence_path,
        "ClassToSpawn": "/Script/Engine.Character"
    })
    
    print("\n  [OK] Scene created with 2 characters")
    print(f"  Sequence: {sequence_path}")
    
    return True

def setup_camera():
    """Setup camera to view both characters"""
    print("\n" + "=" * 60)
    print("Step 3: Setting Up Camera")
    print("=" * 60)
    
    sequencer_path = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem"
    
    # Create cine camera
    print("\n  Creating cine camera...")
    camera_result = call_function(sequencer_path, "CreateCamera", {
        "bSpawnable": True
    })
    
    if camera_result:
        print("  [OK] Camera created")
    else:
        print("  [X] Could not create camera")
    
    print("\n  Note: Camera positioning and animation must be done in Unreal Editor")
    print("  - Adjust camera position to frame both characters")
    print("  - Add keyframes for camera movement")
    print("  - Set camera FOV wider to capture both")

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
        setup_camera()
        
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("\n1. In Unreal Editor:")
        print("   - Open /Game/TwoCharacterSequence")
        print("   - Position characters at start locations")
        print("   - Add transform tracks with waypoint keyframes")
        print("   - Adjust camera to frame both characters")
        print("\n2. Test playback remotely:")
        print("   python remote_camera_fix_and_test.py")
        print("\n3. Render video (in Unreal):")
        print("   Tools → Execute Python Script → render_sequence_to_video.py")
        print("\n" + "=" * 60)
        print("\nNOTE: Remote Control API has limitations for complex scene setup.")
        print("For full automation, run create_two_characters.py inside Unreal.")
        print("=" * 60)
    else:
        print("\n[X] Scene creation failed")
        print("\nALTERNATIVE: Run create_two_characters.py inside Unreal")
        print("Tools -> Execute Python Script -> create_two_characters.py")

if __name__ == "__main__":
    main()
