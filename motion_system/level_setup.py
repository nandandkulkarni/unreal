""" 
Level creation and management logic.
"""
import unreal
from logger import log, log_header

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
