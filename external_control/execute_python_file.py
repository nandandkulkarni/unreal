"""
Execute Unreal Python script via file execution
This bypasses the Remote Control serialization issues
"""
import requests
import os

BASE_URL = "http://localhost:30010/remote"

def execute_unreal_python_file(script_path):
    """Execute a Python file in Unreal's Python interpreter"""
    
    # Convert to absolute path and use forward slashes
    abs_path = os.path.abspath(script_path).replace('\\', '/')
    
    # Build Python command to execute the file
    python_command = f"exec(open(r'{abs_path}').read())"
    
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": python_command}
    }
    
    response = requests.put(f"{BASE_URL}/object/call", json=payload)
    
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def main():
    print("=" * 70)
    print("EXECUTE UNREAL PYTHON SCRIPT")
    print("=" * 70)
    
    script_path = "C:/U/CinematicPipeline_Scripts/unreal_scripts/add_keyframes_to_sequence.py"
    
    print(f"\n[1] Executing script: {script_path}")
    print("    (Running in Unreal's Python interpreter)")
    
    success, result = execute_unreal_python_file(script_path)
    
    if success:
        print("\n[2] Script executed!")
        print(f"    Result: {result}")
        print("\n" + "=" * 70)
        print("Check Unreal Output Log for detailed execution results!")
        print("Open Sequencer to see the keyframes!")
        print("=" * 70)
    else:
        print(f"\n[X] Failed: {result}")
        if "cannot be accessed remotely" in str(result):
            print("\n    NOTE: PythonScriptLibrary is not exposed to Remote Control.")
            print("    You need to enable it in Project Settings > Remote Control")

if __name__ == "__main__":
    main()
