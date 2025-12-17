"""
Deep Research: AddPossessable via Remote Control API
Testing with CORRECT sequence path format
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
        result = response.json()
        return True, result
    else:
        return False, response.text

def test_add_possessable():
    """Test AddPossessable with correct sequence path"""
    
    print("=" * 80)
    print("DEEP RESEARCH: AddPossessable with CORRECT path format")
    print("=" * 80)
    
    # Use CORRECT format with .AssetName
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    # Step 1: Open sequence
    print("\n[1] Opening sequence with correct path...")
    print(f"    Path: {sequence_path}")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    
    open_result = result.get('ReturnValue', None)
    print(f"    OpenLevelSequence returned: {open_result}")
    
    # Verify it's open
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    current_seq = current.get('ReturnValue', '')
    print(f"    Current sequence: '{current_seq}'")
    
    if not current_seq:
        print("\n[ERROR] Sequence not open! Cannot proceed.")
        return
    
    # Step 2: Get bindings BEFORE adding
    print("\n[2] Get bindings BEFORE adding...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetBindings",
        {"Sequence": sequence_path}
    )
    bindings_before = result.get('ReturnValue', []) if success else []
    print(f"    Bindings count BEFORE: {len(bindings_before)}")
    
    # Step 3: Get a character actor
    print("\n[3] Getting character actor...")
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
    
    if not character:
        print("    [ERROR] No character found!")
        return
    
    print(f"    Character: {character}")
    
    # Step 4: AddPossessable
    print("\n[4] Adding possessable...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "AddPossessable",
        {
            "Sequence": sequence_path,
            "ObjectToAdd": character
        }
    )
    
    binding = result.get('ReturnValue', {}) if success else {}
    print(f"    Success: {success}")
    print(f"    Binding returned: {json.dumps(binding, indent=4)}")
    
    binding_id = binding.get('BindingID', {})
    print(f"    Binding ID: A={binding_id.get('A')}, B={binding_id.get('B')}, C={binding_id.get('C')}, D={binding_id.get('D')}")
    
    # Step 5: Get bindings AFTER adding
    print("\n[5] Get bindings AFTER adding...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetBindings",
        {"Sequence": sequence_path}
    )
    bindings_after = result.get('ReturnValue', []) if success else []
    print(f"    Bindings count AFTER: {len(bindings_after)}")
    
    if len(bindings_after) > len(bindings_before):
        print(f"    ✓ Binding was added! (+{len(bindings_after) - len(bindings_before)})")
    else:
        print(f"    ✗ No change in binding count")
    
    # Step 6: Try GetPossessables
    print("\n[6] Get possessables...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetPossessables",
        {"Sequence": sequence_path}
    )
    possessables = result.get('ReturnValue', []) if success else []
    print(f"    Possessables count: {len(possessables)}")
    
    if possessables:
        print(f"    ✓ Found possessables!")
        for i, poss in enumerate(possessables):
            print(f"      [{i}] {poss}")
    
    # Step 7: Try to use the binding
    if binding:
        print("\n[7] Testing if binding is valid...")
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "GetName",
            {"InBinding": binding}
        )
        name = result.get('ReturnValue', '') if success else ''
        print(f"    Binding name: '{name}'")
        
        if name:
            print(f"    ✓ Binding IS valid! Name: {name}")
        else:
            print(f"    ✗ Binding returned empty name (invalid)")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    if len(bindings_after) > len(bindings_before) or len(possessables) > 0:
        print("✓ AddPossessable WORKS! Binding was successfully added.")
    else:
        print("✗ AddPossessable returns success but binding not persisted.")
        print("  Possible cause: Remote Control API limitation")
    print("=" * 80)

if __name__ == "__main__":
    test_add_possessable()
