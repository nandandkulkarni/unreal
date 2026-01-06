"""
Enumerate ExponentialHeightFogComponent properties
Run this in Unreal to see all available properties
"""
import requests

script = """
import unreal

# Get or create fog actor
fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
    unreal.EditorLevelLibrary.get_editor_world(),
    unreal.ExponentialHeightFog
)

if fog_actors:
    fog_actor = fog_actors[0]
else:
    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0, 0, 0)
    )

fog_component = fog_actor.component

print("\\n" + "="*60)
print("ExponentialHeightFogComponent Properties")
print("="*60)

# Get all properties
props = dir(fog_component)
fog_props = [p for p in props if 'fog' in p.lower() or 'volumetric' in p.lower() or 'inscatter' in p.lower()]

for prop in sorted(fog_props):
    if not prop.startswith('_'):
        try:
            value = getattr(fog_component, prop)
            if not callable(value):
                print(f"{prop}: {value}")
        except:
            print(f"{prop}: <error reading>")

print("="*60)
"""

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script}
}

response = requests.put(REMOTE_CONTROL_URL, json=payload, timeout=10)
print(response.json())
