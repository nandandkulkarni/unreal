"""
Find Existing Sequences via Remote Control API
Tests common sequence paths to see which ones exist
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

def find_sequences():
    """Try to find existing sequences by attempting to open them"""
    print("=" * 60)
    print("SEARCHING FOR EXISTING SEQUENCES")
    print("=" * 60)
    
    editor_library = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary"
    
    # Common sequence paths to check
    test_paths = [
        "/Game/Sequences/CharacterWalkSequence.CharacterWalkSequence",
        "/Game/CharacterWalkSequence.CharacterWalkSequence",
        "/Game/TwoCharacterSequence.TwoCharacterSequence",
        "/Game/TestSequence.TestSequence",
        "/Game/MasterSequence.MasterSequence",
        "/Game/CinematicSequence.CinematicSequence",
        "/Game/MainSequence.MainSequence",
        "/Game/Sequences/MainSequence.MainSequence",
    ]
    
    print(f"\nTesting {len(test_paths)} common paths...\n")
    
    found_sequences = []
    
    for seq_path in test_paths:
        # Try to open the sequence
        result = call_function(
            editor_library,
            "OpenLevelSequence",
            {"LevelSequence": seq_path}
        )
        
        if result:
            # Check if sequence is now open
            verify = call_function(editor_library, "GetCurrentLevelSequence")
            if verify and verify.get("ReturnValue"):
                current_path = verify.get("ReturnValue")
                if seq_path in str(current_path):
                    print(f"  [FOUND] {seq_path}")
                    found_sequences.append(seq_path)
                    # Close it for next test
                    call_function(editor_library, "CloseLevelSequence")
    
    print(f"\n{'=' * 60}")
    if found_sequences:
        print(f"FOUND {len(found_sequences)} SEQUENCE(S):")
        for seq in found_sequences:
            print(f"  - {seq}")
    else:
        print("NO SEQUENCES FOUND")
        print("Sequences must be created inside Unreal Editor first.")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    find_sequences()
