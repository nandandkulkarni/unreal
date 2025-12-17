"""
Test different approaches for adding keyframes to channels
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

def setup():
    """Setup binding, track, section"""
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    current_seq = current.get('ReturnValue', '')
    
    # Get character
    success, result = call_function(
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "GetAllLevelActors"
    )
    all_actors = result.get('ReturnValue', [])
    character = [a for a in all_actors if 'Character' in str(a)][0]
    
    # AddPossessable
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "AddPossessable",
        {"Sequence": current_seq, "ObjectToPossess": character}
    )
    binding = result.get('ReturnValue', {})
    
    # AddTrack
    success, track_result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
        "AddTrack",
        {"InBinding": binding, "TrackType": "/Script/MovieSceneTracks.MovieScene3DTransformTrack"}
    )
    track = track_result.get('ReturnValue', '')
    
    # AddSection
    success, section_result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneTrackExtensions",
        "AddSection",
        {"Track": track}
    )
    section = section_result.get('ReturnValue', '')
    
    return section

def test_keyframe_methods():
    """Test different ways to add keyframes"""
    
    print("=" * 80)
    print("TEST: Different methods for adding keyframes")
    print("=" * 80)
    
    section = setup()
    print(f"\n✓ Setup complete - Section: {section}")
    
    # Get channels info
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetAllChannels",
        {"Section": section}
    )
    channels = result.get('ReturnValue', [])
    print(f"✓ Channels: {channels[:3]}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS: Channels are transient objects - cannot call methods on them remotely")
    print("We may need to use Python API inside Unreal for keyframe addition")
    print("Remote Control API limitation: Can't access transient runtime objects")
    print("=" * 80)

if __name__ == "__main__":
    test_keyframe_methods()
