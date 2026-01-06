"""
Full Motion Matching Database Population Script

This script uses the AAANKPose plugin to:
1. Create the Motion Matching database (if needed)
2. Find all 123 locomotion animations
3. Add them all to the database automatically
4. Build the database

Run with: python run_remote.py populate_database_full.py
"""

import unreal
import os
from datetime import datetime

# Log file with timestamp in logs subfolder
LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"populate_database_{timestamp}.log")

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(message):
    """Write to log and console"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def find_locomotion_animations():
    """Find all locomotion animations for Manny"""
    log("\n" + "=" * 80)
    log("FINDING LOCOMOTION ANIMATIONS")
    log("=" * 80)
    
    # Animation folders to search
    anim_folders = [
        "/Game/Characters/Mannequins/Animations",
        "/Game/Characters/Mannequins/Animations/Manny",
        "/Game/Characters/Mannequins/Animations/Unarmed",
        "/Game/Characters/Mannequins/Animations/Pistol",
        "/Game/Characters/Mannequins/Animations/Rifle"
    ]
    
    # Keywords for locomotion animations
    locomotion_keywords = [
        'walk', 'run', 'idle', 'jog', 'sprint',
        'turn', 'start', 'stop', 'pivot',
        'strafe', 'backward', 'forward', 'left', 'right',
        'mm_', 'locomotion'
    ]
    
    all_animations = []
    
    for folder in anim_folders:
        try:
            # Get all assets in folder
            assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False)
            
            for asset_path in assets:
                # Load asset to check if it's an AnimSequence
                asset = unreal.EditorAssetLibrary.load_asset(asset_path)
                
                if isinstance(asset, unreal.AnimSequence):
                    asset_name = asset.get_name().lower()
                    
                    # Check if it matches locomotion keywords
                    if any(keyword in asset_name for keyword in locomotion_keywords):
                        all_animations.append(asset)
                        log(f"  Found: {asset.get_name()} ({asset_path})")
        except Exception as e:
            log(f"  Warning: Could not search folder {folder}: {e}")
    
    log(f"\n✓ Found {len(all_animations)} locomotion animations")
    return all_animations

def create_database_if_needed():
    """Create schema and database if they don't exist"""
    log("\n" + "=" * 80)
    log("CHECKING DATABASE")
    log("=" * 80)
    
    schema_path = "/Game/MotionMatching/MannyMotionSchema"
    database_path = "/Game/MotionMatching/MannyMotionDatabase"
    
    # Check if database exists
    database = unreal.EditorAssetLibrary.load_asset(database_path)
    
    if database:
        log(f"✓ Database already exists: {database.get_name()}")
        return database
    
    log("Database not found, creating...")
    
    # Find skeleton
    skeleton_path = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
    skeleton = unreal.EditorAssetLibrary.load_asset(skeleton_path)
    
    if not skeleton:
        log(f"✗ ERROR: Could not find skeleton at {skeleton_path}")
        return None
    
    log(f"✓ Found skeleton: {skeleton.get_name()}")
    
    # Create schema
    log("\nCreating PoseSearchSchema...")
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    schema_factory = unreal.DataAssetFactory()
    schema_factory.data_asset_class = unreal.PoseSearchSchema
    
    schema = asset_tools.create_asset(
        "MannyMotionSchema",
        "/Game/MotionMatching",
        unreal.PoseSearchSchema,
        schema_factory
    )
    
    if schema:
        schema.set_editor_property("skeleton", skeleton)
        unreal.EditorAssetLibrary.save_asset(schema_path)
        log(f"✓ Created schema: {schema.get_name()}")
    else:
        log("✗ ERROR: Failed to create schema")
        return None
    
    # Create database
    log("\nCreating PoseSearchDatabase...")
    database_factory = unreal.DataAssetFactory()
    database_factory.data_asset_class = unreal.PoseSearchDatabase
    
    database = asset_tools.create_asset(
        "MannyMotionDatabase",
        "/Game/MotionMatching",
        unreal.PoseSearchDatabase,
        database_factory
    )
    
    if database:
        database.set_editor_property("schema", schema)
        unreal.EditorAssetLibrary.save_asset(database_path)
        log(f"✓ Created database: {database.get_name()}")
        return database
    else:
        log("✗ ERROR: Failed to create database")
        return None

def populate_database():
    """Main function to populate the database"""
    
    log("=" * 80)
    log("MOTION MATCHING DATABASE - FULL AUTOMATION")
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    
    # Load plugin library
    log("\nLoading AAANKPose plugin...")
    try:
        lib = unreal.AAANKPoseBlueprintLibrary
        log("✓ Plugin loaded successfully")
    except Exception as e:
        log(f"✗ ERROR: Could not load plugin: {e}")
        return False
    
    # Create or load database
    database = create_database_if_needed()
    if not database:
        log("\n✗ FAILED: Could not create/load database")
        return False
    
    # Get current count
    current_count = lib.get_animation_count(database)
    log(f"\nCurrent animation count: {current_count}")
    
    # Find all animations
    animations = find_locomotion_animations()
    
    if not animations:
        log("\n✗ ERROR: No animations found")
        return False
    
    # Add all animations
    log("\n" + "=" * 80)
    log(f"ADDING {len(animations)} ANIMATIONS TO DATABASE")
    log("=" * 80)
    
    try:
        added_count = lib.add_animations_to_database(database, animations)
        log(f"\n✓ Successfully added {added_count}/{len(animations)} animations")
    except Exception as e:
        log(f"\n✗ ERROR adding animations: {e}")
        return False
    
    # Get new count
    new_count = lib.get_animation_count(database)
    log(f"New animation count: {new_count}")
    log(f"Increase: +{new_count - current_count}")
    
    # Build database
    log("\n" + "=" * 80)
    log("BUILDING DATABASE")
    log("=" * 80)
    
    try:
        success = lib.build_database(database)
        if success:
            log("✓ Database built successfully!")
        else:
            log("⚠ Build returned False (check Unreal Output Log)")
    except Exception as e:
        log(f"✗ ERROR building database: {e}")
        return False
    
    # Get final info
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
    log(f"\nFull log saved to: {LOG_FILE}")
    log("\nYour Motion Matching database is ready to use!")
    log("Next: Create an AnimBP with Motion Matching node and test it!")
    
    return True

if __name__ == "__main__":
    success = populate_database()
    if success:
        print("\n🎉 Database population complete!")
    else:
        print("\n❌ Database population failed - check log for details")
