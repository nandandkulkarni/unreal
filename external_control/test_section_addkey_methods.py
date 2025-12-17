"""
Key insight: Maybe we can add keys by passing SECTION + CHANNEL_INDEX
instead of trying to pass channel object references
"""
import requests

BASE_URL = "http://localhost:30010/remote"

def call_function(object_path, function_name, parameters=None):
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
    print("=" * 80)
    print("ADD KEY USING SECTION + INDEX APPROACH")
    print("=" * 80)
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    # Maybe there's an AddKeyToChannel method on SectionExtensions
    print("\n[1] Check if SectionExtensions has AddKey methods...")
    
    test_methods = [
        "AddKey",
        "AddKeyToChannel",
        "SetKeyValue",
        "SetChannelKeyValue",
        "AddKeyAtTime",
    ]
    
    for method in test_methods:
        print(f"\n  Testing: {method}")
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
            method,
            {
                "Section": section_path,
                "ChannelIndex": 0,
                "Time": {"FrameNumber": {"Value": 50}},
                "Value": 999.0
            }
        )
        
        if success:
            print(f"    ✓ SUCCESS! {result}")
        else:
            if "does not exist" in str(result):
                print(f"    - Method doesn't exist")
            else:
                print(f"    [X] {result[:150]}")
    
    # Maybe MovieScene3DTransformSection has specific methods
    print("\n[2] Check MovieScene3DTransformSection for direct methods...")
    
    transform_methods = [
        "SetLocation",
        "SetLocationAtTime",
        "AddLocationKey",
        "SetTransformAtTime",
    ]
    
    for method in transform_methods:
        print(f"\n  Testing: {method}")
        success, result = call_function(
            section_path,
            method,
            {
                "Time": {"FrameNumber": {"Value": 60}},
                "Location": {"X": 100.0, "Y": 200.0, "Z": 300.0}
            }
        )
        
        if success:
            print(f"    ✓ SUCCESS! {result}")
        else:
            if "does not exist" in str(result):
                print(f"    - Method doesn't exist")
            else:
                print(f"    [X] {result[:150]}")

if __name__ == "__main__":
    main()
