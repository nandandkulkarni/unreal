"""
Atmosphere and Volumetric Fog Setup

Creates and configures exponential height fog, volumetric effects, and light shafts.
"""
import unreal
from logger import log, log_header


# Fog density presets
FOG_DENSITY_PRESETS = {
    "clear": 0.005,
    "light": 0.02,
    "medium": 0.05,
    "heavy": 0.1,
    "dense": 0.2
}

# Fog color presets (RGB 0-1)
FOG_COLOR_PRESETS = {
    "atmospheric": (0.85, 0.9, 1.0),
    "warm_haze": (1.0, 0.95, 0.9),
    "cool_white": (0.95, 0.95, 1.0),
    "pollution": (0.9, 0.85, 0.7),
    "mystical": (0.7, 0.8, 1.0),
    "forest": (0.8, 0.9, 0.85)
}

# Light shaft bloom presets
LIGHT_SHAFT_PRESETS = {
    "subtle": 0.1,
    "cinematic": 0.3,
    "dramatic": 0.6
}


def get_fog_density_value(density):
    """Convert fog density preset or return numeric value"""
    if isinstance(density, str):
        return FOG_DENSITY_PRESETS.get(density.lower(), 0.02)
    return float(density)


def get_fog_color_value(color):
    """Convert fog color preset to unreal.LinearColor or parse RGB array"""
    if isinstance(color, str):
        rgb = FOG_COLOR_PRESETS.get(color.lower(), (0.85, 0.9, 1.0))
        return unreal.LinearColor(r=rgb[0], g=rgb[1], b=rgb[2])
    elif isinstance(color, (list, tuple)) and len(color) >= 3:
        return unreal.LinearColor(r=float(color[0]), g=float(color[1]), b=float(color[2]))
    return unreal.LinearColor(r=0.85, g=0.9, b=1.0)


def get_light_shaft_value(preset_or_value):
    """Convert light shaft preset or return numeric value"""
    if isinstance(preset_or_value, str):
        return LIGHT_SHAFT_PRESETS.get(preset_or_value.lower(), 0.3)
    return float(preset_or_value)


def create_exponential_height_fog(fog_density=0.02, fog_height_falloff=0.2, fog_color="atmospheric",
                                  volumetric=True, volumetric_scattering=1.0, start_distance=0,
                                  fog_max_opacity=1.0):
    """
    Create or update exponential height fog in the level
    
    Args:
        fog_density: Density preset or numeric value (default: 0.02)
        fog_height_falloff: Height falloff coefficient (default: 0.2)
        fog_color: Color preset or RGB array (default: "atmospheric")
        volumetric: Enable volumetric fog (default: True)
        volumetric_scattering: Scattering intensity 0-2 (default: 1.0)
        start_distance: Distance where fog starts in cm (default: 0)
        fog_max_opacity: Maximum fog opacity 0-1 (default: 1.0)
        
    Returns:
        ExponentialHeightFog actor
    """
    log_header("Setting up Atmospheric Fog")
    
    # Check if fog already exists
    existing_fog = None
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for actor in all_actors:
        if isinstance(actor, unreal.ExponentialHeightFog):
            existing_fog = actor
            log(f"✓ Found existing ExponentialHeightFog")
            break
    
    # Create new fog if none exists
    if not existing_fog:
        fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.ExponentialHeightFog,
            unreal.Vector(0, 0, 0)
        )
        if not fog_actor:
            log("✗ Failed to create ExponentialHeightFog")
            return None
        log("✓ Created new ExponentialHeightFog")
    else:
        fog_actor = existing_fog
    
    # Tag it as managed by motion system
    if "MotionSystemActor" not in fog_actor.tags:
        fog_actor.tags.append("MotionSystemActor")
    
    # Get fog component
    fog_component = fog_actor.component
    
    # Convert presets to values
    density_value = get_fog_density_value(fog_density)
    color_value = get_fog_color_value(fog_color)
    
    # Set basic fog properties
    fog_component.set_editor_property("fog_density", density_value)
    fog_component.set_editor_property("fog_height_falloff", fog_height_falloff)
    fog_component.set_editor_property("fog_inscattering_color", color_value)
    fog_component.set_editor_property("fog_max_opacity", fog_max_opacity)
    fog_component.set_editor_property("start_distance", start_distance)
    
    # Set volumetric fog properties
    if volumetric:
        fog_component.set_editor_property("volumetric_fog", True)
        fog_component.set_editor_property("volumetric_fog_scattering_distribution", volumetric_scattering)
        
        # Additional volumetric settings for better quality
        fog_component.set_editor_property("volumetric_fog_albedo", unreal.Color(r=255, g=255, b=255))
        fog_component.set_editor_property("volumetric_fog_emissive", unreal.LinearColor(0, 0, 0))
        fog_component.set_editor_property("volumetric_fog_extinction_scale", 1.0)
        
        log(f"✓ Volumetric fog enabled (scattering: {volumetric_scattering})")
    else:
        fog_component.set_editor_property("volumetric_fog", False)
    
    log(f"✓ Fog density: {density_value}")
    log(f"✓ Fog color: {color_value}")
    log(f"✓ Height falloff: {fog_height_falloff}")
    
    return fog_actor


