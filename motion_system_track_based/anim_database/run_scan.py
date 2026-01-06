"""
Trigger Belica Animation Scanner in Unreal Engine

Executes the scan_belica.py script inside Unreal via Remote Control API.
"""
import requests
import os
import sys

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Read the scanner script
scanner_path = os.path.join(script_dir, "scan_belica.py")
with open(scanner_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

# Execute via Remote Control
url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

print("=" * 60)
print("SCANNING BELICA ANIMATIONS IN UNREAL")
print("=" * 60)

try:
    response = requests.put(url, json=payload, timeout=30)
    
    if response.status_code == 200:
        print("\n✓ Scan complete!")
        print(f"  Database: {script_dir}\\belica_animations.json")
        sys.exit(0)
    else:
        print(f"\n✗ Error: HTTP {response.status_code}")
        print(response.text)
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
