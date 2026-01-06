"""
Run animation folder finder
"""
import requests

script_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\find_all_anims.py"
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("Finding all animation folders...")
response = requests.put(url, json=payload, timeout=30)

if response.status_code == 200:
    print("\n✓ Search complete!")
    print("  Check: anim_database/find_anims_output.txt")
else:
    print(f"\n✗ Error: HTTP {response.status_code}")
