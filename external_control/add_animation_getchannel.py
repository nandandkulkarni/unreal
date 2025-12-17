"""
FINAL TEST: Add complete animation using GetChannel + AddKey approach
Then verify the keyframes were actually created
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
    print("COMPLETE ANIMATION USING GETCHANNEL APPROACH")
    print("=" * 80)
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    # Get channels
    print("\n[1] Getting channels...")
    channels = []
    for i in range(9):
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
            "GetChannel",
            {"Section": section_path, "ChannelIndex": i}
        )
        if success:
            channels.append(result.get('ReturnValue'))
    
    print(f"    Got {len(channels)} channels")
    
    # Define animation waypoints
    waypoints = [
        (0, 0, 100),
        (500, 0, 100),
        (500, 500, 100),
        (0, 500, 100),
        (0, 0, 100)
    ]
    
    frames_per_waypoint = 300 // (len(waypoints) - 1)
    
    print(f"\n[2] Adding {len(waypoints)} keyframes per channel...")
    keyframes_added = 0
    
    for wp_idx, (x, y, z) in enumerate(waypoints):
        frame = wp_idx * frames_per_waypoint
        location = [x, y, z]
        
        print(f"\n    Frame {frame}: ({x}, {y}, {z})")
        
        for channel_idx, value in enumerate(location):
            success, result = call_function(
                "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
                "AddKey",
                {
                    "Channel": channels[channel_idx],
                    "InTime": {"FrameNumber": {"Value": frame}},
                    "NewValue": value,
                    "SubFrame": 0.0,
                    "TimeUnit": 0  # Display rate
                }
            )
            
            if success:
                keyframes_added += 1
                print(f"      ✓ Channel {channel_idx}")
            else:
                print(f"      [X] Channel {channel_idx} failed")
    
    print(f"\n[3] Results:")
    print(f"    Total keyframes added: {keyframes_added}")
    print(f"    Expected: {len(waypoints) * 3}")
    
    # Verify by checking key count
    print(f"\n[4] Verifying keyframes...")
    for i in range(3):
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
            "GetNumKeys",
            {"Channel": channels[i]}
        )
        
        if success:
            num_keys = result.get('ReturnValue', 0)
            print(f"    Channel {i}: {num_keys} keys")
        else:
            print(f"    Channel {i}: Could not verify")
    
    if keyframes_added == len(waypoints) * 3:
        print("\n" + "=" * 80)
        print("SUCCESS! All keyframes added!")
        print("Open Sequencer in Unreal to see the animation!")
        print("=" * 80)

if __name__ == "__main__":
    main()
