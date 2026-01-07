"""
Run Find Pose Search DB
"""
import requests

script_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\find_pose_search_db.py"
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("Searching for PoseSearchDatabase assets...")
response = requests.put(url, json=payload, timeout=30)

if response.status_code == 200:
    print("\nSearch complete!")
else:
    print(f"\nError: HTTP {response.status_code}")
