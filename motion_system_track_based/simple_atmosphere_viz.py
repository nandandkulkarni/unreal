"""
Simple atmosphere visualization test - bypassing motion system completely
"""
import unreal

print("Setting up dense twilight atmosphere...")

# Delete old fog and lights
world = unreal.EditorLevelLibrary.get_editor_world()

# Delete existing fog
fog_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ExponentialHeightFog)
for fog in fog_actors:
    unreal.EditorLevelLibrary.destroy_actor(fog)
    print(f"Deleted old fog: {fog.get_name()}")

# Delete existing directional lights
lights = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.DirectionalLight)
for light in lights:
    if "Sun" in light.get_actor_label() or "Atmospheric" in light.get_actor_label():
        unreal.EditorLevelLibrary.destroy_actor(light)
        print(f"Deleted old light: {light.get_name()}")

# Create dense fog
fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.ExponentialHeightFog,
    unreal.Vector(0, 0, 0)
)
fog_actor.set_actor_label("TwilightFog")
fog_component = fog_actor.component

# Dense reddish fog
fog_component.set_editor_property("fog_density", 0.2)
fog_component.set_editor_property("fog_height_falloff", 0.05)
fog_component.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(1.0, 0.4, 0.3))
fog_component.set_editor_property("fog_max_opacity", 1.0)

# Volumetric settings
fog_component.set_editor_property("volumetric_fog_scattering_distribution", 2.0)
fog_component.set_editor_property("volumetric_fog_albedo", unreal.Color(r=255, g=245, b=235))

print(f"✓ Created fog with density 0.2 (very dense reddish clouds)")

# Create sun at horizon
sun_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.DirectionalLight,
    unreal.Vector(0, 0, 500)
)
sun_light.set_actor_label("AtmosphericSun")
sun_light.set_actor_rotation(unreal.Rotator(pitch=-5, yaw=180, roll=0))

light_comp = sun_light.light_component
light_comp.set_intensity(8.0)
light_comp.set_light_color(unreal.LinearColor(1.0, 0.7, 0.4))
light_comp.set_editor_property("atmosphere_sun_light", True)
light_comp.set_editor_property("cast_volumetric_shadow", True)

print(f"✓ Created sun light at horizon")
print("")
print("=" * 60)
print("TWILIGHT ATMOSPHERE COMPLETE")
print("=" * 60)
print("Dense reddish fog should be VERY visible in viewport")
print("If you don't see clouds:")
print("  1. Make sure viewport is in 'Lit' mode (not Wireframe)")
print("  2. Look around - fog is everywhere")
print("  3. Try moving camera back from origin")
print("=" * 60)
