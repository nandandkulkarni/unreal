"""
Test: Add keyframes using MovieSceneScriptingChannel directly
Try to use th object returned by GetAllChannels properly
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
    print("TEST: Add Keys to Channels Using Scripting API")
    print("=" * 70)
    
    # The section object path from our previous run
    # This should be updated to match what we got from the last run
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    print("\n[1] Getting channels from section...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetAllChannels",
        {"Section": section_path}
    )
    
    if not success:
        print(f"    [X] Failed: {result}")
        return
    
    channels = result.get('ReturnValue', [])
    print(f"    Got {len(channels)} channels")
    
    if len(channels) < 3:
        print(f"    [X] Need at least 3 channels, got {len(channels)}")
        return
    
    # Print channel info
    for i, ch in enumerate(channels[:3]):
        print(f"    Channel {i}: {ch}")
    
    # Try adding a key using the channel as a parameter to the static method
    print("\n[2] Adding test key to first channel (X)...")
    
    # First try: Pass channel as object reference
    print("\n    Attempt 1: Channel as object parameter...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "AddKey",
        {
            "Channel": channels[0],  # Pass the channel object from GetAllChannels
            "InTime": {"FrameNumber": {"Value": 10}},
            "NewValue": 123.45,
            "SubFrame": 0.0,
            "TimeUnit": 0  # ESequenceTimeUnit::DisplayRate
        }
    )
    
    if success:
        print(f"      ✓ Success! Result: {result}")
    else:
        print(f"      [X] Failed: {result}")
    
    # Second try: Different parameter structure
    print("\n    Attempt 2: Using Time/Value structure...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "AddKey",
        {
            "Channel": channels[0],
            "Time": {"FrameNumber": {"Value": 20}},
            "Value": 234.56
        }
    )
    
    if success:
        print(f"      ✓ Success! Result: {result}")
    else:
        print(f"      [X] Failed: {result}")
    
    # Third try: Minimal parameters
    print("\n    Attempt 3: Minimal parameters...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "AddKey",
        {
            "Channel": channels[0],
            "Time": 30,
            "Value": 345.67
        }
    )
    
    if success:
        print(f"      ✓ Success! Result: {result}")
    else:
        print(f"      [X] Failed: {result}")

if __name__ == "__main__":
    main()
