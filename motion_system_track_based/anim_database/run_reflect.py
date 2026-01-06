"""
Run AnimSequence API Reflection
"""
import requests

# Read the reflection script
with open(r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\reflect_animsequence.py", 'r', encoding='utf-8') as f:
    script_content = f.read()

# Execute via Remote Control
url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("Running AnimSequence API reflection in Unreal...")
response = requests.put(url, json=payload, timeout=30)

if response.status_code == 200:
    print("\n✓ Reflection complete!")
    print("  Check: anim_database/animsequence_api_reflection.txt")
else:
    print(f"\n✗ Error: HTTP {response.status_code}")
    print(response.text)
