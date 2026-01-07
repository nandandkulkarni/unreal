"""
Run Scan for Manny Unarmed
"""
import requests

script_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\scan_manny_unarmed.py"
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("Scanning Manny Unarmed animations...")
response = requests.put(url, json=payload, timeout=30)

if response.status_code == 200:
    print("\nScan complete!")
else:
    print(f"\nError: HTTP {response.status_code}")
