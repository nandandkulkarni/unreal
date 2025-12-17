"""
BREAKTHROUGH: get_channel() takes channel_name (Name), not index!
Try getting channels by their actual names like "Location.X", "Location.Y", etc.
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
    print("GET CHANNELS BY NAME")
    print("=" * 80)
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    # Common channel names for 3D Transform
    channel_names = [
        "Location.X",
        "Location.Y",
        "Location.Z",
        "Rotation.X",
        "Rotation.Y",
        "Rotation.Z",
        "Scale.X",
        "Scale.Y",
        "Scale.Z",
        # Maybe they're just simple names?
        "X",
        "Y",
        "Z",
        # Or maybe numbered?
        "Channel0",
        "Channel1",
        "Channel2",
    ]
    
    print("\n[1] Trying different channel names...")
    
    for channel_name in channel_names:
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
            "GetChannel",
            {"Section": section_path, "ChannelName": channel_name}
        )
        
        if success:
            channel = result.get('ReturnValue')
            if channel:  # Not empty string
                print(f"  ✓ '{channel_name}' -> {channel}")
            else:
                print(f"  ✗ '{channel_name}' -> empty")
        else:
            if "does not exist" not in str(result):
                print(f"  ✗ '{channel_name}' -> {result[:100]}")
    
    # Also try GetAllChannels to see what the actual channel objects look like
    print("\n[2] Getting all channels to see their structure...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetAllChannels",
        {"Section": section_path}
    )
    
    if success:
        channels = result.get('ReturnValue', [])
        print(f"  Got {len(channels)} channels:")
        for i, ch in enumerate(channels[:9]):
            print(f"    [{i}] {ch}")

if __name__ == "__main__":
    main()
