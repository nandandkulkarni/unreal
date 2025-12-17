"""
Test AssetRegistry Access via Remote Control API
Exploring if asset registry functions are accessible
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
            result = response.json()
            print(f"  [OK] Status: {response.status_code}")
            print(f"  Result: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"  [X] Status: {response.status_code}")
            print(f"  Error: {response.text}")
        return None
    except Exception as e:
        print(f"  [X] Exception: {e}")
        return None

def test_asset_registry():
    """Test asset registry access"""
    print("=" * 60)
    print("TESTING ASSET REGISTRY ACCESS")
    print("=" * 60)
    
    # Note: GetAssetRegistry returned empty, so it might not give us a usable object
    # But let's try different approaches
    
    # Try MovieSceneSequenceExtensions which has asset-related functions
    print("\n[TEST 1] MovieSceneSequenceExtensions.FindBindingByName")
    print("(This works on open sequences, testing if accessible)")
    sequencer = "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions"
    result = call_function(sequencer, "GetBindings", {"Sequence": None})
    
    print("\n[TEST 2] Can we access any asset through object path?")
    # Try to directly access a sequence asset
    seq_path = "/Game/Sequences/CharacterWalkSequence.CharacterWalkSequence"
    result = call_function(seq_path, "GetDisplayRate")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_asset_registry()
