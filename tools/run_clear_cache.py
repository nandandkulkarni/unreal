import requests

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": "exec(open(r'C:/UnrealProjects/Coding/unreal/tools/clear_python_cache.py').read())"}
}

response = requests.put("http://localhost:30010/remote/object/call", json=payload)
print(response.json())