def configure_light_shafts(light_actor, enable_light_shafts=True, bloom_scale=0.3, 
                          bloom_threshold=8.0, occlusion_mask_darkness=0.5):
    """
    Configure light shaft (god rays) settings on a directional light
    
    Args:
        light_actor: DirectionalLight actor
        enable_light_shafts: Enable light shaft bloom (default: True)
        bloom_scale: Light shaft bloom intensity (default: 0.3)
        bloom_threshold: Brightness threshold for bloom (default: 8.0)
        occlusion_mask_darkness: Shadow darkness 0-1 (default: 0.5)
        
    Returns:
        True if successful
    """
    if not light_actor:
        log("✗ No light actor provided for light shaft configuration")
        return False
    
    log_header(f"Configuring Light Shafts: {light_actor.get_actor_label()}")
    
    # Get light component
    light_component = light_actor.light_component
    
    # Convert preset if needed
    bloom_value = get_light_shaft_value(bloom_scale)
    
    # Enable/disable light shafts
    light_component.set_editor_property("enable_light_shaft_bloom", enable_light_shafts)
    
    if enable_light_shafts:
        light_component.set_editor_property("bloom_scale", bloom_value)
        light_component.set_editor_property("bloom_threshold", bloom_threshold)
        light_component.set_editor_property("light_shaft_override_direction", unreal.Vector(0, 0, 0))
        
        # Occlusion settings
        light_component.set_editor_property("occlusion_mask_darkness", occlusion_mask_darkness)
        light_component.set_editor_property("light_shaft_occlusion", True)
        
        log(f"✓ Light shafts enabled")
        log(f"  Bloom scale: {bloom_value}")
        log(f"  Bloom threshold: {bloom_threshold}")
        log(f"  Occlusion darkness: {occlusion_mask_darkness}")
    else:
        log(f"✓ Light shafts disabled")
    
    return True


def enable_volumetric_light_scattering(light_actor, cast_volumetric_shadow=True):
    """
    Enable volumetric scattering on a directional light
    
    Args:
        light_actor: DirectionalLight actor
        cast_volumetric_shadow: Cast shadows in volumetric fog (default: True)
        
    Returns:
        True if successful
    """
    if not light_actor:
        return False
    
    light_component = light_actor.light_component
    
    # Enable volumetric scattering
    light_component.set_editor_property("cast_volumetric_shadow", cast_volumetric_shadow)
    
    log(f"✓ Volumetric shadow casting: {cast_volumetric_shadow}")
    
    return True


def get_fog_actor():
    """
    Find the ExponentialHeightFog actor in the level
    
    Returns:
        ExponentialHeightFog actor or None
    """
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for actor in all_actors:
        if isinstance(actor, unreal.ExponentialHeightFog):
            return actor
    return None


def setup_post_process_for_bloom(intensity=1.0):
    """
    Configure post-process volume for enhanced bloom (god rays)
    
    Args:
        intensity: Bloom intensity multiplier (default: 1.0)
        
    Returns:
        PostProcessVolume actor
    """
    log_header("Setting up Post-Process for Bloom")
    
    # Find or create post-process volume
    existing_pp = None
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for actor in all_actors:
        if isinstance(actor, unreal.PostProcessVolume):
            existing_pp = actor
            break
    
    if not existing_pp:
        pp_volume = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.PostProcessVolume,
            unreal.Vector(0, 0, 0)
        )
        if not pp_volume:
            log("✗ Failed to create PostProcessVolume")
            return None
        log("✓ Created PostProcessVolume")
    else:
        pp_volume = existing_pp
        log("✓ Found existing PostProcessVolume")
    
    # Make it unbound (affects entire level)
    pp_volume.set_editor_property("unbound", True)
    
    # Configure bloom settings
    settings = pp_volume.settings
    settings.set_editor_property("bloom_intensity", intensity)
    settings.set_editor_property("bloom_threshold", 0.8)
    
    log(f"✓ Post-process bloom intensity: {intensity}")
    
    return pp_volume
