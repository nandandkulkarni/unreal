"""
Run Check PSZ Lib
"""
import requests

script_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\check_psz_lib.py"
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("Checking PoseSearchLibrary...")
response = requests.put(url, json=payload, timeout=30)
if response.status_code == 200:
    for line in response.json()['Output']:
        print(line['Message'])
else:
    print(f"Error: {response.status_code}")
