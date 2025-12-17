"""
Trigger sequence rendering remotely via Remote Control API
Run from PowerShell: python remote_render_sequence.py
"""

import requests
import json
import time
from datetime import datetime
import os

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"
SEQUENCE_PATH = '/Game/Sequences/CharacterWalkSequence.CharacterWalkSequence'

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
        response = requests.put(REMOTE_CONTROL_URL, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

def render_sequence_remote():
    """Render sequence via Remote Control API"""
    log("\n" + "=" * 70)
    log("REMOTE SEQUENCE RENDERING")
    log("=" * 70)
    
    # Step 1: Open the sequence
    log("\n[1/5] Opening sequence...")
    success, result = call_function(
        '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary',
        'OpenLevelSequence',
        {'LevelSequence': SEQUENCE_PATH}
    )
    
    if not success:
        log(f"FAILED: Could not open sequence: {result}")
        return False
    
    log("SUCCESS: Sequence opened")
    time.sleep(0.5)
    
    # Step 2: Set up render to current viewport
    log("\n[2/5] Locking camera to viewport...")
    success, result = call_function(
        '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary',
        'SetLockCameraCutToViewport',
        {'bLock': True}
    )
    
    if success:
        log("SUCCESS: Camera locked")
    time.sleep(0.3)
    
    # Step 3: Use Sequencer's render movie command
    log("\n[3/5] Initiating render to movie...")
    log("Attempting to trigger render via Sequencer...")
    
    # Try to use the Sequencer's render movie function
    # This is exposed through the editor scripting utilities
    success, result = call_function(
        '/Script/SequencerScripting.Default__SequencerTools',
        'RenderMovie',
        {
            'InCaptureSettings': {
                'OutputDirectory': {'Path': 'C:/U/CinematicPipeline/Saved/VideoCaptures'},
                'GameModeOverride': None,
                'OutputFormat': '{sequence}',
                'bOverwriteExisting': True,
                'bUseRelativeFrameNumbers': False,
                'HandleFrames': 0,
                'ZeroPadFrameNumbers': 4,
                'FrameRate': {'Numerator': 30, 'Denominator': 1},
                'bUseCustomFrameRate': True,
                'Resolution': {'X': 1920, 'Y': 1080},
                'bEnableTextureStreaming': True,
                'CinematicEngineScalability': True,
                'CinematicMode': True
            }
        }
    )
    
    if success:
        log("SUCCESS: Render command sent")
        log("Video rendering initiated!")
    else:
        log(f"Method 1 failed: {result}")
        
        # Alternative: Play sequence while recording viewport
        log("\n[3.5/5] Trying play + viewport capture method...")
        
        # Start playback first
        log("Starting sequence playback...")
        success, result = call_function(
            '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary',
            'Play'
        )
        
        if not success:
            log(f"FAILED: Could not start playback: {result}")
            log("\nNOTE: Direct rendering via Remote Control API may not be supported.")
            log("Recommendation: Use render_sequence_to_video.py inside Unreal instead.")
            return False
        
        log("SUCCESS: Sequence playing - you should see it animating in Unreal viewport")
        log("\nNOTE: Sequence is playing but viewport capture via Remote Control")
        log("is not directly supported.")
        log("\nFor actual video recording, you need to:")
        log("1. Run render_sequence_to_video.py inside Unreal, OR")
        log("2. Use Unreal's Movie Render Queue manually:")
        log("   Window > Cinematics > Movie Render Queue")
        log("   Add your sequence and click 'Render (Local)'")
    
    # Step 4: Verify output location
    log("\n[4/5] Checking output location...")
    output_dir = "C:/U/CinematicPipeline/Saved/VideoCaptures"
    
    if os.path.exists(output_dir):
        log(f"SUCCESS: Output directory exists: {output_dir}")
        files = os.listdir(output_dir)
        if files:
            log(f"Files in directory: {len(files)}")
            for f in files[:5]:  # Show first 5 files
                log(f"  - {f}")
        else:
            log("Directory is empty (render may still be processing)")
    else:
        log(f"WARNING: Output directory does not exist yet")
        log("Directory will be created during render")
    
    # Step 5: Instructions
    log("\n[5/5] Render information:")
    log("=" * 70)
    log("Output location: C:/U/CinematicPipeline/Saved/VideoCaptures")
    log("Expected file: CharacterWalkSequence.avi or .mov")
    log("\nMonitor render progress:")
    log("1. Check Unreal Editor - render progress should be visible")
    log("2. Check Output Log in Unreal")
    log("3. Watch the output folder for new files")
    log("\nIf render didn't start:")
    log("- Run render_sequence_to_video.py inside Unreal (Tools > Execute Python Script)")
    log("- Remote rendering may require additional plugins/configuration")
    log("=" * 70)
    
    return True

def main():
    print("\n" + "=" * 70)
    print("REMOTE SEQUENCE RENDER TRIGGER")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    success = render_sequence_remote()
    
    if success:
        log("\n" + "=" * 70)
        log("RENDER PROCESS INITIATED")
        log("=" * 70)
        log("\nCheck Unreal Editor for render progress")
        log("Output will appear in: C:/U/CinematicPipeline/Saved/VideoCaptures")
    else:
        log("\n" + "=" * 70)
        log("RENDER TRIGGER FAILED")
        log("=" * 70)
        log("\nFallback: Run render_sequence_to_video.py inside Unreal")

if __name__ == "__main__":
    main()
