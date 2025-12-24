import requests
import json

url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {
        "PythonCommand": "exec(open(r'C:/UnrealProjects/Coding/unreal/tools/list_sequences.py').read())"
    }
}

response = requests.put(url, headers={"Content-Type": "application/json"}, json=payload)
result = response.json()
print(result.get('ReturnValue', result))
