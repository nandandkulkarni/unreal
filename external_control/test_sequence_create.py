"""
Test Sequence Creation via Remote Control API
Simple script to test if we can create a Level Sequence remotely
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
        print(f"\n  Response Status: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"  [X] Error calling {function_name}")
            return None
    except Exception as e:
        print(f"  [X] Exception: {e}")
        return None

def test_sequence_creation():
    """Test creating a new Level Sequence"""
    print("=" * 60)
    print("TESTING SEQUENCE CREATION")
    print("=" * 60)
    
    sequencer_subsystem = "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem"
    asset_tools = "/Script/UnrealEd.Default__EditorAssetLibrary"
    
    # Test 1: Try to create a new Level Sequence asset
    print("\n[TEST 1] Creating new Level Sequence asset...")
    sequence_path = "/Game/TestSequence"
    
    # Try CreateNewLevelSequence
    print("\n  Attempting: CreateNewLevelSequence")
    result = call_function(
        sequencer_subsystem,
        "CreateNewLevelSequence",
        {
            "NewLevelSequenceName": "TestSequence",
            "bSaveAfterCreation": False
        }
    )
    
    if result:
        print(f"  [OK] Result: {result}")
    
    # Test 2: Try to create using AssetTools
    print("\n\n[TEST 2] Trying via EditorAssetLibrary...")
    result2 = call_function(
        asset_tools,
        "MakeDirectory",
        {"DirectoryPath": "/Game/Sequences"}
    )
    print(f"  Make Directory result: {result2}")
    
    # Test 3: List available functions
    print("\n\n[TEST 3] Getting available functions...")
    print("  On LevelSequenceEditorSubsystem:")
    test_call = {
        "objectPath": sequencer_subsystem,
        "functionName": "NonExistentFunction"
    }
    response = requests.put(f"{REMOTE_CONTROL_URL}/call", json=test_call)
    print(f"  Response: {response.text[:200]}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_sequence_creation()
