"""
Check if god rays light exists with proper settings
"""
import unreal

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\check_light.txt"

with open(output_file, 'w') as f:
    f.write("=== CHECKING LIGHTS ===\n\n")
    
    # Check directional lights
    lights = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.DirectionalLight
    )
    
    f.write(f"Found {len(lights)} directional light(s)\n\n")
    
    for light in lights:
        f.write(f"Light: {light.get_name()}\n")
        f.write(f"  Label: {light.get_actor_label()}\n")
        
        comp = light.light_component
        f.write(f"  Intensity: {comp.get_editor_property('intensity')}\n")
        
        # Check volumetric shadow
        try:
            cast_vol = comp.get_editor_property('cast_volumetric_shadow')
            f.write(f"  Cast Volumetric Shadow: {cast_vol}\n")
        except:
            f.write(f"  Cast Volumetric Shadow: (property not accessible)\n")
        
        # Check light shafts
        try:
            bloom = comp.get_editor_property('enable_light_shaft_bloom')
            bloom_scale = comp.get_editor_property('light_shaft_bloom_scale')
            f.write(f"  Light Shaft Bloom: {bloom}\n")
            f.write(f"  Light Shaft Bloom Scale: {bloom_scale}\n")
        except:
            f.write(f"  Light Shaft properties: (not accessible)\n")
        
        # Check atmospheric sun
        try:
            atmo_sun = comp.get_editor_property('atmosphere_sun_light')
            f.write(f"  Atmosphere Sun Light: {atmo_sun}\n")
        except:
            f.write(f"  Atmosphere Sun Light: (not accessible)\n")
        
        f.write("\n")

print("Check complete - see check_light.txt")
