"""
Test calling AddKey on Default__MovieSceneScriptingFloatChannel with channel as first parameter
This MIGHT work if it's actually a static method that takes channel as first param
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
    print("=" * 80)
    print("TEST: AddKey as STATIC method with Channel parameter")
    print("=" * 80)
    
    # Get a channel from the section
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    print("\n[1] Getting channels...")
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
    if channels:
        print(f"    First channel: {channels[0]}")
    
    # Now try calling AddKey on the Default__ class with various parameter structures
    print("\n[2] Attempting to call AddKey...")
    
    # Attempt 1: Channel as self parameter (treating as pseudo-static)
    print("\n    Attempt 1: Channel + Time + NewValue + SubFrame + TimeUnit")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "AddKey",
        {
            "Channel": channels[0],
            "InTime": {"FrameNumber": {"Value": 100}},
            "NewValue": 555.0,
            "SubFrame": 0.0,
            "TimeUnit": 0  # DISPLAY_RATE
        }
    )
    print(f"      Result: Success={success}")
    if not success:
        print(f"      Error: {result[:200]}")
    else:
        print(f"      Data: {result}")
    
    # Attempt 2: Try without Channel parameter (maybe it uses 'self' implicitly?)
    print("\n    Attempt 2: InTime + NewValue only")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "AddKey",
        {
            "InTime": {"FrameNumber": {"Value": 110}},
            "NewValue": 666.0
        }
    )
    print(f"      Result: Success={success}")
    if not success:
        print(f"      Error: {result[:200]}")
    else:
        print(f"      Data: {result}")
    
    # Attempt 3: Call it ON the channel path itself
    print("\n    Attempt 3: Call AddKey ON the channel object path")
    success, result = call_function(
        channels[0],  # Call on the channel itself
        "AddKey",
        {
            "InTime": {"FrameNumber": {"Value": 120}},
            "NewValue": 777.0,
            "SubFrame": 0.0
        }
    )
    print(f"      Result: Success={success}")
    if not success:
        print(f"      Error: {result[:200]}")
    else:
        print(f"      Data: {result}")

if __name__ == "__main__":
    main()
