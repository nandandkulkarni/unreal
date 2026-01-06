"""
Trigger Belica Animation Database Builder in Unreal

This script triggers the animation database builder inside Unreal Engine
via Remote Control API.
"""

import sys
import os
import requests

# Add motion_system_track_based to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

def build_animation_database():
    """Execute the animation database builder in Unreal."""
    
    print("Building Belica Animation Database...")
    print("=" * 60)
    
    # Path to the database builder script
    script_path = os.path.join(script_dir, "build_belica_anim_database.py")
    
    # Read the script
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # Execute via Remote Control
    url = "http://localhost:30010/remote/object/call"
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {
            "PythonCommand": script_content
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("\n✓ Animation database built successfully!")
            print(f"  Check: {script_dir}\\belica_anim_database.json")
            return True
        else:
            print(f"\n✗ Failed: HTTP {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = build_animation_database()
    sys.exit(0 if success else 1)
