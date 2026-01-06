"""
Test atmosphere settings directly in Unreal
"""
import unreal

# Test applying atmosphere settings
cmd = {
    "fog_density": 0.15,
    "fog_height_falloff": 0.05,
    "fog_color": (1.0, 0.4, 0.3),
    "volumetric": True,
    "volumetric_scattering": 2.0,
    "volumetric_albedo": (1.0, 0.96, 0.92),
    "start_distance": 0,
    "fog_max_opacity": 1.0
}

try:
    print("Testing atmosphere settings...")
    
    # Color presets
    COLOR_PRESETS = {
        "white": (1.0, 1.0, 1.0),
        "gray": (0.5, 0.5, 0.5),
        "blue": (0.6, 0.7, 1.0),
        "mystical": (0.5, 1.0, 0.7),
        "orange": (1.0, 0.6, 0.3),
        "purple": (0.8, 0.4, 1.0),
        "forest": (0.3, 0.8, 0.4),
    }
    
    # Density presets
    DENSITY_PRESETS = {
        "clear": 0.01,
        "light": 0.02,
        "medium": 0.05,
        "heavy": 0.1,
        "dense": 0.2,
    }
    
    # Get or create ExponentialHeightFog
    fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.ExponentialHeightFog
    )
    
    if fog_actors:
        fog_actor = fog_actors[0]
        print(f"Using existing ExponentialHeightFog: {fog_actor.get_name()}")
    else:
        fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.ExponentialHeightFog,
            unreal.Vector(0, 0, 0)
        )
        fog_actor.set_actor_label("_AtmosphereFog")
        fog_actor.tags.append("MotionSystemActor")
        print(f"Created new ExponentialHeightFog actor")
    
    # Get fog component
    fog_component = fog_actor.component
    print(f"Got fog component: {fog_component}")
    
    # Apply fog density
    fog_density = cmd.get("fog_density", 0.02)
    if isinstance(fog_density, str):
        fog_density = DENSITY_PRESETS.get(fog_density, 0.02)
    fog_component.set_editor_property("fog_density", fog_density)
    print(f"Set fog_density to {fog_density}")
    
    # Apply fog color (use fog_inscattering_luminance in UE 5.7)
    fog_color = cmd.get("fog_color", (0.6, 0.7, 1.0))
    if isinstance(fog_color, str):
        fog_color = COLOR_PRESETS.get(fog_color, (0.6, 0.7, 1.0))
    color = unreal.LinearColor(r=fog_color[0], g=fog_color[1], b=fog_color[2])
    fog_component.set_editor_property("fog_inscattering_luminance", color)
    print(f"Set fog_inscattering_luminance to {fog_color}")
    
    # Apply height falloff
    fog_height_falloff = cmd.get("fog_height_falloff", 0.2)
    fog_component.set_editor_property("fog_height_falloff", fog_height_falloff)
    print(f"Set fog_height_falloff to {fog_height_falloff}")
    
    # Apply max opacity
    fog_max_opacity = cmd.get("fog_max_opacity", 1.0)
    fog_component.set_editor_property("fog_max_opacity", fog_max_opacity)
    print(f"Set fog_max_opacity to {fog_max_opacity}")
    
    # Apply start distance
    start_distance = cmd.get("start_distance", 0)
    fog_component.set_editor_property("start_distance", start_distance)
    print(f"Set start_distance to {start_distance}")
    
    # Apply volumetric fog settings
    volumetric = cmd.get("volumetric", False)
    
    if volumetric:
        # Apply volumetric scattering intensity
        volumetric_scattering = cmd.get("volumetric_scattering", 1.0)
        fog_component.set_editor_property("volumetric_fog_scattering_distribution", volumetric_scattering)
        print(f"Set volumetric_fog_scattering_distribution to {volumetric_scattering}")
        
        # Apply volumetric albedo (uses unreal.Color with 0-255 values)
        volumetric_albedo = cmd.get("volumetric_albedo", (0.9, 0.9, 0.9))
        if isinstance(volumetric_albedo, str):
            volumetric_albedo = COLOR_PRESETS.get(volumetric_albedo, (0.9, 0.9, 0.9))
        albedo_color = unreal.Color(
            r=int(volumetric_albedo[0] * 255),
            g=int(volumetric_albedo[1] * 255),
            b=int(volumetric_albedo[2] * 255)
        )
        fog_component.set_editor_property("volumetric_fog_albedo", albedo_color)
        print(f"Set volumetric_fog_albedo to {volumetric_albedo}")
    
    print(f"✓ SUCCESS - All atmosphere settings applied")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
