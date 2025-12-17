"""
Run Complete Cinematic Script via Remote Control API
This script sends the cinematic creation script to Unreal Engine via HTTP Remote Control API

REQUIREMENTS:
1. Unreal Engine must be running
2. Start the web server in Unreal console: WebControl.StartServer
"""

import requests
import json

# Remote Control API endpoint
UNREAL_URL = "http://localhost:30010/remote/object/call"

def execute_python_in_unreal(script_path):
    """Execute Python script in Unreal Engine via PythonScriptLibrary"""
    
    # Read the script file
    with open(script_path, 'r', encoding='utf-8') as f:
        python_code = f.read()
    
    print(f"Attempting multiple object paths and methods...\n")
    
    # Try different object paths
    object_paths = [
        "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "/Engine/PythonTypes.Default__PythonScriptLibrary",
        "/Script/PythonScriptPlugin.PythonScriptLibrary",
        "/Engine/Transient.PythonScriptPlugin:Default__PythonScriptLibrary"
    ]
    
    for i, obj_path in enumerate(object_paths, 1):
        print("=" * 60)
        print(f"ATTEMPT {i}: {obj_path}")
        print("=" * 60)
        
        payload = {
            "objectPath": obj_path,
            "functionName": "ExecutePythonCommand",
            "parameters": {
                "PythonCommand": python_code
            },
            "generateTransaction": False
        }
        
        try:
            response = requests.put(UNREAL_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                print(f"✓ SUCCESS with path: {obj_path}")
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                print("\n" + "=" * 60)
                print("Check logs: C:\\U\\CinematicPipeline_Scripts\\logs\\")
                print("=" * 60)
                return True
            else:
                print(f"✗ Failed: HTTP {response.status_code}")
                print(f"Response: {response.text}\n")
        except Exception as e:
            print(f"✗ Error: {e}\n")
    
    print("=" * 60)
    print("✗ ALL ATTEMPTS FAILED")
    print("=" * 60)
    return False
    
    try:
        response = requests.put(UNREAL_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            print("✓ Command sent successfully!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            print("\n" + "=" * 60)
            print("Check the latest log file in:")
            print("C:\\U\\CinematicPipeline_Scripts\\logs\\")
            print("Or check Unreal's Output Log window")
            print("=" * 60)
            return True
            
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Could not connect to Unreal Engine")
        print("Make sure:")
        print("  1. Unreal Engine is running")
        print("  2. Run in Unreal console: WebControl.StartServer")
        print("  3. Port 30010 is accessible")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    script_path = r"C:\U\CinematicPipeline_Scripts\unreal_scripts\create_complete_cinematic.py"
    
    print(f"Script: {script_path}\n")
    
    # Execute it
    execute_python_in_unreal(script_path)
