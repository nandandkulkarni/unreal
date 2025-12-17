"""
Test AddPossessable using currently OPEN sequence
Instead of passing sequence path, use the sequence that's already open
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

def test_with_open_sequence():
    """Test using the currently open sequence"""
    
    print("=" * 80)
    print("TEST: AddPossessable using OPEN sequence")
    print("=" * 80)
    
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    # Step 1: Open sequence
    print("\n[1] Opening sequence...")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    print(f"    Opened: {result.get('ReturnValue')}")
    
    # Step 2: Get the OPEN sequence object
    print("\n[2] Getting currently open sequence...")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    current_seq = result.get('ReturnValue', '')
    print(f"    Current sequence: '{current_seq}'")
    
    if not current_seq:
        print("    [ERROR] No sequence open!")
        return
    
    # Step 3: Get character
    print("\n[3] Getting character...")
    success, result = call_function(
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "GetAllLevelActors"
    )
    all_actors = result.get('ReturnValue', [])
    character = None
    for actor in all_actors:
        if 'Character' in str(actor):
            character = actor
            break
    print(f"    Character: {character}")
    
    # Step 4: Try AddPossessable with NO Sequence parameter (use open one)
    # print("\n[4] AddPossessable with EMPTY Sequence parameter...")
    # print("    (Maybe it uses the currently open sequence?)")
    # success, result = call_function(
    #     "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
    #     "AddPossessable",
    #     {
    #         "Sequence": "",
    #         "ObjectToPossess": character
    #     }
    # )
    # binding1 = result.get('ReturnValue', {}) if success else {}
    # print(f"    Result: {binding1}")
    
    # Step 5: Try with current_seq path
    print("\n[5] AddPossessable using GetCurrentLevelSequence result...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "AddPossessable",
        {
            "Sequence": current_seq,
            "ObjectToPossess": character
        }
    )
    binding2 = result.get('ReturnValue', {}) if success else {}
    print(f"    Result: {binding2}")
    
    # Step 6: Try loading the sequence asset first
    print("\n[6] Try loading sequence with EditorAssetLibrary...")
    success, result = call_function(
        "/Script/UnrealEd.Default__EditorAssetLibrary",
        "LoadAsset",
        {"AssetPath": sequence_path}
    )
    loaded_asset = result.get('ReturnValue', '') if success else ''
    print(f"    Loaded asset: '{loaded_asset}'")
    
    if loaded_asset:
        print("\n[7] AddPossessable with loaded asset...")
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
            "AddPossessable",
            {
                "Sequence": loaded_asset,
                "ObjectToPossess": character
            }
        )
        binding3 = result.get('ReturnValue', {}) if success else {}
        print(f"    Result: {binding3}")
    
    print("\n" + "=" * 80)
    print("Check Unreal log for deserialization errors")
    print("=" * 80)

if __name__ == "__main__":
    test_with_open_sequence()
