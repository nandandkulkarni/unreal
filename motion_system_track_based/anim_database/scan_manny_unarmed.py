"""
Scan Manny Unarmed Animations

Scans the UE5 Mannequin UNARMED animation folder and generates a JSONX database.
"""
import unreal
import os
import json
import datetime
import math

# Configuration
CHARACTER_NAME = "Manny_Unarmed"
# Target only the Unarmed folder
SEARCH_PATH = "/Game/Characters/Mannequins/Anims/Unarmed" 
OUTPUT_FILENAME = "manny_unarmed_anims.jsonx"

def get_script_dir():
    # In Unreal, __file__ might not be reliable, so we hardcode the known path structure
    # relative to the project if needed, or just use absolute path for now.
    # Assuming this script is in c:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database
    return r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database"

def log(msg):
    print(f"[ScanMannyUnarmed] {msg}")

def categorize_animation(name):
    """
    Categorize animation based on naming convention.
    Returns (type, direction)
    """
    name_lower = name.lower()
    
    anim_type = "other"
    direction = "forward"
    
    # Type detection
    if "idle" in name_lower:
        anim_type = "idle"
    elif "walk" in name_lower:
        anim_type = "walk"
    elif "jog" in name_lower:
        anim_type = "jog"
    elif "run" in name_lower:
        anim_type = "run"
    elif "jump" in name_lower:
        anim_type = "jump"
    elif "land" in name_lower:
        anim_type = "land"
    elif "fall" in name_lower:
        anim_type = "fall"
        
    # Direction detection
    if "bwd" in name_lower or "backward" in name_lower:
        direction = "backward"
    elif "left" in name_lower:
        direction = "left"
    elif "right" in name_lower:
        direction = "right"
    else:
        direction = "forward"
        
    return anim_type, direction

def estimate_speed(anim_asset, anim_type):
    """
    Estimate natural speed based on animation type.
    In a real system, we would extract root motion.
    """
    if anim_type == "idle":
        return 0.0
    elif anim_type == "walk":
        return 1.5 # m/s
    elif anim_type == "jog":
        return 3.5 # m/s (standard UE jog)
    elif anim_type == "run":
        return 5.0 # m/s
    elif anim_type == "sprint":
        return 6.5 # m/s
    return 0.0

def scan_animations():
    log(f"Scanning folder: {SEARCH_PATH}")
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Filter for AnimSequence
    filter = unreal.ARFilter(
        class_names=["AnimSequence"],
        package_paths=[SEARCH_PATH],
        recursive_paths=True
    )
    
    assets = asset_registry.get_assets(filter)
    log(f"Found {len(assets)} animation assets.")
    
    database = {
        "character": CHARACTER_NAME,
        "base_path": SEARCH_PATH,
        "scanned_at": datetime.datetime.now().isoformat(),
        "animations": []
    }
    
    for asset_data in assets:
        asset_name = str(asset_data.asset_name)
        package_name = str(asset_data.package_name)
        
        # Load the asset to get details
        anim_seq = unreal.EditorAssetLibrary.load_asset(package_name)
        if not anim_seq:
            continue
            
        # Get duration
        # Note: get_play_length is the correct API for 5.x
        duration = 0.0
        if hasattr(anim_seq, "get_play_length"):
            duration = anim_seq.get_play_length()
        else:
            # Fallback for older versions
            try:
                duration = anim_seq.sequence_length
            except:
                pass
                
        # Get Frame Count
        # approximate from framerate if not directly available
        # Default UE animation is 30fps usually
        frames = int(duration * 30.0) 
        
        # Categorize
        anim_type, direction = categorize_animation(asset_name)
        speed = estimate_speed(anim_seq, anim_type)
        
        # Determine full path
        # Verify it exists in a way we can load later
        full_path = f"{package_name}.{asset_name}"
        
        entry = {
            "name": asset_name,
            "type": anim_type,
            "direction": direction,
            "duration": duration,
            "frames": frames,
            "natural_speed_mps": speed,
            "path": full_path
        }
        
        database["animations"].append(entry)
        log(f"  Processed: {asset_name} ({anim_type}/{direction})")
        
    # Save database
    # Construct output path in motion_structs
    output_dir = os.path.join(os.path.dirname(get_script_dir()), "motion_structs")
    output_path = os.path.join(output_dir, OUTPUT_FILENAME)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
        
    log(f"Database saved to: {output_path}")
    log(f"Total animations: {len(database['animations'])}")

if __name__ == "__main__":
    scan_animations()
