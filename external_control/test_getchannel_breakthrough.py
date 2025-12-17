"""
BREAKTHROUGH: GetChannel works! Let's see what it returns and use it with AddKey
"""
import requests
import json

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
    print("BREAKTHROUGH: Using GetChannel + AddKey")
    print("=" * 80)
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    print("\n[1] Getting channels using GetChannel for indices 0, 1, 2...")
    
    channels = []
    for i in range(9):  # Try getting all 9 channels (X,Y,Z location, rotation, scale)
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
            "GetChannel",
            {"Section": section_path, "ChannelIndex": i}
        )
        
        if success:
            channel = result.get('ReturnValue')
            channels.append(channel)
            print(f"    Channel {i}: {channel} (type: {type(channel).__name__})")
        else:
            print(f"    Channel {i}: FAILED - {result[:100]}")
            break
    
    print(f"\n    Total channels retrieved: {len(channels)}")
    
    # Now try using these channel references with AddKey
    print("\n[2] Testing AddKey with GetChannel results...")
    
    if len(channels) >= 3:
        # Try adding a key to the X channel (index 0)
        print(f"\n    Adding key to X channel...")
        print(f"    Channel ref: {channels[0]}")
        print(f"    Channel ref type: {type(channels[0])}")
        print(f"    Channel ref repr: {repr(channels[0])}")
        
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
            "AddKey",
            {
                "Channel": channels[0],
                "InTime": {"FrameNumber": {"Value": 150}},
                "NewValue": 888.0,
                "SubFrame": 0.0,
                "TimeUnit": 0
            }
        )
        
        print(f"\n    Result: Success={success}")
        if success:
            print(f"    Data: {result}")
        else:
            print(f"    Error: {result[:200]}")
        
        # Try with all 3 location channels
        print(f"\n[3] Adding keyframes to X, Y, Z channels...")
        
        waypoint = (500.0, 300.0, 150.0)
        frame = 200
        
        for channel_idx, value in enumerate(waypoint):
            if channel_idx < len(channels):
                print(f"\n    Channel {channel_idx} (value={value}):")
                
                success, result = call_function(
                    "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
                    "AddKey",
                    {
                        "Channel": channels[channel_idx],
                        "InTime": {"FrameNumber": {"Value": frame}},
                        "NewValue": value,
                        "SubFrame": 0.0,
                        "TimeUnit": 0
                    }
                )
                
                if success:
                    print(f"      ✓ SUCCESS!")
                else:
                    print(f"      [X] Failed: {result[:150]}")
    else:
        print("    [X] Not enough channels retrieved")

if __name__ == "__main__":
    main()
