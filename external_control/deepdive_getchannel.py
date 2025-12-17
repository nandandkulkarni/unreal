"""
Deep dive into GetChannel - maybe it needs different parameters or returns something special
"""
import requests

BASE_URL = "http://localhost:30010/remote"

def describe_object(object_path):
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": object_path}
    )
    if response.status_code == 200:
        return response.json()
    return None

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
    print("DEEP DIVE INTO GETCHANNEL")
    print("=" * 80)
    
    # Get the full signature of GetChannel
    print("\n[1] Getting GetChannel signature...")
    info = describe_object("/Script/SequencerScripting.Default__MovieSceneSectionExtensions")
    
    if info:
        functions = info.get('Functions', [])
        for func in functions:
            if func['Name'] == 'GetChannel' or func['Name'] == 'GetChannelByType':
                print(f"\n{func['Name']}:")
                print(f"  Return Type: {func.get('ReturnType', 'void')}")
                print(f"  Parameters:")
                for param in func.get('Parameters', []):
                    print(f"    - {param['Name']}: {param['Type']}")
                    if 'Description' in param:
                        print(f"      Desc: {param['Description']}")
    
    section_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11.MovieScene3DTransformSection_0"
    
    # Try GetChannel with explicit parameter names
    print("\n[2] Testing GetChannel with different parameter combinations...")
    
    # Test 1: Just ChannelIndex
    print("\n  Test 1: ChannelIndex only")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannel",
        {"ChannelIndex": 0}
    )
    print(f"    Success: {success}")
    print(f"    Full result: {result}")
    
    # Test 2: Section + ChannelIndex
    print("\n  Test 2: Section + ChannelIndex")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannel",
        {"Section": section_path, "ChannelIndex": 0}
    )
    print(f"    Success: {success}")
    print(f"    Full result: {result}")
    
    # Test 3: Maybe there's GetChannelByType?
    print("\n  Test 3: GetChannelsByType")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannelsByType",
        {"Section": section_path}
    )
    print(f"    Success: {success}")
    if success:
        print(f"    Result: {result}")
    else:
        print(f"    Error: {result[:150]}")
    
    # Test 4: Check what type GetChannel actually returns
    print("\n[3] Analyzing GetChannel return value...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetChannel",
        {"Section": section_path, "ChannelIndex": 0}
    )
    
    if success:
        return_value = result.get('ReturnValue')
        print(f"    ReturnValue: '{return_value}'")
        print(f"    Type: {type(return_value)}")
        print(f"    Length: {len(return_value) if isinstance(return_value, str) else 'N/A'}")
        print(f"    Bool: {bool(return_value)}")
        print(f"    Full result keys: {list(result.keys())}")
        print(f"    Full result: {result}")

if __name__ == "__main__":
    main()
