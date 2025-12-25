import requests

diag_script = """
import unreal
rot = unreal.Rotator(11, 22, 33)
print(f"ORDER_CHECK: A=11, B=22, C=33 -> P={rot.pitch}, Y={rot.yaw}, R={rot.roll}")

# Also check Camera move logic
cam_rot = unreal.Rotator(rot[0], rot[1], rot[2])
"""

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": diag_script}
}

response = requests.put("http://localhost:30010/remote/object/call", json=payload)
print(response.json())
