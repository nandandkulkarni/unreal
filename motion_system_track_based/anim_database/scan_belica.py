"""
Scan Belica Animations and Create Motion Matching Database

Scans Belica's animation folder and creates a JSON database with animation metadata
for use in motion matching system.
"""

import unreal
import json
import os
from datetime import datetime

# Output path - use absolute path since __file__ doesn't work in Unreal Python context
OUTPUT_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\belica_animations.json"
DEBUG_LOG = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\scan_debug.log"

def log(msg):
    """Print message and write to debug log"""
    print(msg)
    with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear debug log
with open(DEBUG_LOG, 'w', encoding='utf-8') as f:
    f.write("")

def scan_belica_animations():
    """Scan Belica's animation folder and catalog all animations."""
    
    log("=" * 80)
    log("SCANNING BELICA ANIMATIONS")
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    
    # Belica animation folder
    anim_folder = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations"
    
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
        "character": "Belica",
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
            "rifle": [],
            "other": []
        }
    }
    
    # Process each asset
    log(f"\nProcessing {len(asset_paths)} assets...")
    
    processed_count = 0
    anim_count = 0
    
    for asset_path in asset_paths:
        processed_count += 1
        if processed_count <= 5:  # Log first 5 for debugging
            log(f"\n  Processing #{processed_count}: {asset_path}")
        
        try:
            # Load the asset
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            
            if not asset:
                if processed_count <= 5:
                    log(f"    ✗ Asset is None")
                continue
            
            if processed_count <= 5:
                log(f"    ✓ Asset loaded: {type(asset)}")
            
            # Check if it's an AnimSequence - use multiple methods
            is_anim = False
            try:
                # Method 1: isinstance check
                if isinstance(asset, unreal.AnimSequence):
                    is_anim = True
                    if processed_count <= 5:
                        log(f"    ✓ Method 1 (isinstance): SUCCESS")
            except Exception as e:
                if processed_count <= 5:
                    log(f"    ✗ Method 1 failed: {e}")
            
            # Method 2: Check class name
            if not is_anim:
                try:
                    class_name = asset.get_class().get_name()
                    if processed_count <= 5:
                        log(f"    Class name: {class_name}")
                    if "AnimSequence" in class_name or "Anim" in class_name:
                        is_anim = True
                        if processed_count <= 5:
                            log(f"    ✓ Method 2 (class name): SUCCESS")
                except Exception as e:
                    if processed_count <= 5:
                        log(f"    ✗ Method 2 failed: {e}")
            
            # Method 3: Check if it has animation-specific methods
            if not is_anim:
                if hasattr(asset, 'get_number_of_frames') and hasattr(asset, 'get_editor_property'):
                    try:
                        # Try to access animation-specific property
                        seq_len = asset.get_editor_property('sequence_length')
                        is_anim = True
                        if processed_count <= 5:
                            log(f"    ✓ Method 3 (properties): SUCCESS (len={seq_len})")
                    except Exception as e:
                        if processed_count <= 5:
                            log(f"    ✗ Method 3 failed: {e}")
            
            if is_anim:
                anim_count += 1
                anim_name = asset.get_name()
                anim_name_lower = anim_name.lower()
                
                # Get animation properties - use only valid methods
                try:
                    sequence_length = asset.get_editor_property('sequence_length')
                except:
                    sequence_length = 0.0
                
                # Frame count calculation (30 fps default for Belica)
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
                elif "rifle" in anim_name_lower:
                    anim_type = "rifle"
                
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
                    "estimated_speed_mps": estimated_speed,
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
    log("=" * 80)

if __name__ == "__main__":
    # Scan animations
    database = scan_belica_animations()
    
    if database:
        # Print summary
        print_summary(database)
        
        # Save to file
        if save_database(database):
            log("\n✅ SUCCESS! Animation database created.")
            log(f"   File: {OUTPUT_PATH}")
        else:
            log("\n✗ FAILED to save database")
    else:
        log("\n✗ FAILED to scan animations")
