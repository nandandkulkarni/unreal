"""
Scan Belica Animations and Create Motion Matching Database

Adapted from populate_animations.py - uses proven EditorAssetLibrary approach
to scan and catalog Belica's animations for motion matching.
"""

import unreal
import json
import os
from datetime import datetime

# Output path
OUTPUT_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\belica_anim_database.json"

def log(msg):
    """Print and log message"""
    print(msg)

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
    for asset_path in asset_paths:
        try:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            
            if isinstance(asset, unreal.AnimSequence):
                anim_name = asset.get_name()
                anim_name_lower = anim_name.lower()
                
                # Get animation properties
                sequence_length = asset.get_editor_property('sequence_length')
                num_frames = asset.get_number_of_frames()
                
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
            log(f"   Use this file in motion_cmds/splines.py for motion matching")
        else:
            log("\n✗ FAILED to save database")
    else:
        log("\n✗ FAILED to scan animations")
