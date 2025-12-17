"""
Test OpenLevelSequence with CORRECT path format
Format: /Game/Sequences/TestSequence.TestSequence (note the .TestSequence at end)
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

def test_correct_path_format():
    """Test with correct Unreal asset path format"""
    
    print("=" * 80)
    print("TEST: OpenLevelSequence with CORRECT path format")
    print("=" * 80)
    
    # CORRECT format includes .AssetName at the end
    correct_path = "/Game/Sequences/TestSequence.TestSequence"
    wrong_path = "/Game/Sequences/TestSequence"
    
    print(f"\n[TEST 1] Wrong format (missing .AssetName):")
    print(f"  Path: {wrong_path}")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": wrong_path}
    )
    print(f"  Result: {result.get('ReturnValue', None)}")
    
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    print(f"  Current sequence: '{current.get('ReturnValue', '')}'")
    
    print(f"\n[TEST 2] CORRECT format (with .AssetName):")
    print(f"  Path: {correct_path}")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": correct_path}
    )
    print(f"  Result: {result.get('ReturnValue', None)}")
    
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    current_seq = current.get('ReturnValue', '')
    print(f"  Current sequence: '{current_seq}'")
    
    print("\n" + "=" * 80)
    if current_seq:
        print("✓ SUCCESS! OpenLevelSequence works with correct path format!")
        print(f"✓ Opened: {current_seq}")
    else:
        print("✗ FAILED even with correct format")
    print("=" * 80)

if __name__ == "__main__":
    test_correct_path_format()
