import requests

diag_script = """
import unreal
rot1 = unreal.Rotator(0, -90, 0)
print(f"DIAG_ROT1: P={rot1.pitch}, Y={rot1.yaw}, R={rot1.roll}")

rot2 = unreal.Rotator(pitch=0, yaw=-90, roll=0)
print(f"DIAG_ROT2: P={rot2.pitch}, Y={rot2.yaw}, R={rot2.roll}")

# Create Bella and check her internal rotation
loc = unreal.Vector(0, 0, 0)
rot = unreal.Rotator(0, -90, 0)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, rot)
actual_rot = actor.get_actor_rotation()
print(f"DIAG_BELLA_ACTUAL: P={actual_rot.pitch}, Y={actual_rot.yaw}, R={actual_rot.roll}")
actor.destroy_actor()
"""

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": diag_script}
}

response = requests.put("http://localhost:30010/remote/object/call", json=payload)
print(response.json())
