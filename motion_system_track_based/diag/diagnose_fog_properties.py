"""
Diagnostic script to discover ExponentialHeightFog properties
Run via Remote Control API
"""

import requests
import json

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

diagnostic_code = """
import unreal

# Get or create ExponentialHeightFog
fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
    unreal.EditorLevelLibrary.get_editor_world(),
    unreal.ExponentialHeightFog
)

if fog_actors:
    fog_actor = fog_actors[0]
    print(f"Found fog actor: {fog_actor.get_name()}")
else:
    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0, 0, 0)
    )
    print(f"Created fog actor: {fog_actor.get_name()}")

# Get component
fog_comp = fog_actor.component

print(f"\\n=== ExponentialHeightFogComponent Properties ===")
print(f"Type: {type(fog_comp)}")

# Test specific properties we need
print(f"\\n=== Testing atmosphere properties ===")
test_props = [
    'fog_density', 
    'fog_height_falloff',
    'fog_max_opacity',
    'start_distance',
    'fog_inscattering_color',
    'volumetric_fog',
    'volumetric_fog_scattering_distribution',
    'volumetric_fog_albedo'
]

for prop_name in test_props:
    try:
        value = fog_comp.get_editor_property(prop_name)
        print(f"  OK {prop_name}: {value}")
    except Exception as e:
        print(f"  FAIL {prop_name}: {str(e)}")
"""

payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": diagnostic_code}
}

print("=== Running Fog Property Diagnostic in Unreal ===")
response = requests.put(REMOTE_CONTROL_URL, json=payload, timeout=30)
result = response.json()
print(f"\nResult: {result}")
