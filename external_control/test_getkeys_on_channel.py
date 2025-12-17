"""
Maybe we need to call AddKey in a single transaction with the channel lookup?
Or use GetKeys first to see the existing structure?
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
    print("TEST: Can we GET existing keys or structure?")
    print("=" * 80)
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    # Get a channel
    print("\n[1] Getting channel 0...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannel",
        {"Section": section_path, "ChannelIndex": 0}
    )
    
    channel = result.get('ReturnValue', '')
    channel_name = result.get('ChannelName', 'None')
    print(f"    Channel: '{channel}'")
    print(f"    ChannelName: '{channel_name}'")
    
    # Try calling GetKeys on the channel using the Default__ class
    print("\n[2] Trying to GetKeys on this channel...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "GetKeys",
        {"Channel": channel}
    )
    
    print(f"    Success: {success}")
    if success:
        keys = result.get('ReturnValue', [])
        print(f"    Keys found: {len(keys)}")
        print(f"    Keys: {keys}")
    else:
        print(f"    Error: {result[:200]}")
    
    # Try GetNumKeys
    print("\n[3] Trying GetNumKeys...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "GetNumKeys",
        {"Channel": channel}
    )
    
    print(f"    Success: {success}")
    if success:
        num = result.get('ReturnValue', 0)
        print(f"    Num keys: {num}")
    else:
        print(f"    Error: {result[:200]}")
    
    # Maybe we need to use GetChannels (plural) from SectionExtensions?
    print("\n[4] Try GetChannels (plural)?...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannels",
        {"Section": section_path}
    )
    
    print(f"    Success: {success}")
    if success:
        print(f"    Result: {result}")
    else:
        if "does not exist" in str(result):
            print(f"    Method doesn't exist")
        else:
            print(f"    Error: {result[:200]}")

if __name__ == "__main__":
    main()
