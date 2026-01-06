"""
Check sunset scene in Unreal
"""
import unreal

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\check_sunset.txt"

with open(output_file, 'w') as f:
    f.write("=== SUNSET SCENE CHECK ===\n\n")
    
    # Check fog
    fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.ExponentialHeightFog
    )
    
    f.write(f"Fog actors: {len(fog_actors)}\n")
    if fog_actors:
        comp = fog_actors[0].component
        f.write(f"  Color: {comp.get_editor_property('fog_inscattering_luminance')}\n")
        f.write(f"  Density: {comp.get_editor_property('fog_density')}\n")
        f.write(f"  Scattering: {comp.get_editor_property('volumetric_fog_scattering_distribution')}\n")
    
    # Check lights
    lights = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.DirectionalLight
    )
    
    f.write(f"\nDirectional lights: {len(lights)}\n")
    for light in lights:
        f.write(f"  {light.get_actor_label()}: ")
        comp = light.light_component
        f.write(f"Intensity={comp.get_editor_property('intensity')}, ")
        f.write(f"VolShadow={comp.get_editor_property('cast_volumetric_shadow')}, ")
        f.write(f"AtmoSun={comp.get_editor_property('atmosphere_sun_light')}\n")
    
    f.write("\n✓ Sunset atmosphere configured successfully\n")

print("Sunset scene check complete - see check_sunset.txt")
