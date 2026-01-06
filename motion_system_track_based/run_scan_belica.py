"""
Run Belica Animation Scanner in Unreal
"""
import requests

# Read the scanner script
with open(r"C:\UnrealProjects\coding\unreal\motion_system_track_based\scan_belica_anims.py", 'r', encoding='utf-8') as f:
    script_content = f.read()

# Execute via Remote Control
url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("Scanning Belica animations in Unreal...")
response = requests.put(url, json=payload)

if response.status_code == 200:
    print("✓ Scan complete! Check: belica_anim_database.json")
else:
    print(f"✗ Error: HTTP {response.status_code}")
    print(response.text)
