"""
Quick diagnostic to discover ExponentialHeightFog properties
"""
import unreal
import os

# Output file
output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\fog_diagnostic_results.txt"

def log(msg):
    print(msg)
    with open(output_file, 'a') as f:
        f.write(msg + '\n')

# Clear file
with open(output_file, 'w') as f:
    f.write("=== FOG DIAGNOSTIC RESULTS ===\n\n")

# Get or create fog
fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
    unreal.EditorLevelLibrary.get_editor_world(),
    unreal.ExponentialHeightFog
)

if fog_actors:
    fog_actor = fog_actors[0]
    log(f"Found fog: {fog_actor.get_name()}")
else:
    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0, 0, 0)
    )
    log(f"Created fog: {fog_actor.get_name()}")

fog_comp = fog_actor.component

log("\n=== ALL Volumetric Properties ===")
all_props = dir(fog_comp)
volumetric_props = [p for p in all_props if 'volumetric' in p.lower() and not p.startswith('_')]
for prop in sorted(volumetric_props):
    try:
        val = fog_comp.get_editor_property(prop)
        log(f"  ✓ {prop}: {val}")
    except:
        log(f"  ? {prop}: (method or unavailable)")

log("\n=== Testing Atmosphere Properties ===")
test_props = [
    'fog_density', 
    'fog_height_falloff',
    'fog_max_opacity',
    'start_distance',
    'fog_inscattering_color',
    'inscattering_color_cubemap',
    'fog_inscattering_luminance',
    'volumetric_fog',
    'volumetric_fog_enable',
    'volumetric_fog_scattering_distribution',
    'volumetric_fog_albedo'
]

for prop in test_props:
    try:
        val = fog_comp.get_editor_property(prop)
        log(f"  ✓ {prop}: {val}")
    except Exception as e:
        log(f"  ✗ {prop}: {e}")

log("\n=== Setting Test ===")
try:
    # Test setting color
    test_color = unreal.LinearColor(0.5, 1.0, 0.7, 1.0)
    fog_comp.set_editor_property("fog_inscattering_color", test_color)
    log(f"  ✓ Color set successfully")
    
    # Test setting density
    fog_comp.set_editor_property("fog_density", 0.05)
    log(f"  ✓ Density set successfully")
    
    # Test volumetric
    fog_comp.set_editor_property("volumetric_fog", True)
    log(f"  ✓ Volumetric enabled successfully")
except Exception as e:
    log(f"  ✗ Setting failed: {e}")

log(f"\n=== Results written to: {output_file} ===")
unreal.log(f"Diagnostic complete - results in {output_file}")
