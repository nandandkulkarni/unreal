"""
Runtime Animation Loader for Motion Matching

Loads animation metadata at runtime from Unreal Engine and saves to .jsonx format.
Run this script whenever animations are updated to refresh the database.

Usage:
    python anim_database/load_and_save_anims.py
"""

import unreal
import json

# Output path - .jsonx format
OUTPUT_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\motion_structs\belica_anims.jsonx"
DEBUG_LOG = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\load_anims_debug.log"

def log(msg):
    """Print and log to file"""
    print(msg)
    with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear debug log
with open(DEBUG_LOG, 'w', encoding='utf-8') as f:
    f.write("")

def load_animation_metadata(anim_path):
    """
    Load animation from Unreal and extract metadata.
    
    Args:
        anim_path: Full path to animation asset
        
    Returns:
        dict with animation metadata or None if failed
    """
    try:
        anim = unreal.load_object(None, anim_path)
        if not anim or not isinstance(anim, unreal.AnimSequence):
            return None
        
        # Get duration (use get_play_length() - confirmed available)
        try:
            duration = anim.get_play_length()
        except:
            try:
                duration = anim.sequence_length
            except:
                duration = 0.0
        
        # Calculate frames (30 fps for Belica)
        frames = int(duration * 30.0) if duration > 0 else 0
        
        return {
            "name": anim.get_name(),
            "path": anim_path,
            "duration": duration,
            "frames": frames,
        }
    except Exception as e:
        print(f"Error loading {anim_path}: {e}")
        return None

def classify_animation(anim_name):
    """
    Classify animation by type and estimate natural speed.
    
    Returns:
        (type, direction, speed_mps)
    """
    name_lower = anim_name.lower()
    
    # Determine type and speed
    if "idle" in name_lower or "stand" in name_lower:
        return ("idle", "forward", 0.0)
    elif "walk" in name_lower:
        return ("walk", "forward", 1.5)
    elif "jog" in name_lower:
        return ("jog", "forward", 3.5)
    elif "run" in name_lower or "sprint" in name_lower:
        return ("run", "forward", 5.5)
    elif "crouch" in name_lower:
        return ("crouch", "forward", 1.0)
    elif "jump" in name_lower:
        return ("jump", "forward", 0.0)
    else:
        return ("other", "forward", 0.0)

def build_animation_database():
    """
    Build animation database by loading all Belica animations.
    
    Returns:
        dict with animation database
    """
    log("=" * 80)
    log("LOADING BELICA ANIMATIONS (Runtime)")
    log("=" * 80)
    
    # Belica animation folder
    anim_folder = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations"
    
    log(f"\nScanning: {anim_folder}")
    
    # List all assets
    try:
        asset_paths = unreal.EditorAssetLibrary.list_assets(
            anim_folder, 
            recursive=True, 
            include_folder=False
        )
        log(f"Found {len(asset_paths)} assets")
    except Exception as e:
        log(f"Error listing assets: {e}")
        return None
    
    # Build database
    database = {
        "character": "Belica",
        "base_path": anim_folder,
        "animations": {},  # Dict for fast lookup by name
        "by_type": {
            "idle": [],
            "walk": [],
            "jog": [],
            "run": [],
            "crouch": [],
            "jump": [],
            "other": []
        }
    }
    
    # Process animations
    loaded_count = 0
    for asset_path in asset_paths:
        metadata = load_animation_metadata(asset_path)
        
        if metadata:
            anim_name = metadata["name"]
            anim_type, direction, speed = classify_animation(anim_name)
            
            # Add classification
            metadata["type"] = anim_type
            metadata["direction"] = direction
            metadata["natural_speed_mps"] = speed
            
            # Store in database (by name for fast lookup)
            database["animations"][anim_name] = metadata
            
            # Also categorize by type
            if anim_type in database["by_type"]:
                database["by_type"][anim_type].append(anim_name)
            
            loaded_count += 1
            
            # Log progress
            if loaded_count <= 5 or loaded_count % 20 == 0:
                print(f"  [{loaded_count:3d}] {anim_name:40s} ({anim_type}, {speed:.1f} m/s)")
    
    print(f"\n✓ Loaded {loaded_count} animations")
    return database

def save_to_jsonx(database, output_path):
    """Save database to .jsonx format."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2)
        print(f"\n✓ Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"\n✗ Error saving: {e}")
        return False

def print_summary(database):
    """Print database summary."""
    print("\n" + "=" * 80)
    print("DATABASE SUMMARY")
    print("=" * 80)
    print(f"Character: {database['character']}")
    print(f"Total Animations: {len(database['animations'])}")
    print("\nBy Type:")
    for anim_type, anim_names in database["by_type"].items():
        if anim_names:
            print(f"  {anim_type:10s}: {len(anim_names):3d} animations")
    print("=" * 80)

if __name__ == "__main__":
    # Build database
    database = build_animation_database()
    
    if database:
        # Print summary
        print_summary(database)
        
        # Save to .jsonx
        if save_to_jsonx(database, OUTPUT_PATH):
            print("\n✅ SUCCESS!")
            print(f"   Animation database ready for motion matching")
            print(f"   Import in Python: import json; db = json.load(open('belica_anims.jsonx'))")
        else:
            print("\n✗ FAILED to save database")
    else:
        print("\n✗ FAILED to build database")
