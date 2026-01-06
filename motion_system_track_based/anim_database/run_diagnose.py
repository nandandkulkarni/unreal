"""
Run Belica Diagnostic Script
"""
import requests

# Read the diagnostic script
with open(r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\diagnose_belica.py", 'r', encoding='utf-8') as f:
    script_content = f.read()

# Execute via Remote Control
url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("Running Belica diagnostic in Unreal...")
response = requests.put(url, json=payload, timeout=30)

if response.status_code == 200:
    print("\n✓ Diagnostic complete! Check Unreal Output Log for results.")
else:
    print(f"\n✗ Error: HTTP {response.status_code}")
    print(response.text)
