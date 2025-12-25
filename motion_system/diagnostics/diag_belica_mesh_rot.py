import requests

diag_script = """
import unreal
loc = unreal.Vector(0, 0, 0)
rot = unreal.Rotator(0, 0, 0)
skeletal_mesh = unreal.load_object(None, "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica")
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, rot)
actor.skeletal_mesh_component.set_skinned_asset_and_update(skeletal_mesh)

rel_rot = actor.skeletal_mesh_component.get_editor_property("relative_rotation")
print(f"DIAG_BELLA_MESH_REL_ROT: P={rel_rot.pitch}, Y={rel_rot.yaw}, R={rel_rot.roll}")

# Check World Rotation of Mesh
comp_rot = actor.skeletal_mesh_component.get_world_rotation()
print(f"DIAG_BELLA_MESH_WORLD_ROT: P={comp_rot.pitch}, Y={comp_rot.yaw}, R={comp_rot.roll}")

actor.destroy_actor()
"""

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": diag_script}
}

response = requests.put("http://localhost:30010/remote/object/call", json=payload)
print(response.json())
