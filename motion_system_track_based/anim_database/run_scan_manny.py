"""
Trigger script to run Manny animation scanner in Unreal
"""
import requests

# Read the scanner script
script_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\scan_manny.py"
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
print("SCANNING MANNY ANIMATIONS IN UNREAL")
print("=" * 60)

response = requests.put(url, json=payload, timeout=30)

if response.status_code == 200:
    print("\n✓ Scan complete!")
    print("  Database: anim_database/manny_animations.json")
    print("  Debug log: anim_database/scan_manny_debug.log")
else:
    print(f"\n✗ Error: HTTP {response.status_code}")
    print(response.text)
