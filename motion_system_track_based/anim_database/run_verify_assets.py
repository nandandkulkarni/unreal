"""
Run verification script
"""
import requests

script_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\verify_assets.py"
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("Verifying assets...")
response = requests.put(url, json=payload, timeout=30)

if response.status_code == 200:
    print("\n✓ Verification complete!")
    print("  Output: anim_database/verify_assets_output.txt")
else:
    print(f"\n✗ Error: HTTP {response.status_code}")
