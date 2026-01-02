
# Light setup module
import unreal

# import logger
# from logger import log

def log(msg):
    print(msg)

def create_light(name, location, rotation, properties):
    """
    Create and configure a light actor.
    Allowed types: Point, Directional, Spot, Rect, Sky
    """
    light_type = properties.get("light_type", "Point")
    log(f"  Creating Light: {name} ({light_type})")
    
    actor_class = None
    if light_type == "Point":
        actor_class = unreal.PointLight
    elif light_type == "Directional":
        actor_class = unreal.DirectionalLight
    elif light_type == "Spot":
        actor_class = unreal.SpotLight
    elif light_type == "Rect":
        actor_class = unreal.RectLight
    elif light_type == "Sky":
        actor_class = unreal.SkyLight
    else:
        log(f"  ⚠ Unknown light type: {light_type}")
        return None
        
    # Spawn
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class, 
        location, 
        rotation
    )
    
    if not actor:
        log(f"  ✗ Failed to spawn light: {name}")
        return None
        
    actor.set_actor_label(name)
    actor.tags.append("MotionSystemActor")
    
    # Configure Component
    # Most lights have a 'LightComponent' (Point/Spot/Dir/Rect)
    # SkyLight has 'SkyLightComponent'
    
    comp = None
    if light_type == "Sky":
        comp = actor.light_component # Actually SkyLight uses 'light_component' property to access component?
        # Let's check API. usually actor.sky_light_component?
        # fallback
        pass
    else:
        comp = actor.light_component
        
    if comp:
        # Common settings
        intensity = properties.get("intensity", 5000.0)
        color = properties.get("color", [1, 1, 1])
        cast_shadows = properties.get("cast_shadows", True)
        
        # Color (LinearColor)
        lin_color = unreal.LinearColor(color[0], color[1], color[2], 1.0)
        comp.set_light_color(lin_color)
        
        # Intensity
        comp.set_intensity(intensity)
        # TODO: Handle Units if possible (unreal.LightUnits enum)
        
        comp.set_cast_shadows(cast_shadows)
        
        # Specifics
        if light_type == "Point" or light_type == "Spot":
            radius = properties.get("radius", 1000.0)
            comp.set_attenuation_radius(radius)
            
        if light_type == "Spot":
            inner = properties.get("cone_inner", 15.0)
            outer = properties.get("cone_outer", 45.0)
            comp.set_inner_cone_angle(inner)
            comp.set_outer_cone_angle(outer)
            
        if light_type == "Rect":
            # Rect lights use SourceWidth/Height
            # We didn't expose these yet, assume defaults or use radius as width?
            pass
            
    return actor
