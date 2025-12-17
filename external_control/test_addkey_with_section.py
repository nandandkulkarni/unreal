"""
CRITICAL TEST: Call AddKey with Section + ChannelIndex instead of Channel object
Maybe AddKey needs the section context to know which channel to modify!
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
    print("CRITICAL TEST: AddKey with Section + ChannelIndex")
    print("=" * 80)
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    # Try 1: Call AddKey with Section and ChannelIndex as parameters
    print("\n[1] Try AddKey with Section + ChannelIndex parameters...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "AddKey",
        {
            "Section": section_path,
            "ChannelIndex": 0,
            "InTime": {"FrameNumber": {"Value": 50}},
            "NewValue": 999.0,
            "SubFrame": 0.0,
            "TimeUnit": 0
        }
    )
    
    print(f"    Success: {success}")
    if success:
        print(f"    Result: {result}")
    else:
        print(f"    Error: {result[:200]}")
    
    # Try 2: Maybe there's an AddKeyToSection method?
    print("\n[2] Try AddKeyToChannel on SectionExtensions...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "AddKeyToChannel",
        {
            "Section": section_path,
            "ChannelIndex": 0,
            "Time": {"FrameNumber": {"Value": 60}},
            "Value": 888.0
        }
    )
    
    print(f"    Success: {success}")
    if success:
        print(f"    Result: {result}")
    else:
        if "does not exist" in str(result):
            print(f"    Method doesn't exist")
        else:
            print(f"    Error: {result[:200]}")
    
    # Try 3: What if we need to get the channel IN THE SAME CALL?
    # Maybe call structure needs to be nested?
    print("\n[3] Try calling GetChannel then immediately AddKey...")
    
    # First get channel
    success1, result1 = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannel",
        {"Section": section_path, "ChannelIndex": 0}
    )
    
    print(f"    GetChannel: {success1}, channel='{result1.get('ReturnValue', '')}'")
    
    if success1:
        # Immediately use it
        channel_ref = result1.get('ReturnValue', '')
        
        # Try with InTime/NewValue (from docs)
        success2, result2 = call_function(
            "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
            "AddKey",
            {
                "Channel": channel_ref,
                "InTime": {"FrameNumber": {"Value": 70}},
                "NewValue": 777.0,
                "SubFrame": 0.0,
                "TimeUnit": 0,
                "Interpolation": 0  # Try adding interpolation
            }
        )
        
        print(f"    AddKey: {success2}")
        if success2:
            print(f"    Result: {result2}")
        else:
            print(f"    Error: {result2[:200]}")
        
        # Now verify if key was added
        success3, result3 = call_function(
            "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
            "GetNumKeys",
            {"Channel": channel_ref}
        )
        
        if success3:
            num_keys = result3.get('ReturnValue', 0)
            print(f"    Verification: {num_keys} keys in channel")

if __name__ == "__main__":
    main()
