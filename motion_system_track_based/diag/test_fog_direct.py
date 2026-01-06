"""
Direct fog test - run via run_remote.py
"""
import unreal
import os

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\fog_test_results.txt"

def log(msg):
    print(msg)
    with open(output_file, 'a') as f:
        f.write(msg + '\n')

with open(output_file, 'w') as f:
    f.write("=== FOG TEST RESULTS ===\n\n")

# Create fog
fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
    unreal.EditorLevelLibrary.get_editor_world(),
    unreal.ExponentialHeightFog
)

if fog_actors:
    fog_actor = fog_actors[0]
    log(f"Found existing fog: {fog_actor.get_name()}")
else:
    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0, 0, 0)
    )
    fog_actor.set_actor_label("TestFog")
    fog_actor.tags.append("MotionSystemActor")
    log(f"Created new fog: {fog_actor.get_name()}")

fog_comp = fog_actor.component

# Apply settings
fog_comp.set_editor_property("fog_density", 0.05)
fog_comp.set_editor_property("fog_height_falloff", 0.2)
fog_comp.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.6, 0.7, 1.0))
fog_comp.set_editor_property("fog_max_opacity", 1.0)
fog_comp.set_editor_property("start_distance", 0.0)
fog_comp.set_editor_property("volumetric_fog_scattering_distribution", 1.0)
fog_comp.set_editor_property("volumetric_fog_albedo", unreal.Color(r=230, g=230, b=230))

log("✓ Fog configured successfully")
log(f"  Density: {fog_comp.get_editor_property('fog_density')}")
log(f"  Color: {fog_comp.get_editor_property('fog_inscattering_luminance')}")

# Check if sequence exists
sequence_path = "/Game/Movies/TestSequence/Simple_Fog_Test"
if unreal.EditorAssetLibrary.does_asset_exist(sequence_path):
    log(f"\n✓ Sequence exists: {sequence_path}")
else:
    log(f"\n✗ Sequence not found: {sequence_path}")
    
# List all sequences
all_sequences = unreal.EditorAssetLibrary.list_assets("/Game/Movies/", recursive=True)
sequences = [s for s in all_sequences if "Sequence" in s]
log(f"\nFound {len(sequences)} sequences:")
for seq in sequences[:5]:
    log(f"  {seq}")

log("\n=== TEST COMPLETE ===")
unreal.log("Fog test complete - check fog_test_results.txt")
