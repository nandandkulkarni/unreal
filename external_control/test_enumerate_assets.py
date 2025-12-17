"""
Test Directory/Asset Enumeration via Remote Control API
Try different methods to list assets in /Game/Sequences
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
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Result: {json.dumps(result, indent=2)[:500]}")
            return result
        else:
            print(f"  Error: {response.text[:200]}")
        return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None

def test_enumeration():
    """Test various methods to enumerate assets"""
    print("=" * 60)
    print("TESTING ASSET ENUMERATION METHODS")
    print("=" * 60)
    
    # Test 1: EditorAssetLibrary.ListAssets (probably won't work)
    print("\n[TEST 1] EditorAssetLibrary.ListAssets")
    call_function(
        "/Script/UnrealEd.Default__EditorAssetLibrary",
        "ListAssets",
        {"DirectoryPath": "/Game/Sequences"}
    )
    
    # Test 2: EditorAssetLibrary.DoesDirectoryExist
    print("\n[TEST 2] EditorAssetLibrary.DoesDirectoryExist")
    call_function(
        "/Script/UnrealEd.Default__EditorAssetLibrary",
        "DoesDirectoryExist",
        {"DirectoryPath": "/Game/Sequences"}
    )
    
    # Test 3: Try getting directory info from level
    print("\n[TEST 3] Level.GetAllActors (for comparison)")
    call_function(
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "GetAllLevelActors"
    )
    
    # Test 4: Check if there's an asset registry access
    print("\n[TEST 4] AssetRegistryHelpers (if accessible)")
    call_function(
        "/Script/AssetRegistry.Default__AssetRegistryHelpers",
        "GetAssetRegistry"
    )
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_enumeration()
