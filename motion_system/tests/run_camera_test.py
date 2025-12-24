"""
Run Camera Move test and render results
Reads `camera_test_script.py` and executes it in Unreal Engine via Remote Control.
"""
import requests
import time
import os

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

def execute_python_command(command):
    """Execute Python command in Unreal via Remote Control"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": command}
    }
    response = requests.put(REMOTE_CONTROL_URL, headers={'Content-Type': 'application/json'}, json=payload)
    return response.json()

def run_test():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_script_path = os.path.join(script_dir, "camera_test_script.py")
    
    print(f"Reading test script from: {test_script_path}")
    
    try:
        with open(test_script_path, "r") as f:
            test_command = f.read()
            
        print("\n" + "="*80)
        print("Running Camera Move Test")
        print("="*80 + "\n")
        
        result = execute_python_command(test_command)
        print(f"Test execution result: {result}")
        
    except FileNotFoundError:
        print(f"ERROR: Could not find test script at {test_script_path}")
    except Exception as e:
        print(f"ERROR: Failed to run test: {e}")

if __name__ == "__main__":
    run_test()
