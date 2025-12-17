"""
Simple test script to play existing sequence via Remote Control API
Tests SetLockCameraCutToViewport + ForceUpdate + Play
"""

import requests
import json
import time
from datetime import datetime

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"
EDITOR_LIBRARY = '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary'
SEQUENCE_PATH = '/Game/Sequences/CharacterWalkSequence.CharacterWalkSequence'

def call_function(object_path, function_name, parameters=None):
    """Call a function on an Unreal object via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name
    }
    
    if parameters:
        payload["parameters"] = parameters
    
    try:
        response = requests.put(
            REMOTE_CONTROL_URL,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
            
    except Exception as e:
        return False, str(e)

def test_sequence_playback():
    """Test playing the existing sequence"""
    print("\n" + "=" * 70)
    print("TESTING SEQUENCE PLAYBACK WITH VIEWPORT LOCK")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Sequence: {SEQUENCE_PATH}\n")
    
    # Step 1: Open sequence
    print("Step 1: Opening sequence...")
    success, result = call_function(
        EDITOR_LIBRARY,
        'OpenLevelSequence',
        {'LevelSequence': SEQUENCE_PATH}
    )
    
    if not success:
        print(f"✗ FAILED to open sequence: {result}")
        return False
    print("✓ Sequence opened")
    time.sleep(0.5)
    
    # Step 2: Lock camera to viewport (KEY FIX)
    print("\nStep 2: Locking camera cut to viewport...")
    success, result = call_function(
        EDITOR_LIBRARY,
        'SetLockCameraCutToViewport',
        {'bLock': True}
    )
    
    if not success:
        print(f"⚠ WARNING: Could not lock camera: {result}")
    else:
        print("✓ Camera cut locked to viewport")
    time.sleep(0.3)
    
    # Step 3: Force update
    print("\nStep 3: Forcing sequencer update...")
    success, result = call_function(
        EDITOR_LIBRARY,
        'ForceUpdate'
    )
    
    if success:
        print("✓ Sequencer updated")
    time.sleep(0.3)
    
    # Step 4: Play
    print("\nStep 4: Starting playback...")
    success, result = call_function(
        EDITOR_LIBRARY,
        'Play'
    )
    
    if success:
        print("✓ PLAYBACK STARTED!")
        print("\n" + "=" * 70)
        print("CHECK UNREAL: Character should now be animating in viewport!")
        print("=" * 70)
        return True
    else:
        print(f"✗ FAILED to start playback: {result}")
        return False

if __name__ == "__main__":
    test_sequence_playback()
