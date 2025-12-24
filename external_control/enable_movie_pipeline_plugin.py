"""
Enable Movie Render Queue Plugin
"""
import requests
import json

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

def execute_python_command(command):
    """Execute Python command in Unreal via Remote Control"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": command}
    }
    response = requests.put(REMOTE_CONTROL_URL, headers={'Content-Type': 'application/json'}, json=payload)
    result = response.json()
    return result.get('ReturnValue', result)

# Check plugin status
print("Checking Movie Render Queue plugin status...")
result = execute_python_command("""
import unreal

# Try to list all plugins
try:
    # Get plugin manager (if available)
    plugins = [p for p in dir(unreal) if 'plugin' in p.lower()]
    f"Found plugin-related: {plugins}"
except Exception as e:
    f"Error: {e}"
""")
print(f"Plugin check: {result}")

print("\nNote: The Movie Render Queue plugin must be enabled in:")
print("  Edit > Plugins > Search for 'Movie Render Queue' > Enable")
print("  Then restart Unreal Editor")
