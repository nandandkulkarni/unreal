"""
Check if sequences exist and OpenLevelSequence behavior
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote"

def call_function(object_path, function_name, parameters=None):
    """Call Unreal function via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name,
        "parameters": parameters or {}
    }
    
    response = requests.put(f"{BASE_URL}/object/call", json=payload)
    
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def check_sequences():
    """Check if sequences exist and can be opened"""
    
    print("=" * 80)
    print("SEQUENCE EXISTENCE CHECK")
    print("=" * 80)
    
    # Test paths where sequences might exist
    sequence_paths = [
        "/Game/Sequences/CharacterWalkSequence",
        "/Game/TwoCharacterSequence",
        "/Game/Sequences/TwoCharacterSequence",
        "/Game/CharacterWalkSequence"
    ]
    
    print("\n[TEST 1] Checking what sequences currently exist...")
    print("(We'll test by trying to open each path)\n")
    
    for seq_path in sequence_paths:
        print(f"\n--- Testing: {seq_path} ---")
        
        # Try to open it
        success, result = call_function(
            "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
            "OpenLevelSequence",
            {"LevelSequence": {"objectPath": seq_path}}
        )
        
        open_result = result.get('ReturnValue', None)
        print(f"  OpenLevelSequence result: {open_result}")
        
        # Check if it's now current
        success, current = call_function(
            "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
            "GetCurrentLevelSequence"
        )
        
        current_seq = current.get('ReturnValue', '')
        print(f"  GetCurrentLevelSequence: '{current_seq}'")
        
        if current_seq:
            print(f"  ✓ SUCCESS! Sequence opened: {current_seq}")
            
            # Get more info about this sequence
            success, bindings = call_function(
                "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
                "GetBindings",
                {"Sequence": {"objectPath": seq_path}}
            )
            bindings_list = bindings.get('ReturnValue', []) if success else []
            
            success, possessables = call_function(
                "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
                "GetPossessables",
                {"Sequence": {"objectPath": seq_path}}
            )
            possessables_list = possessables.get('ReturnValue', []) if success else []
            
            print(f"  → Bindings: {len(bindings_list)}")
            print(f"  → Possessables: {len(possessables_list)}")
            
            if possessables_list:
                print(f"  → Possessables data: {possessables_list}")
            
            # Close it for next test
            call_function(
                "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
                "CloseLevelSequence"
            )
        else:
            print(f"  ✗ Not found or failed to open")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Sequences that successfully opened will be listed above.")
    print("If none opened, sequences may need to be created first.")
    print("=" * 80)

if __name__ == "__main__":
    check_sequences()
