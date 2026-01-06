# Simple inline logger functions for motion_includes
# This avoids import conflicts with other logger modules in the Python path

def log(message, log_file=None):
    """Print message"""
    print(message)

def log_header(title):
    """Print header"""
    print("=" * 60)
    print(title)
    print("=" * 60)


""" 
Level creation and management logic.
"""
import unreal
# import logger
# from logger import log, log_header

def create_basic_level():
    """Create a new level based on the Basic (Template_Default) template."""
    log_header("STEP 1: Creating New Level (Basic Template)")
    
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    # Path to the typical "Basic" template in UE5
    template_path = "/Engine/Maps/Templates/Template_Default"
    new_level_path = "/Game/Movies/TempLevel"
    
    try:
        # Signature can be (AssetPath, TemplatePath) or vice versa depending on UE version/plugin
        success = subsystem.new_level_from_template(new_level_path, template_path)
        if not success:
            log(f"  ⚠ First attempt failed, trying alternate argument order...")
            success = subsystem.new_level_from_template(template_path, new_level_path)
        
        if success:
            log(f"✓ New level created from template: {template_path}")
            # Explicitly load/open the level for the editor
            subsystem.load_level(new_level_path)
            unreal.EditorLevelLibrary.save_all_dirty_packages(False, True)
            return True
        else:
            log(f"✗ Failed to create level from template: {template_path}")
            return False
            
    except Exception as e:
        log(f"✗ ERROR creating level: {e}")
        return False

def save_current_level(level_path):
    """Save the currently open level to a specific path."""
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    success = subsystem.save_current_level_as(level_path)
    if success:
        log(f"✓ Level saved to: {level_path}")
    else:
        log(f"✗ Failed to save level to: {level_path}")
    return success


def apply_atmosphere_settings(cmd):
    """Apply atmosphere/fog settings to the level's ExponentialHeightFog actor."""
    
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
    
    # Delete all existing fog actors first (clean slate)
    fog_actors = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.ExponentialHeightFog
    )
    
    for old_fog in fog_actors:
        unreal.EditorLevelLibrary.destroy_actor(old_fog)
        log(f"    Deleted old fog: {old_fog.get_name()}")
    
    # Create new fog actor
    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog,
        unreal.Vector(0, 0, 0)
    )
    fog_actor.set_actor_label("_AtmosphereFog")
    fog_actor.tags.append("MotionSystemActor")
    log(f"    Created new ExponentialHeightFog actor")
    
    # Get fog component
    fog_component = fog_actor.component
    
    # Apply fog density
    fog_density = cmd.get("fog_density", 0.02)
    if isinstance(fog_density, str):
        fog_density = DENSITY_PRESETS.get(fog_density, 0.02)
    fog_component.set_editor_property("fog_density", fog_density)
    
    # Apply fog color (use fog_inscattering_luminance in UE 5.7)
    fog_color = cmd.get("fog_color", (0.6, 0.7, 1.0))
    if isinstance(fog_color, str):
        fog_color = COLOR_PRESETS.get(fog_color, (0.6, 0.7, 1.0))
    color = unreal.LinearColor(r=fog_color[0], g=fog_color[1], b=fog_color[2])
    fog_component.set_editor_property("fog_inscattering_luminance", color)
    
    # Apply height falloff
    fog_height_falloff = cmd.get("fog_height_falloff", 0.2)
    fog_component.set_editor_property("fog_height_falloff", fog_height_falloff)
    
    # Apply max opacity
    fog_max_opacity = cmd.get("fog_max_opacity", 1.0)
    fog_component.set_editor_property("fog_max_opacity", fog_max_opacity)
    
    # Apply start distance
    start_distance = cmd.get("start_distance", 0)
    fog_component.set_editor_property("start_distance", start_distance)
    
    # Apply volumetric fog settings (volumetric_fog boolean doesn't exist in UE 5.7, skip it)
    volumetric = cmd.get("volumetric", False)
    
    if volumetric:
        # Apply volumetric scattering intensity
        volumetric_scattering = cmd.get("volumetric_scattering", 1.0)
        fog_component.set_editor_property("volumetric_fog_scattering_distribution", volumetric_scattering)
        
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
    
    log(f"    Fog density: {fog_density}, color: {fog_color}, volumetric: {volumetric}")
