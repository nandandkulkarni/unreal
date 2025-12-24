import requests

diag_script = """
import unreal
# Spawn Belica with zero rotation
loc = unreal.Vector(0, 0, 0)
rot = unreal.Rotator(0, 0, 0)
actor_name = "Bella_Diag"

skeletal_mesh = unreal.load_object(None, "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica")
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, rot)
actor.set_actor_label(actor_name)
actor.skeletal_mesh_component.set_skeletal_mesh(skeletal_mesh)

forward = actor.get_actor_forward_vector()
right = actor.get_actor_right_vector()
up = actor.get_actor_up_vector()

print(f"DIAG_BELLA_ZERO_ROT: FWD=({forward.x:.3f}, {forward.y:.3f}, {forward.z:.3f})")
print(f"DIAG_BELLA_ZERO_ROT: RGT=({right.x:.3f}, {right.y:.3f}, {right.z:.3f})")
print(f"DIAG_BELLA_ZERO_ROT: UP=({up.x:.3f}, {up.y:.3f}, {up.z:.3f})")

# Cleanup
actor.destroy_actor()
"""

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": diag_script}
}

response = requests.put("http://localhost:30010/remote/object/call", json=payload)
print(response.json())
