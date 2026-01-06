"""
Populate Motion Matching Database with Animations

Uses the AAANKPose plugin to add all locomotion animations to the database.
"""

import unreal
import os
from datetime import datetime

# Log setup
LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"populate_animations_{timestamp}.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

log("=" * 80)
log("POPULATING DATABASE WITH ANIMATIONS")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# Load plugin
log("\nLoading AAANKPose plugin...")
try:
    lib = unreal.AAANKPoseBlueprintLibrary
    log("✓ Plugin loaded")
except Exception as e:
    log(f"✗ ERROR: {e}")
    raise

# Load database
log("\nLoading database...")
database_path = "/Game/MotionMatching/MannyMotionDatabase"
try:
    database = unreal.load_object(None, database_path)
    if database:
        log(f"✓ Database loaded: {database.get_name()}")
    else:
        log(f"✗ ERROR: Database not found at {database_path}")
        raise Exception("Database not found")
except Exception as e:
    log(f"✗ ERROR: {e}")
    raise

# Get current count
current_count = lib.get_animation_count(database)
log(f"  Current animations: {current_count}")

# Find all locomotion animations
log("\nFinding locomotion animations...")
anim_folders = [
    "/Game/Characters/Mannequins/Anims"
]

locomotion_keywords = [
    'walk', 'run', 'idle', 'jog', 'sprint',
    'turn', 'start', 'stop', 'pivot',
    'strafe', 'backward', 'forward', 'left', 'right',
    'mm_', 'locomotion', 'jump', 'fall', 'land'
]

animations = []

for folder in anim_folders:
    try:
        assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False)
        
        for asset_path in assets:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            
            if isinstance(asset, unreal.AnimSequence):
                asset_name = asset.get_name().lower()
                
                if any(keyword in asset_name for keyword in locomotion_keywords):
                    animations.append(asset)
                    log(f"  Found: {asset.get_name()}")
    except Exception as e:
        log(f"  Warning: Could not search {folder}: {e}")

log(f"\n✓ Found {len(animations)} locomotion animations")

if not animations:
    log("\n✗ ERROR: No animations found")
    raise Exception("No animations found")

# Add animations to database
log("\n" + "=" * 80)
log(f"ADDING {len(animations)} ANIMATIONS TO DATABASE")
log("=" * 80)

try:
    added_count = lib.add_animations_to_database(database, animations)
    log(f"\n✓ Added {added_count}/{len(animations)} animations")
except Exception as e:
    log(f"\n✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())
    raise

# Get new count
new_count = lib.get_animation_count(database)
log(f"  New animation count: {new_count}")
log(f"  Increase: +{new_count - current_count}")

# Build database
log("\n" + "=" * 80)
log("BUILDING DATABASE INDEX")
log("=" * 80)

try:
    success = lib.build_database(database)
    if success:
        log("✓ Database built and saved successfully!")
    else:
        log("⚠ Build returned False (check Unreal Output Log)")
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

# Final info
log("\n" + "=" * 80)
log("DATABASE INFO")
log("=" * 80)

try:
    info = lib.get_database_info(database)
    log(info)
except Exception as e:
    log(f"Could not get info: {e}")

log("\n" + "=" * 80)
log("✅ COMPLETE!")
log("=" * 80)
log(f"\nYour Motion Matching database is ready!")
log(f"  Database: {database_path}")
log(f"  Animations: {new_count}")
log(f"\nLog: {LOG_FILE}")
