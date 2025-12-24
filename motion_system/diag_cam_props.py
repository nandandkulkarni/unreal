import requests

diag_script = """
import unreal
cam = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector())
comp = cam.get_cine_camera_component()
# Get all property names
names = comp.get_editor_property_names()
filtered = [n for n in names if 'look' in n.lower() or 'track' in n.lower()]
print(f"DIAG_PROPS: {','.join(filtered)}")
cam.destroy_actor()
"""

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": diag_script}
}

response = requests.put("http://localhost:30010/remote/object/call", json=payload)
print(response.json())
