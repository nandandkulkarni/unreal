"""
Trigger Cinematic Sequence Creation via Remote Control API
Uses Remote Control to call Unreal functions that trigger the Python script internally
"""

import requests
import json
import time

UNREAL_URL = "http://localhost:30010/remote/object/call"

def call_unreal_function(object_path, function_name, parameters=None):
    """Call a function on an Unreal object via Remote Control API"""
    
    payload = {
        "objectPath": object_path,
        "functionName": function_name,
        "parameters": parameters or {},
        "generateTransaction": False
    }
    
    try:
        response = requests.put(UNREAL_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def trigger_cinematic_creation():
    """Trigger cinematic sequence creation using console command"""
    
    print("=" * 60)
    print("Triggering Cinematic Creation via Remote Control")
    print("=" * 60)
    
    # Method 1: Use EditorScriptingUtilities to run Python
    print("\nAttempting to trigger via EditorUtilitySubsystem...")
    
    script_path = "C:/U/CinematicPipeline_Scripts/unreal_scripts/create_complete_cinematic.py"
    
    # Try calling the editor scripting utility
    success, result = call_unreal_function(
        "/Script/UnrealEd.Default__EditorUtilitySubsystem",
        "ExecutePythonCommandEx",
        {
            "Command": f'exec(open(r"{script_path}").read())'
        }
    )
    
    if success:
        print("✓ Successfully triggered cinematic creation!")
        print(f"Result: {json.dumps(result, indent=2)}")
        print("\nCheck Unreal Editor Sequencer - sequence should be created")
        print("Check logs: C:\\U\\CinematicPipeline_Scripts\\logs\\")
        return True
    else:
        print(f"✗ Failed: {result}")
        
        # Method 2: Direct console command
        print("\nAttempting alternative method...")
        print("Note: This requires the script to be set up as a startup script")
        return False

if __name__ == "__main__":
    print("Make sure:")
    print("  1. Unreal Engine is running")
    print("  2. WebControl.StartServer has been run in console")
    print("  3. Project is open\n")
    
    input("Press Enter to trigger cinematic creation...")
    
    trigger_cinematic_creation()
