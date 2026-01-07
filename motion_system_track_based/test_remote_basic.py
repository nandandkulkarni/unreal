
import requests
import json

RC_URL = "http://localhost:30010/remote/object/call"

script = "print('HELLO FROM REMOTE CALL')"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script}
}
response = requests.put(RC_URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Body: {json.dumps(response.json(), indent=2)}")
