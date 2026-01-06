"""
Scan Manny (UE5 Mannequin) Animations and Create Motion Matching Database

Scans the built-in UE5 Manny character's animation folder and creates a JSON database
with animation metadata for use in motion matching system.
"""

import unreal
import json
from datetime import datetime

# Output path
OUTPUT_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\manny_animations.json"
DEBUG_LOG = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\scan_manny_debug.log"

def log(msg):
    """Print message and write to debug log"""
    print(msg)
    with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear debug log
with open(DEBUG_LOG, 'w', encoding='utf-8') as f:
    f.write("")

def scan_manny_animations():
    """Scan Manny's animation folder and catalog all animations."""
    
    log("=" * 80)
    log("SCANNING MANNY (UE5 MANNEQUIN) ANIMATIONS")
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    
    # Manny animation path (confirmed to exist)
    anim_folder = "/Game/Characters/Mannequins/Anims"
    
    log(f"\nChecking folder: {anim_folder}")
    
    if not unreal.EditorAssetLibrary.does_directory_exist(anim_folder):
        log(f"✗ ERROR: Folder not found: {anim_folder}")
        return None
    
    log(f"✓ Folder exists!")
    
    log(f"\nScanning folder: {anim_folder}")
    
    # List all assets in folder
    try:
        asset_paths = unreal.EditorAssetLibrary.list_assets(anim_folder, recursive=True, include_folder=False)
        log(f"Found {len(asset_paths)} assets")
    except Exception as e:
        log(f"✗ ERROR: Could not list assets: {e}")
        return None
    
    # Build database
    database = {
        "character": "Manny",
        "base_path": anim_folder,
        "scanned_at": datetime.now().isoformat(),
        "animations": [],
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
    
    # Process each asset
    log(f"\nProcessing {len(asset_paths)} assets...")
    
    anim_count = 0
    
    for asset_path in asset_paths:
        try:
            # Load the asset
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            
            if not asset:
                continue
            
            # Check if it's an AnimSequence
            is_anim = False
            try:
                if isinstance(asset, unreal.AnimSequence):
                    is_anim = True
            except:
                pass
            
            if not is_anim:
                try:
                    class_name = asset.get_class().get_name()
                    if "AnimSequence" in class_name:
                        is_anim = True
                except:
                    pass
            
            if is_anim:
                anim_count += 1
                anim_name = asset.get_name()
                anim_name_lower = anim_name.lower()
                
                # Get animation properties
                try:
                    sequence_length = asset.get_editor_property('sequence_length')
                except:
                    sequence_length = 0.0
                
                # Frame count calculation (30 fps default)
                num_frames = int(sequence_length * 30.0) if sequence_length > 0 else 0
                
                # Classify animation
                anim_type = "other"
                estimated_speed = 0.0
                
                if "idle" in anim_name_lower or "stand" in anim_name_lower:
                    anim_type = "idle"
                    estimated_speed = 0.0
                elif "walk" in anim_name_lower:
                    anim_type = "walk"
                    estimated_speed = 1.5
                elif "jog" in anim_name_lower:
                    anim_type = "jog"
                    estimated_speed = 3.5
                elif "run" in anim_name_lower or "sprint" in anim_name_lower:
                    anim_type = "run"
                    estimated_speed = 5.5
                elif "crouch" in anim_name_lower:
                    anim_type = "crouch"
                    estimated_speed = 1.0
                elif "jump" in anim_name_lower:
                    anim_type = "jump"
                    estimated_speed = 0.0
                
                # Determine direction
                direction = "forward"
                if "bwd" in anim_name_lower or "back" in anim_name_lower:
                    direction = "backward"
                elif "left" in anim_name_lower:
                    direction = "left"
                elif "right" in anim_name_lower:
                    direction = "right"
                
                # Create animation entry
                anim_info = {
                    "name": anim_name,
                    "type": anim_type,
                    "direction": direction,
                    "duration": sequence_length,
                    "frames": num_frames,
                    "natural_speed_mps": estimated_speed,
                    "path": str(asset_path)
                }
                
                # Add to database
                database["animations"].append(anim_info)
                
                # Categorize
                if anim_type in database["by_type"]:
                    database["by_type"][anim_type].append(anim_info)
                
                log(f"  [{anim_type:8s}] {anim_name:50s} ({estimated_speed:.1f} m/s)")
                
        except Exception as e:
            log(f"  ⚠ Error loading {asset_path}: {e}")
    
    log(f"\n✓ Processed {anim_count} animations")
    return database

def save_database(database):
    """Save database to JSON file."""
    try:
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2)
        log(f"\n✓ Database saved to: {OUTPUT_PATH}")
        return True
    except Exception as e:
        log(f"\n✗ ERROR saving database: {e}")
        return False

def print_summary(database):
    """Print summary of scanned animations."""
    log("\n" + "=" * 80)
    log("ANIMATION DATABASE SUMMARY")
    log("=" * 80)
    log(f"Character: {database['character']}")
    log(f"Total Animations: {len(database['animations'])}")
    log("\nBy Type:")
    for anim_type, anims in database["by_type"].items():
        if anims:
            log(f"  {anim_type:10s}: {len(anims):3d} animations")
            # Show first few animation names
            for anim in anims[:3]:
                log(f"    - {anim['name']}")
    log("=" * 80)

if __name__ == "__main__":
    # Scan animations
    database = scan_manny_animations()
    
    if database:
        # Print summary
        print_summary(database)
        
        # Save to file
        if save_database(database):
            log("\n✅ SUCCESS! Manny animation database created.")
            log(f"   File: {OUTPUT_PATH}")
        else:
            log("\n✗ FAILED to save database")
    else:
        log("\n✗ FAILED to scan animations")
