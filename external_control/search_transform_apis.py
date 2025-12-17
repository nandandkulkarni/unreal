"""
Search for higher-level keyframe/transform APIs on section/track
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote"

def describe_object(object_path):
    """Get all functions available on an object"""
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": object_path}
    )
    return response.json() if response.status_code == 200 else {}

def setup():
    """Get a section object"""
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    # Open sequence
    requests.put(f"{BASE_URL}/object/call", json={
        "objectPath": "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "functionName": "OpenLevelSequence",
        "parameters": {"LevelSequence": sequence_path}
    })
    
    # Get current
    r = requests.put(f"{BASE_URL}/object/call", json={
        "objectPath": "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "functionName": "GetCurrentLevelSequence"
    })
    current_seq = r.json().get('ReturnValue', '')
    
    # Get character
    r = requests.put(f"{BASE_URL}/object/call", json={
        "objectPath": "/Script/UnrealEd.Default__EditorActorSubsystem",
        "functionName": "GetAllLevelActors"
    })
    actors = r.json().get('ReturnValue', [])
    character = [a for a in actors if 'Character' in str(a)][0]
    
    # Add possessable
    r = requests.put(f"{BASE_URL}/object/call", json={
        "objectPath": "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "functionName": "AddPossessable",
        "parameters": {"Sequence": current_seq, "ObjectToPossess": character}
    })
    binding = r.json().get('ReturnValue', {})
    
    # Add track
    r = requests.put(f"{BASE_URL}/object/call", json={
        "objectPath": "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
        "functionName": "AddTrack",
        "parameters": {"InBinding": binding, "TrackType": "/Script/MovieSceneTracks.MovieScene3DTransformTrack"}
    })
    track = r.json().get('ReturnValue', '')
    
    # Add section
    r = requests.put(f"{BASE_URL}/object/call", json={
        "objectPath": "/Script/SequencerScripting.Default__MovieSceneTrackExtensions",
        "functionName": "AddSection",
        "parameters": {"Track": track}
    })
    section = r.json().get('ReturnValue', '')
    
    return section, track

def main():
    print("=" * 80)
    print("Searching for transform/keyframe APIs")
    print("=" * 80)
    
    section, track = setup()
    print(f"\nSection: {section}")
    print(f"Track: {track}")
    
    # Check section extensions for keyframe-related functions
    print("\n" + "=" * 80)
    print("MovieSceneSectionExtensions functions:")
    print("=" * 80)
    info = describe_object("/Script/SequencerScripting.Default__MovieSceneSectionExtensions")
    functions = info.get('Functions', [])
    
    keyframe_funcs = [f for f in functions if any(word in f['Name'].lower() 
                      for word in ['key', 'transform', 'location', 'add', 'set'])]
    
    for func in keyframe_funcs:
        print(f"\n{func['Name']}")
        for param in func.get('Parameters', []):
            print(f"  - {param['Name']}: {param['Type']}")
    
    # Check track extensions
    print("\n" + "=" * 80)
    print("MovieSceneTrackExtensions functions:")
    print("=" * 80)
    info = describe_object("/Script/SequencerScripting.Default__MovieSceneTrackExtensions")
    functions = info.get('Functions', [])
    
    keyframe_funcs = [f for f in functions if any(word in f['Name'].lower() 
                      for word in ['key', 'transform', 'location', 'add', 'set'])]
    
    for func in keyframe_funcs:
        print(f"\n{func['Name']}")
        for param in func.get('Parameters', []):
            print(f"  - {param['Name']}: {param['Type']}")

if __name__ == "__main__":
    main()
