"""
Read back all twilight atmosphere settings from Unreal
"""
import unreal

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\verify_twilight.txt"

with open(output_file, 'w') as f:
    f.write("=== TWILIGHT ATMOSPHERE VERIFICATION ===\n\n")
    
    # Check fog settings
    f.write("FOG SETTINGS:\n")
    fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.ExponentialHeightFog
    )
    
    if fog_actors:
        comp = fog_actors[0].component
        f.write(f"  Density: {comp.get_editor_property('fog_density')}\n")
        f.write(f"  Height Falloff: {comp.get_editor_property('fog_height_falloff')}\n")
        f.write(f"  Max Opacity: {comp.get_editor_property('fog_max_opacity')}\n")
        f.write(f"  Start Distance: {comp.get_editor_property('start_distance')}\n")
        f.write(f"  Inscattering Color: {comp.get_editor_property('fog_inscattering_luminance')}\n")
        f.write(f"  Volumetric Scattering: {comp.get_editor_property('volumetric_fog_scattering_distribution')}\n")
        f.write(f"  Volumetric Albedo: {comp.get_editor_property('volumetric_fog_albedo')}\n")
    else:
        f.write("  NO FOG FOUND\n")
    
    # Check all lights
    f.write("\nLIGHT SETTINGS:\n")
    lights = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.DirectionalLight
    )
    
    f.write(f"  Found {len(lights)} directional light(s)\n\n")
    
    for light in lights:
        f.write(f"  Light: {light.get_actor_label()}\n")
        rot = light.get_actor_rotation()
        f.write(f"    Rotation: Pitch={rot.pitch:.2f}, Yaw={rot.yaw:.2f}, Roll={rot.roll:.2f}\n")
        
        comp = light.light_component
        f.write(f"    Intensity: {comp.get_editor_property('intensity')}\n")
        
        try:
            color = comp.get_light_color()
            f.write(f"    Color: R={color.r:.2f}, G={color.g:.2f}, B={color.b:.2f}\n")
        except:
            f.write(f"    Color: (not readable)\n")
        
        f.write(f"    Cast Shadows: {comp.get_editor_property('cast_shadows')}\n")
        f.write(f"    Atmosphere Sun: {comp.get_editor_property('atmosphere_sun_light')}\n")
        f.write(f"    Cast Volumetric Shadow: {comp.get_editor_property('cast_volumetric_shadow')}\n")
        
        try:
            bloom_enabled = comp.get_editor_property('enable_light_shaft_bloom')
            f.write(f"    Light Shaft Bloom Enabled: {bloom_enabled}\n")
        except:
            pass
        
        try:
            bloom_scale = comp.get_editor_property('light_shaft_bloom_scale')
            f.write(f"    Light Shaft Bloom Scale: {bloom_scale}\n")
        except:
            pass
        
        f.write("\n")
    
    f.write("=== VERIFICATION COMPLETE ===\n")

print("Verification complete - see verify_twilight.txt")
