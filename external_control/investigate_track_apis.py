"""
Investigate MovieScene3DTransformTrack - maybe IT has keyframe methods!
We've been focused on sections and channels, but tracks might have higher-level APIs
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
    print("INVESTIGATE TRACK-LEVEL APIS")
    print("=" * 80)
    
    # The actual track object from our sequence
    track_path = "/Game/Sequences/TestSequence.TestSequence:MovieScene_0.MovieScene3DTransformTrack_11"
    
    print("\n[1] Describe MovieScene3DTransformTrack...")
    info = describe_object(track_path)
    
    if info:
        functions = info.get('Functions', [])
        print(f"    Total functions: {len(functions)}")
        
        for func in functions:
            name = func['Name']
            if any(kw in name.lower() for kw in ['key', 'transform', 'location', 'set', 'add']):
                print(f"\n  {name}:")
                params = func.get('Parameters', [])
                if params:
                    for p in params:
                        print(f"      - {p['Name']}: {p['Type']}")
        
        # Show ALL functions
        print(f"\n\n  All functions on track:")
        for func in functions:
            print(f"    - {func['Name']}")
    
    # Try calling a method on the track itself
    print("\n\n[2] Try calling methods on track...")
    
    test_methods = [
        "SetTransformAtTime",
        "AddKeyAtTime", 
        "SetLocationAtTime",
        "AddTransformKey"
    ]
    
    for method in test_methods:
        print(f"\n  {method}:")
        success, result = call_function(
            track_path,
            method,
            {
                "Time": {"FrameNumber": {"Value": 100}},
                "Location": {"X": 500.0, "Y": 300.0, "Z": 150.0}
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
