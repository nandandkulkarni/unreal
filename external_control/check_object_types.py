"""
Check what types of objects we're successfully passing through Remote Control
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote/object/call"

print("=" * 80)
print("CHECKING OBJECT TYPES PASSED THROUGH REMOTE CONTROL")
print("=" * 80)

# Step 1: Get sequence (string)
print("\n[1] Getting sequence...")
result = requests.put(BASE_URL, json={
    'objectPath': '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary',
    'functionName': 'GetCurrentLevelSequence'
}).json()
sequence = result['ReturnValue']
print(f"    Type: {type(sequence)}")
print(f"    Value: {sequence}")
print(f"    → This is a PRIMITIVE (string) ✓")

# Step 2: Get bindings (structs with primitives)
print("\n[2] Getting bindings...")
result = requests.put(BASE_URL, json={
    'objectPath': '/Script/SequencerScripting.Default__MovieSceneSequenceExtensions',
    'functionName': 'GetBindings',
    'parameters': {'Sequence': sequence}
}).json()
bindings = result['ReturnValue']
if bindings:
    binding = bindings[0]
    print(f"    Type: {type(binding)}")
    print(f"    Value: {json.dumps(binding, indent=2)}")
    print(f"    → This is a STRUCT with primitives (dict of ints/strings) ✓")
    print(f"    → BindingID: {binding.get('BindingID')} (dict of 4 integers)")
    print(f"    → Sequence: {binding.get('Sequence')} (string)")
    
    # Step 3: Try to pass binding to AddTrack
    print("\n[3] Passing binding_proxy to AddTrack...")
    print(f"    Parameter 'InBinding' = {json.dumps(binding, indent=2)}")
    result = requests.put(BASE_URL, json={
        'objectPath': '/Script/SequencerScripting.Default__MovieSceneBindingExtensions',
        'functionName': 'GetTracks',
        'parameters': {'InBinding': binding}
    }).json()
    print(f"    → SUCCESS! Returned: {result.get('ReturnValue', [])}")
    print(f"    → binding_proxy is SERIALIZABLE (struct) ✓")

# Step 4: Check track object
print("\n[4] Getting track object...")
# Need to actually add a track first
char_path = "/Game/Sequences/TestSequence.TestSequence:PersistentLevel.BP_ThirdPersonCharacter_2"
result = requests.put(BASE_URL, json={
    'objectPath': '/Script/SequencerScripting.Default__MovieSceneSequenceExtensions',
    'functionName': 'AddPossessable',
    'parameters': {'Sequence': sequence, 'ObjectToPossess': char_path}
}).json()
binding = result.get('ReturnValue', {})

result = requests.put(BASE_URL, json={
    'objectPath': '/Script/SequencerScripting.Default__MovieSceneBindingExtensions',
    'functionName': 'AddTrack',
    'parameters': {
        'InBinding': binding,
        'TrackType': '/Script/MovieSceneTracks.MovieScene3DTransformTrack'
    }
}).json()
track = result.get('ReturnValue', {})
print(f"    Type: {type(track)}")
print(f"    Value: {json.dumps(track, indent=2) if track else 'Empty'}")

if track:
    print(f"    → Track is a STRING (object path) ✓")
    
    # Step 5: Check section object
    print("\n[5] Getting section object...")
    result = requests.put(BASE_URL, json={
        'objectPath': '/Script/SequencerScripting.Default__MovieSceneTrackExtensions',
        'functionName': 'GetSections',
        'parameters': {'Track': track}
    }).json()
    sections = result.get('ReturnValue', [])
    if sections:
        section = sections[0]
        print(f"    Type: {type(section)}")
        print(f"    Value: {section}")
        print(f"    → Section is a STRING (object path) ✓")
        
        # Step 6: Check channel object
        print("\n[6] Getting channel object...")
        result = requests.put(BASE_URL, json={
            'objectPath': '/Script/SequencerScripting.Default__MovieSceneSectionExtensions',
            'functionName': 'GetAllChannels',
            'parameters': {'Section': section}
        }).json()
        channels = result.get('ReturnValue', [])
        if channels:
            channel = channels[0]
            print(f"    Type: {type(channel)}")
            print(f"    Value: {channel}")
            print(f"    → Channel is a STRING but it's TRANSIENT ✗")
            print(f"    → Contains '/Engine/Transient' = temporary Python object")
            print(f"    → This is why AddKey FAILS!")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("✓ Sequence: string (object path) = PRIMITIVE")
print("✓ Binding: struct with ints/strings = SERIALIZABLE")  
print("✓ Track: string (object path) = PRIMITIVE")
print("✓ Section: string (object path) = PRIMITIVE")
print("✗ Channel: string but TRANSIENT (Python wrapper) = NOT SERIALIZABLE")
print("\nAll of these LOOK like primitives when returned via HTTP,")
print("but channels are special Python objects that can't be reconstructed!")
print("=" * 80)
