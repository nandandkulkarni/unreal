"""
Run Simple Motion Tests
Reads `run_motion_tests.py` and executes it in Unreal Engine via Remote Control.
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
    test_script_path = os.path.join(script_dir, "run_motion_tests.py")
    
    print(f"Reading test script from: {test_script_path}")
    
    try:
        with open(test_script_path, "r", encoding='utf-8') as f:
            test_command = f.read()
        
        # Ensure run_all_tests() is called execution
        test_command += "\n\nif __name__ != '__main__':\n    run_all_tests()\n"
            
        print("\n" + "="*80)
        print("Running Simple Motion Tests (run_motion_tests.py)")
        print("="*80 + "\n")
        
        result = execute_python_command(test_command)
        print(f"Test execution result: {result}")
        print("Check Unreal Output Log (Film5.log) for details.")
        
    except FileNotFoundError:
        print(f"ERROR: Could not find test script at {test_script_path}")
    except Exception as e:
        print(f"ERROR: Failed to run test: {e}")

if __name__ == "__main__":
    run_test()
