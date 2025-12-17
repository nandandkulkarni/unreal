"""
Step 2: Test if OpenLevelSequence works on the existing TestSequence
Run this AFTER creating the sequence in Unreal
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

def test_open_existing_sequence():
    """Test opening an existing sequence"""
    
    print("=" * 80)
    print("TEST: OpenLevelSequence on EXISTING sequence")
    print("=" * 80)
    
    sequence_path = "/Game/Sequences/TestSequence"
    
    print(f"\n[1] Attempting to open: {sequence_path}")
    print("    (Make sure you created it in Unreal first!)\n")
    
    # Try to open it
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": {"objectPath": sequence_path}}
    )
    
    print(f">>> OpenLevelSequence API response:")
    print(f"    Success: {success}")
    print(f"    Result: {json.dumps(result, indent=4)}")
    
    open_result = result.get('ReturnValue', None)
    print(f"\n>>> ReturnValue: {open_result}")
    
    # Check if it's now current
    print(f"\n[2] Checking GetCurrentLevelSequence...")
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    
    current_seq = current.get('ReturnValue', '')
    print(f">>> Current sequence: '{current_seq}'")
    
    # Try focused sequence too
    print(f"\n[3] Checking GetFocusedLevelSequence...")
    success, focused = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetFocusedLevelSequence"
    )
    
    focused_seq = focused.get('ReturnValue', '')
    print(f">>> Focused sequence: '{focused_seq}'")
    
    print("\n" + "=" * 80)
    print("ANALYSIS:")
    print("=" * 80)
    
    if open_result == True:
        print("✓ OpenLevelSequence returned True")
    elif open_result == False:
        print("✗ OpenLevelSequence returned False (sequence might not exist)")
    else:
        print(f"? OpenLevelSequence returned: {open_result}")
    
    if current_seq:
        print(f"✓ Sequence IS open in editor: {current_seq}")
        print("\n>>> CONCLUSION: OpenLevelSequence WORKS!")
    else:
        print("✗ No sequence open in editor")
        print("\n>>> CONCLUSION: OpenLevelSequence FAILED or sequence doesn't exist")
    
    print("=" * 80)

if __name__ == "__main__":
    test_open_existing_sequence()
