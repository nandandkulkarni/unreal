
import requests
import sys
import os

RC_URL = "http://localhost:30010/remote/object/call"

def run_remote(script_path):
    if not os.path.exists(script_path):
        print(f"Error: File {script_path} not found.")
        return

    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()

    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": script_content}
    }
    
    print(f"Executing {script_path} on remote...")
    try:
        response = requests.put(RC_URL, json=payload, timeout=60)
        if response.status_code == 200:
            print("Success!")
            print("--- Remote Output ---")
            data = response.json()
            for entry in data.get("Output", []):
                print(entry.get("Message", ""))
        else:
            print(f"Failed with status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python exec_remote.py <script_file>")
    else:
        run_remote(sys.argv[1])
