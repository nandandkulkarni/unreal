"""
Access channels by INDEX rather than by transient object reference
This should give us a stable way to reference channels
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
    print("ACCESS CHANNELS BY INDEX")
    print("=" * 80)
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    # Try GetChannelsByType with different enum values
    print("\n[1] Testing GetChannelsByType with different values...")
    
    for i in range(5):
        print(f"\n  Trying ChannelType = {i}:")
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
            "FindChannelsByType",
            {"Section": section_path, "ChannelType": i}
        )
        
        if success:
            channels = result.get('ReturnValue', [])
            print(f"    ✓ Got {len(channels)} channels")
            if channels:
                print(f"      First: {channels[0]}")
        else:
            print(f"    [X] {result[:100]}")
    
    # Try getting channel by index
    print("\n[2] Testing GetChannel (singular) if it exists...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannel",
        {"Section": section_path, "ChannelIndex": 0}
    )
    
    if success:
        channel = result.get('ReturnValue')
        print(f"    ✓ Got channel: {channel}")
    else:
        print(f"    [X] {result[:100]}")
    
    # Try GetChannelsByIndex
    print("\n[3] Testing GetChannelsByIndex...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannelsByIndex",
        {"Section": section_path, "ChannelIndices": [0, 1, 2]}
    )
    
    if success:
        channels = result.get('ReturnValue', [])
        print(f"    ✓ Got {len(channels)} channels")
        for i, ch in enumerate(channels):
            print(f"      [{i}]: {ch}")
    else:
        print(f"    [X] {result[:100]}")
    
    # Check what methods the section itself has
    print("\n[4] Maybe section has SetKeyAtTime or similar...")
    success, result = call_function(
        section_path,
        "GetStartFrame",
        {}
    )
    print(f"    GetStartFrame works: {success}")

if __name__ == "__main__":
    main()
