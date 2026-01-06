"""
Check sun light configuration
"""
import unreal

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\check_sun.txt"

with open(output_file, 'w') as f:
    f.write("=== SUN LIGHT CHECK ===\n\n")
    
    lights = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.DirectionalLight
    )
    
    f.write(f"Found {len(lights)} directional light(s)\n\n")
    
    for light in lights:
        f.write(f"Light: {light.get_actor_label()}\n")
        
        # Get rotation
        rot = light.get_actor_rotation()
        f.write(f"  Rotation: Pitch={rot.pitch}, Yaw={rot.yaw}, Roll={rot.roll}\n")
        
        # Get location
        loc = light.get_actor_location()
        f.write(f"  Location: X={loc.x}, Y={loc.y}, Z={loc.z}\n")
        
        comp = light.light_component
        f.write(f"  Intensity: {comp.get_editor_property('intensity')}\n")
        f.write(f"  Atmosphere Sun: {comp.get_editor_property('atmosphere_sun_light')}\n")
        f.write(f"  Cast Volumetric Shadow: {comp.get_editor_property('cast_volumetric_shadow')}\n")
        
        # Check color
        try:
            color = comp.get_light_color()
            f.write(f"  Color: R={color.r}, G={color.g}, B={color.b}\n")
        except:
            f.write(f"  Color: (not readable)\n")
        
        f.write("\n")

print("Sun check complete - see check_sun.txt")
