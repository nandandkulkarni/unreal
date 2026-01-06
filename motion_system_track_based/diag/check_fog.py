"""
Check if fog exists in level
"""
import unreal

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\check_fog.txt"

with open(output_file, 'w') as f:
    f.write("=== CHECKING FOR FOG ===\n\n")
    
    fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.ExponentialHeightFog
    )
    
    f.write(f"Found {len(fog_actors)} fog actor(s)\n\n")
    
    for fog in fog_actors:
        f.write(f"Fog: {fog.get_name()}\n")
        f.write(f"  Label: {fog.get_actor_label()}\n")
        comp = fog.component
        f.write(f"  Density: {comp.get_editor_property('fog_density')}\n")
        f.write(f"  Color: {comp.get_editor_property('fog_inscattering_luminance')}\n")
        f.write("\n")

print("Check complete - see check_fog.txt")
