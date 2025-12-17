"""
Try different object paths for PythonScriptLibrary
Sometimes the path format matters
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote/object/call"

# Try all possible path variations
python_paths = [
    "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "/Script/PythonScriptPlugin.PythonScriptLibrary",
    "/Engine/PythonTypes.Default__PythonScriptLibrary",
    "PythonScriptLibrary",
]

test_code = "print('Hello from Unreal!')"

print("=" * 80)
print("TRYING DIFFERENT PYTHONSCRIPTLIBRARY PATHS")
print("=" * 80)

for path in python_paths:
    print(f"\n[{python_paths.index(path) + 1}] Trying: {path}")
    
    payload = {
        "objectPath": path,
        "functionName": "ExecutePythonCommand",
        "parameters": {
            "PythonCommand": test_code
        }
    }
    
    response = requests.put(BASE_URL, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"    ✓ SUCCESS!")
        print(f"    Response: {json.dumps(result, indent=2)}")
        print(f"\n{'='*80}")
        print(f"WORKING PATH: {path}")
        print('='*80)
        break
    else:
        error = response.json() if response.headers.get('content-type') == 'application/json' else response.text
        if isinstance(error, dict):
            print(f"    ✗ Error: {error.get('errorMessage', error)}")
        else:
            print(f"    ✗ Error: {error[:150]}")

# Also try to describe the object to see if it's accessible
print(f"\n{'='*80}")
print("TRYING TO DESCRIBE PythonScriptLibrary")
print('='*80)

for path in python_paths:
    response = requests.put("http://localhost:30010/remote/object/describe", json={"objectPath": path})
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ {path} is accessible!")
        funcs = result.get('Functions', [])
        exec_func = [f for f in funcs if 'Execute' in f['Name']]
        if exec_func:
            print(f"  Found ExecutePython functions: {[f['Name'] for f in exec_func]}")
        break
    else:
        print(f"✗ {path} - {response.status_code}")
