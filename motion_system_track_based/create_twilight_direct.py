"""
Direct Twilight Setup - Standalone script
Creates twilight atmosphere directly in Unreal without motion system
"""
import unreal

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\twilight_setup.txt"

def log(msg):
    print(msg)
    with open(output_file, 'a') as f:
        f.write(msg + '\n')

with open(output_file, 'w') as f:
    f.write("=== TWILIGHT SETUP ===\n\n")

# 1. Delete existing fog
log("Cleaning up old fog...")
fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
    unreal.EditorLevelLibrary.get_editor_world(),
    unreal.ExponentialHeightFog
)
for fog_actor in fog_actors:
    unreal.EditorLevelLibrary.destroy_actor(fog_actor)
    log(f"  Deleted: {fog_actor.get_actor_label()}")

# 2. Create new fog
log("\nSetting up fog...")
fog = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.ExponentialHeightFog,
    unreal.Vector(0, 0, 0)
)
fog.set_actor_label("TwilightFog")
log(f"  Created new fog: {fog.get_name()}")

fog_comp = fog.component

# Reddish clouds with silver lining effect - MUCH denser for visibility
fog_comp.set_editor_property("fog_density", 0.2)
fog_comp.set_editor_property("fog_height_falloff", 0.05)
fog_comp.set_editor_property("fog_max_opacity", 1.0)
fog_comp.set_editor_property("start_distance", 0.0)
# Warm reddish-orange for cloud color
fog_comp.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(1.0, 0.4, 0.3))
fog_comp.set_editor_property("volumetric_fog_scattering_distribution", 3.0)
# Brighter albedo for silver lining effect
fog_comp.set_editor_property("volumetric_fog_albedo", unreal.Color(r=255, g=245, b=235))

log(f"  ✓ Fog configured (DENSE reddish with silver highlights)")
log(f"    Density: {fog_comp.get_editor_property('fog_density')}")
log(f"    Height Falloff: {fog_comp.get_editor_property('fog_height_falloff')}")

# 3. Delete existing directional lights
log("\nCleaning up old lights...")
old_lights = unreal.GameplayStatics.get_all_actors_of_class(
    unreal.EditorLevelLibrary.get_editor_world(),
    unreal.DirectionalLight
)
for light in old_lights:
    unreal.EditorLevelLibrary.destroy_actor(light)
    log(f"  Deleted DirectionalLight: {light.get_actor_label()}")

# Delete existing sky lights
old_sky_lights = unreal.GameplayStatics.get_all_actors_of_class(
    unreal.EditorLevelLibrary.get_editor_world(),
    unreal.SkyLight
)
for light in old_sky_lights:
    unreal.EditorLevelLibrary.destroy_actor(light)
    log(f"  Deleted SkyLight: {light.get_actor_label()}")

# 4. Create Twilight Sun (fading, near horizon)
log("\nSetting up twilight sun...")
sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.DirectionalLight,
    unreal.Vector(0, 0, 400)
)
sun.set_actor_label("TwilightSun")
sun.set_actor_rotation(unreal.Rotator(pitch=-5, yaw=180, roll=0), False)

sun_comp = sun.light_component
sun_comp.set_intensity(8.0)
sun_comp.set_light_color(unreal.LinearColor(r=1.0, g=0.7, b=0.4))
sun_comp.set_cast_shadows(True)
sun_comp.set_editor_property("atmosphere_sun_light", True)
sun_comp.set_editor_property("cast_volumetric_shadow", True)

# Light shafts
try:
    sun_comp.set_editor_property("enable_light_shaft_bloom", True)
    sun_comp.set_editor_property("light_shaft_bloom_scale", 0.4)
    sun_comp.set_editor_property("enable_light_shaft_occlusion", True)
    log(f"  ✓ Sun created with light shafts")
except Exception as e:
    log(f"  ✓ Sun created (light shafts: {e})")

# 6. Verify settings
log("\n=== VERIFICATION ===")
log(f"Fog Color: {fog_comp.get_editor_property('fog_inscattering_luminance')}")
log(f"Sun Rotation: {sun.get_actor_rotation()}")
log(f"Sun Color: {sun_comp.get_light_color()}")
log(f"Sun Intensity: {sun_comp.get_editor_property('intensity')}")

log("\n✓ TWILIGHT SETUP COMPLETE")
unreal.log("Twilight atmosphere created - check twilight_setup.txt")
