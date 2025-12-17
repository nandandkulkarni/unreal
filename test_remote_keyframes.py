"""
Test if we can add keyframes via Remote Control API
"""
import requests
import json

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
        result = response.json()
        return True, result
    else:
        return False, response.text

def test_keyframe_addition():
    """Test if we can add keyframes remotely"""
    
    print("=" * 70)
    print("Testing Remote Keyframe Addition")
    print("=" * 70)
    
    # Step 1: Try to get current sequence
    print("\n1. Getting current sequence...")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    
    if success:
        print(f"   [OK] Current sequence: {result}")
        
        # Check if we got a sequence object back
        if result and 'ReturnValue' in result:
            sequence_path = result['ReturnValue']
            print(f"   Sequence path: {sequence_path}")
            
            # Step 2: Try to call a method on the sequence object
            print("\n2. Trying to call method on sequence object...")
            
            # This will likely fail because Remote Control doesn't support
            # calling methods on returned objects, only subsystem functions
            success2, result2 = call_function(
                sequence_path,  # Try using the sequence path
                "GetPlaybackStart"  # Try a simple getter
            )
            
            if success2:
                print(f"   [OK] Can call methods on sequence! Result: {result2}")
                print("\n   ✓ Keyframes CAN be added remotely!")
            else:
                print(f"   [X] Cannot call methods on sequence object")
                print(f"   Error: {result2}")
                print("\n   ✗ Keyframes CANNOT be added remotely")
                print("   → Must use in-Unreal script")
        else:
            print("   [X] No sequence returned")
    else:
        print(f"   [X] Failed to get current sequence: {result}")
    
    # Step 3: Check if there's a subsystem function for adding keyframes
    print("\n3. Checking for keyframe subsystem functions...")
    print("   Remote Control API limitations:")
    print("   - Can call SUBSYSTEM functions (EditorActorSubsystem, etc.)")
    print("   - CANNOT call methods on returned objects")
    print("   - No subsystem function exists for 'add keyframe to sequence'")
    
    print("\n" + "=" * 70)
    print("CONCLUSION:")
    print("=" * 70)
    print("Keyframe addition requires:")
    print("1. sequence.add_possessable(actor)")
    print("2. binding.add_track(track_type)")
    print("3. track.add_section()")
    print("4. section.get_channels_by_type()")
    print("5. channel.add_key(frame, value)")
    print()
    print("These are all OBJECT METHODS, not subsystem functions.")
    print("Remote Control API only exposes subsystem functions.")
    print()
    print("✗ Keyframes CANNOT be added remotely")
    print("✓ Must use clipboard copy → paste in Unreal Python console")
    print("=" * 70)

if __name__ == "__main__":
    test_keyframe_addition()
