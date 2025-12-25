import requests
import os
import sys

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

def run_diagnostic(script_relative_path):
    """Run a diagnostic Python script in Unreal Engine via remote control"""
    
    # Absolute path to the diagnostic script
    script_path = os.path.abspath(os.path.join(os.getcwd(), script_relative_path))
    
    try:
        with open(script_path, "r", encoding='utf-8') as f:
            script_content = f.read()
        
        payload = {
            "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
            "functionName": "ExecutePythonCommand",
            "parameters": {"PythonCommand": script_content}
        }
        
        print(f"--- Running Diagnostic: {script_relative_path} ---")
        response = requests.put(REMOTE_CONTROL_URL, json=payload, timeout=60)
        print(f"Result: {response.json()}")
        
    except Exception as e:
        print(f"ERROR: Failed to run diagnostic: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_diagnostic(sys.argv[1])
    else:
        print("Usage: python run_diagnostic.py <path_to_diagnostic_script>")
