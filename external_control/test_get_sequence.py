"""
Simple test: Open sequence and get current sequence
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

def test_get_sequence():
    """Test getting sequence"""
    
    print("=" * 80)
    print("TEST: Get Current Sequence")
    print("=" * 80)
    
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    # Step 1: Open sequence
    print("\n[1] Opening sequence...")
    print(f"    Path: {sequence_path}")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    
    if not success:
        print(f"    [ERROR] Failed to open: {result}")
        return
    
    open_result = result.get('ReturnValue', None)
    print(f"    ✓ OpenLevelSequence returned: {open_result}")
    
    # Step 2: Get the OPEN sequence object
    print("\n[2] Getting currently open sequence...")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    
    if not success:
        print(f"    [ERROR] Failed to get current: {result}")
        return
    
    current_seq = result.get('ReturnValue', '')
    print(f"    ✓ Current sequence: '{current_seq}'")
    
    if not current_seq:
        print("\n[ERROR] No sequence open!")
        return
    
    print("\n" + "=" * 80)
    print("✓ SUCCESS - Sequence logic is working!")
    print(f"✓ Sequence reference: {current_seq}")
    print("=" * 80)

if __name__ == "__main__":
    test_get_sequence()
