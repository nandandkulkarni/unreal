"""
Test: Find methods that set transform values directly on sections
Without needing to access channels
"""
import requests

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

def main():
    print("=" * 70)
    print("TEST: Section-Level Transform Methods")
    print("=" * 70)
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    # Try 1: Set location using transform extensions
    print("\n[1] Try SetLocation on section...")
    success, result = call_function(
        section_path,
        "SetLocation",
        {"InLocation": {"X": 100.0, "Y": 200.0, "Z": 300.0}}
    )
    print(f"    Result: Success={success}, {result}")
    
    # Try 2: Try MovieScene3DTransformSection-specific methods
    print("\n[2] Try EvalTransform...")
    success, result = call_function(
        section_path,
        "EvalTransform",
        {"InTime": {"FrameNumber": {"Value": 0}}}
    )
    print(f"    Result: Success={success}, {result}")
    
    # Try 3: See if we can use unreal.MovieSceneScriptingActorReferenceKey
    print("\n[3] Check available properties...")
    
    # Try 4: Use the MovieSceneToolHelpers or LevelSequenceEditorBlueprintLibrary
    print("\n[4] Try using SequencerTools...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__SequencerTools",
        "GetObjectBindings",
        {}
    )
    print(f"    Result: Success={success}, {result[:200] if isinstance(result, str) else result}")
    
    # Try 5: Use Python-based keyframe setting if available
    print("\n[5] Try MovieSceneSequenceExtensions.SetTransformKey...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "SetTransformKey",
        {
            "Sequence": "/Game/Sequences/TestSequence.TestSequence",
            "Binding": {"BindingID": {"A": 1517953254, "B": 1260393600, "C": -1206917210, "D": 963686623}, "Sequence": "/Game/Sequences/TestSequence.TestSequence"},
            "InTime": {"FrameNumber": {"Value": 50}},
            "InTransform": {
                "Translation": {"X": 400.0, "Y": 500.0, "Z": 100.0},
                "Rotation": {"X": 0.0, "Y": 0.0, "Z": 0.0},
                "Scale3D": {"X": 1.0, "Y": 1.0, "Z": 1.0}
            }
        }
    )
    print(f"    Result: Success={success}, {result}")

if __name__ == "__main__":
    main()
