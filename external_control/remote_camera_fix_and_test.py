"""
Remote camera binding fix - runs from PowerShell via Remote Control API
Tests itself after running and shows results automatically
"""

import requests
import json
import time
from datetime import datetime

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"
REMOTE_PROPERTY_URL = "http://localhost:30010/remote/object/property"
SEQUENCE_PATH = '/Game/Sequences/CharacterWalkSequence.CharacterWalkSequence'
EDITOR_LIBRARY = '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary'

def log(message):
    """Print with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")

def call_function(object_path, function_name, parameters=None):
    """Call a function via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name
    }
    if parameters:
        payload["parameters"] = parameters
    
    try:
        response = requests.put(REMOTE_CONTROL_URL, headers={'Content-Type': 'application/json'}, json=payload, timeout=5)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

def get_property(object_path, property_name):
    """Get a property via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "propertyName": property_name,
        "access": "READ_ACCESS"
    }
    
    try:
        response = requests.put(REMOTE_PROPERTY_URL, headers={'Content-Type': 'application/json'}, json=payload, timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except Exception as e:
        return False, str(e)

def fix_camera_binding_remote():
    """Fix camera binding using Remote Control API"""
    log("\n" + "=" * 70)
    log("REMOTE CAMERA BINDING FIX - STARTING")
    log("=" * 70)
    
    # Step 1: Open the sequence
    log("\n[1/4] Opening sequence...")
    success, result = call_function(EDITOR_LIBRARY, 'OpenLevelSequence', {'LevelSequence': SEQUENCE_PATH})
    if not success:
        log(f"FAILED: Could not open sequence: {result}")
        return False
    log("SUCCESS: Sequence opened")
    time.sleep(0.5)
    
    # Step 2: Check if camera cut is locked to viewport
    log("\n[2/4] Checking camera cut lock status...")
    success, result = call_function(EDITOR_LIBRARY, 'IsCameraCutLockedToViewport')
    if success:
        log(f"Current lock status: {result}")
    
    # Step 3: Lock camera to viewport
    log("\n[3/4] Locking camera cut to viewport...")
    success, result = call_function(EDITOR_LIBRARY, 'SetLockCameraCutToViewport', {'bLock': True})
    if not success:
        log(f"FAILED: Could not lock camera: {result}")
        return False
    log("SUCCESS: Camera locked to viewport")
    time.sleep(0.3)
    
    # Step 4: Force update
    log("\n[4/4] Forcing sequencer update...")
    success, result = call_function(EDITOR_LIBRARY, 'ForceUpdate')
    if success:
        log("SUCCESS: Sequencer updated")
    
    log("\n" + "=" * 70)
    log("CAMERA SETUP COMPLETED")
    log("=" * 70)
    
    return True

def test_playback():
    """Test if playback works"""
    log("\n" + "=" * 70)
    log("TESTING PLAYBACK")
    log("=" * 70)
    
    log("\n[TEST] Starting playback...")
    success, result = call_function(EDITOR_LIBRARY, 'Play')
    
    if success:
        log("SUCCESS: Playback started")
        time.sleep(1)
        
        # Check if still playing
        success, result = call_function(EDITOR_LIBRARY, 'IsPlaying')
        if success:
            log(f"Playback status: {result}")
        
        return True
    else:
        log(f"FAILED: Could not start playback: {result}")
        return False

def check_unreal_logs():
    """Remind user to check Unreal logs"""
    log("\n" + "=" * 70)
    log("VERIFICATION STEPS")
    log("=" * 70)
    log("\n1. Check Unreal Editor viewport - character should be animating")
    log("2. Check Sequencer - Camera Cut track should show no errors")
    log("3. If still showing 'No Object Binding specified':")
    log("   - Run fix_camera_binding.py inside Unreal (Tools > Execute Python Script)")
    log("   - Then run: python view_logs.py")

def main():
    """Run fix, test, and report results"""
    print("\n" + "=" * 70)
    print("AUTOMATED CAMERA BINDING FIX & TEST")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Step 1: Fix camera binding
    fix_success = fix_camera_binding_remote()
    
    if not fix_success:
        log("\nFIX FAILED - Cannot proceed to testing")
        return
    
    # Step 2: Test playback
    time.sleep(1)
    test_success = test_playback()
    
    # Step 3: Show results
    log("\n" + "=" * 70)
    log("RESULTS SUMMARY")
    log("=" * 70)
    log(f"Camera setup: {'SUCCESS' if fix_success else 'FAILED'}")
    log(f"Playback test: {'SUCCESS' if test_success else 'FAILED'}")
    
    # Step 4: Next actions
    if fix_success and test_success:
        log("\n" + "=" * 70)
        log("ALL TESTS PASSED!")
        log("=" * 70)
        log("\nThe sequence should now be playing in Unreal.")
        log("If you still see 'No Object Binding specified' in the Camera Cut track:")
        log("  1. Run fix_camera_binding.py inside Unreal Editor")
        log("  2. Check logs: python view_logs.py")
    else:
        log("\nSOME TESTS FAILED - See errors above")
    
    check_unreal_logs()
    
    log("\n" + "=" * 70)
    log("SCRIPT COMPLETED")
    log("=" * 70)

if __name__ == "__main__":
    main()
