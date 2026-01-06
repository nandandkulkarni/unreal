"""
Trigger script to run animation loader in Unreal
"""
import requests
import sys

# Read the loader script
script_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\load_and_save_anims.py"
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

# Execute via Remote Control
url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("=" * 60)
print("LOADING BELICA ANIMATIONS FROM UNREAL")
print("=" * 60)

try:
    response = requests.put(url, json=payload, timeout=30)
    
    if response.status_code == 200:
        print("\n✓ Animation database updated!")
        print("  File: motion_structs/belica_anims.jsonx")
        sys.exit(0)
    else:
        print(f"\n✗ Error: HTTP {response.status_code}")
        print(response.text)
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
