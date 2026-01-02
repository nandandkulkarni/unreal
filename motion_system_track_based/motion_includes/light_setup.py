"""
Directional light creation and configuration
"""
import unreal
import logger
from logger import log, log_header


# Cardinal direction to yaw mapping
CARDINAL_DIRECTIONS = {
    "north": 0,
    "north_east": 45,
    "east": 90,
    "south_east": 135,
    "south": 180,
    "south_west": -135,
    "west": -90,
    "north_west": -45
}

# Angle presets to pitch mapping
ANGLE_PRESETS = {
    "horizon": -5,
    "low": -15,
    "low_high": -25,
    "medium": -45,
    "medium_high": -60,
    "high": -75,
    "very_high": -85,
    "overhead": -90
}

# Intensity presets
INTENSITY_PRESETS = {
    "very_dim": 2.0,
    "dim": 4.0,
    "soft": 6.0,
    "moderate": 8.0,
    "normal": 10.0,
    "bright": 12.0,
    "very_bright": 14.0,
    "intense": 16.0,
    "extreme": 18.0
}

# Color presets (RGB 0-255)
COLOR_PRESETS = {
    "deep_sunset": (255, 153, 77),
    "sunset": (255, 179, 128),
    "golden": (255, 217, 179),
    "warm_white": (255, 242, 230),
    "white": (255, 255, 255),
    "cool_white": (242, 242, 255),
    "overcast": (204, 217, 255),
    "moonlight": (153, 179, 255)
}


def get_cardinal_yaw(direction):
    """Convert cardinal direction string to yaw angle"""
    return CARDINAL_DIRECTIONS.get(direction.lower(), 0)


def get_angle_pitch(angle_preset):
    """Convert angle preset string to pitch value"""
    return ANGLE_PRESETS.get(angle_preset.lower(), -45)


def get_intensity_value(intensity):
    """Convert intensity preset or return numeric value"""
    if isinstance(intensity, str):
        return INTENSITY_PRESETS.get(intensity.lower(), 10.0)
    return float(intensity)


def get_color_value(color):
    """Convert color preset to unreal.Color or parse RGB array"""
    if isinstance(color, str):
        rgb = COLOR_PRESETS.get(color.lower(), (255, 255, 255))
        return unreal.Color(r=rgb[0], g=rgb[1], b=rgb[2])
    elif isinstance(color, (list, tuple)) and len(color) >= 3:
        # Convert 0-1 float to 0-255 int if needed
        if all(isinstance(c, float) and 0 <= c <= 1 for c in color[:3]):
            return unreal.Color(r=int(color[0]*255), g=int(color[1]*255), b=int(color[2]*255))
        else:
            return unreal.Color(r=int(color[0]), g=int(color[1]), b=int(color[2]))
    return unreal.Color(r=255, g=255, b=255)


def create_directional_light(name, from_direction, angle, direction_offset=0, angle_offset=0,
                            intensity="normal", color="white", cast_shadows=True, 
                            atmosphere_sun=True, location=None):
    """
    Create a directional light with specified properties
    
    Args:
        name: Actor label
        from_direction: Cardinal direction (e.g., "west", "north_east")
        angle: Angle preset (e.g., "low", "medium", "overhead")
        direction_offset: Yaw offset in degrees (optional)
        angle_offset: Pitch offset in degrees (optional)
        intensity: Intensity preset or numeric value
        color: Color preset or RGB array
        cast_shadows: Whether to cast shadows
        atmosphere_sun: Whether to interact with atmosphere
        location: Optional location override
        
    Returns:
        DirectionalLight actor
    """
    log_header(f"Creating Directional Light: {name}")
    
    # Calculate rotation
    yaw = get_cardinal_yaw(from_direction) + direction_offset
    pitch = get_angle_pitch(angle) + angle_offset
    rotation = unreal.Rotator(pitch=pitch, yaw=yaw, roll=0)
    
    # Default location (high up for visibility)
    if location is None:
        location = unreal.Vector(0, 0, 1000)
    
    # Spawn the light
    light_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        location,
        rotation
    )
    
    if not light_actor:
        log("✗ Failed to create directional light")
        return None
    
    # Set label
    light_actor.set_actor_label(name)
    light_actor.tags.append("MotionSystemActor")
    
    # Get light component
    light_component = light_actor.light_component
    
    # Set properties
    intensity_value = get_intensity_value(intensity)
    color_value = get_color_value(color)
    
    light_component.set_editor_property("intensity", intensity_value)
    light_component.set_editor_property("light_color", color_value)
    light_component.set_editor_property("cast_shadows", cast_shadows)
    light_component.set_editor_property("atmosphere_sun_light", atmosphere_sun)
    light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    
    log(f"✓ Directional light '{name}' created")
    log(f"  Shadows: {cast_shadows}, Atmosphere: {atmosphere_sun}")
    
    return light_actor


def create_rect_light(name, location, rotation, intensity="bright", 
                     width=100, height=100, barn_door_angle=90, barn_door_length=20,
                     color="white", cast_shadows=False):
    """
    Create a RectLight (Area Light)
    """
    log_header(f"Creating Rect Light: {name}")
    
    # Spawn
    light_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.RectLight,
        location,
        rotation
    )
    
    if not light_actor:
        log("✗ Failed to create rect light")
        return None
        
    light_actor.set_actor_label(name)
    light_actor.tags.append("MotionSystemActor")
    
    # Properties
    comp = light_actor.light_component
    intensity_value = get_intensity_value(intensity) * 100 # Rect lights need higher values usually? or use cd
    # Actually Intensity Units default to cd (Candelas) for RectLights in 5.x usually.
    # Our presets are simple (10.0). 10 cd is nothing. 
    # Directional uses Lux (approx). Point/Spot/Rect use Candelas or Lumens.
    # 10.0 directional ~ 100,000 lux? No, directional is unitless or lux depending on settings.
    # Let's assume we need to boost it.
    
    comp.set_editor_property("intensity", intensity_value * 500) # Boost for non-directional
    comp.set_editor_property("light_color", get_color_value(color))
    comp.set_editor_property("cast_shadows", cast_shadows)
    comp.set_editor_property("source_width", width)
    comp.set_editor_property("source_height", height)
    comp.set_editor_property("barn_door_angle", barn_door_angle)
    comp.set_editor_property("barn_door_length", barn_door_length)
    comp.set_mobility(unreal.ComponentMobility.MOVABLE)
    
    log(f"✓ Rect light '{name}' created")
    return light_actor
