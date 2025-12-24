import requests

diag_script = """
import unreal
rot = unreal.Rotator(pitch=0, yaw=90, roll=0)
loc = unreal.Vector(0, 0, 0)
# Spawn an actor and check its forward vs world Y
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, loc, rot)
fwd = actor.get_actor_forward_vector()
print(f"YAW_90_FORWARD: ({fwd.x:.3f}, {fwd.y:.3f}, {fwd.z:.3f})")
actor.destroy_actor()
"""

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": diag_script}
}

response = requests.put("http://localhost:30010/remote/object/call", json=payload)
print(response.json())
