"""
Trigger script to run motion matching database creation in Unreal Engine.

This script runs on your local machine and sends the database creation
script to Unreal Engine via HTTP.
"""
import requests
import os
import sys

def trigger_database_creation():
    """Send database creation script to Unreal Engine"""
    
    # Get the script path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "create_motion_database.py")
    
    print(f"Reading script: {script_path}")
    
    # Read the script content
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: Script not found: {script_path}")
        return False
    
    print(f"Script loaded ({len(script_content)} bytes)")
    print("\nSending to Unreal Engine...")
    
    # Send to Unreal Engine
    url = "http://localhost:30010/remote/object/call"
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {
            "PythonCommand": script_content
        }
    }
    
    try:
        response = requests.put(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✓ Script executed successfully")
            print("\nCheck Unreal Engine Output Log for results")
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to Unreal Engine")
        print("  Make sure:")
        print("  1. Unreal Engine is running")
        print("  2. Remote Control plugin is enabled")
        print("  3. HTTP server is running on port 30010")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("="*80)
    print("Motion Matching Database Creation - Remote Trigger")
    print("="*80)
    print()
    
    success = trigger_database_creation()
    
    print()
    print("="*80)
    if success:
        print("Next steps:")
        print("1. Check Unreal Engine Output Log for detailed results")
        print("2. Open /Game/MotionMatching/MannyMotionDatabase in Content Browser")
        print("3. Configure schema channels and add animations")
    else:
        print("Setup failed. Check error messages above.")
    print("="*80)
    
    sys.exit(0 if success else 1)
