"""
Deep Research: AddPossessable via Remote Control API
Investigating why binding is added but count stays 0
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
    
    print(f"\n>>> CALL: {function_name}")
    print(f"    Payload: {json.dumps(parameters, indent=8)}")
    print(f"    Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"    Result: {json.dumps(result, indent=8)}")
        return True, result
    else:
        print(f"    Error: {response.text}")
        return False, response.text

def deep_research_add_possessable():
    """Deep dive into AddPossessable behavior"""
    
    print("=" * 80)
    print("DEEP RESEARCH: AddPossessable")
    print("=" * 80)
    
    sequence_path = "/Game/Sequences/CharacterWalkSequence"
    
    # Step 1: Open sequence and verify
    print("\n[STEP 1] Open sequence")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": {"objectPath": sequence_path}}
    )
    
    # Step 2: Get current sequence (should return the sequence object)
    print("\n[STEP 2] Get current sequence object")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    current_sequence = result.get('ReturnValue', '')
    print(f"\n>>> Current sequence path: '{current_sequence}'")
    
    # Step 3: Get bindings BEFORE adding (using sequence object path)
    print("\n[STEP 3] Get bindings BEFORE adding (using objectPath)")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetBindings",
        {"Sequence": {"objectPath": sequence_path}}
    )
    bindings_before = result.get('ReturnValue', []) if success else []
    print(f"\n>>> Bindings count BEFORE: {len(bindings_before)}")
    print(f">>> Bindings data: {bindings_before}")
    
    # Step 4: Get a character actor
    print("\n[STEP 4] Get character actor")
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
    
    print(f"\n>>> Character found: {character}")
    
    if not character:
        print("\n[ERROR] No character found!")
        return
    
    # Step 5: Try AddPossessable with different parameter formats
    print("\n[STEP 5a] AddPossessable - Format 1: objectPath in nested dict")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "AddPossessable",
        {
            "Sequence": {"objectPath": sequence_path},
            "ObjectToAdd": {"objectPath": character}
        }
    )
    binding1 = result.get('ReturnValue', {}) if success else {}
    print(f"\n>>> Binding returned: {binding1}")
    
    # Step 5b: Try different parameter format
    print("\n[STEP 5b] AddPossessable - Format 2: direct paths")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "AddPossessable",
        {
            "Sequence": sequence_path,
            "ObjectToAdd": character
        }
    )
    binding2 = result.get('ReturnValue', {}) if success else {}
    print(f"\n>>> Binding returned: {binding2}")
    
    # Step 6: Get bindings AFTER adding
    print("\n[STEP 6a] Get bindings AFTER (using objectPath)")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetBindings",
        {"Sequence": {"objectPath": sequence_path}}
    )
    bindings_after_1 = result.get('ReturnValue', []) if success else []
    print(f"\n>>> Bindings count AFTER: {len(bindings_after_1)}")
    print(f">>> Bindings data: {bindings_after_1}")
    
    # Step 6b: Try GetBindings with different format
    print("\n[STEP 6b] Get bindings AFTER (direct path)")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetBindings",
        {"Sequence": sequence_path}
    )
    bindings_after_2 = result.get('ReturnValue', []) if success else []
    print(f"\n>>> Bindings count AFTER: {len(bindings_after_2)}")
    
    # Step 7: Try to use the returned binding
    print("\n[STEP 7] Try to use returned binding to get its name")
    if binding1:
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "GetName",
            {"InBinding": binding1}
        )
        name = result.get('ReturnValue', '') if success else ''
        print(f"\n>>> Binding name: '{name}'")
    
    # Step 8: Try GetPossessables
    print("\n[STEP 8] Get possessables from sequence")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetPossessables",
        {"Sequence": {"objectPath": sequence_path}}
    )
    possessables = result.get('ReturnValue', []) if success else []
    print(f"\n>>> Possessables count: {len(possessables)}")
    print(f">>> Possessables data: {possessables}")
    
    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print("Check if:")
    print("1. Binding ID is all zeros = invalid/null binding")
    print("2. GetBindings needs specific sequence object reference")
    print("3. AddPossessable works but returns proxy that doesn't persist")
    print("4. Need to call SaveLoadedAsset after adding")
    print("=" * 80)

if __name__ == "__main__":
    deep_research_add_possessable()
