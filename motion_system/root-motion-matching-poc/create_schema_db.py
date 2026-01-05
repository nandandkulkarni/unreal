"""
Create PoseSearch Schema and Database

Simple script to create the Motion Matching schema and database assets.
"""

import unreal
import os

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
LOG_FILE = os.path.join(LOG_DIR, "create_schema_db.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

log("=" * 80)
log("CREATING POSESEARCH SCHEMA AND DATABASE")
log("=" * 80)

# Step 1: Find skeleton
log("\nStep 1: Finding skeleton...")
skeleton_path = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
try:
    skeleton = unreal.EditorAssetLibrary.load_asset(skeleton_path)
    if skeleton:
        log(f"✓ Skeleton loaded: {skeleton.get_name()}")
    else:
        log(f"✗ ERROR: Skeleton not found at {skeleton_path}")
        raise Exception("Skeleton not found")
except Exception as e:
    log(f"✗ ERROR: {e}")
    raise

# Step 2: Create MotionMatching folder
log("\nStep 2: Creating /Game/MotionMatching folder...")
try:
    mm_exists = unreal.EditorAssetLibrary.does_directory_exist("/Game/MotionMatching")
    if mm_exists:
        log("  Folder already exists")
    else:
        success = unreal.EditorAssetLibrary.make_directory("/Game/MotionMatching")
        if success:
            log("✓ Folder created")
        else:
            log("✗ ERROR: Could not create folder")
            raise Exception("Folder creation failed")
except Exception as e:
    log(f"✗ ERROR: {e}")
    raise

# Step 3: Create Schema
log("\nStep 3: Creating PoseSearchSchema...")
schema_path = "/Game/MotionMatching/MannyMotionSchema"

try:
    # Check if it already exists
    existing_schema = unreal.EditorAssetLibrary.load_asset(schema_path)
    if existing_schema:
        log(f"  Schema already exists: {existing_schema.get_name()}")
        schema = existing_schema
    else:
        # Create new schema
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", unreal.PoseSearchSchema.static_class())
        
        log(f"  Creating schema at: {schema_path}")
        schema = asset_tools.create_asset(
            "MannyMotionSchema",
            "/Game/MotionMatching",
            unreal.PoseSearchSchema,
            factory
        )
        
        if schema:
            log(f"✓ Schema created: {schema.get_name()}")
        else:
            log("✗ ERROR: create_asset returned None")
            raise Exception("Schema creation failed")
    
    # Set skeleton
    log("  Setting skeleton property...")
    schema.set_editor_property("skeleton", skeleton)
    
    # Save
    log("  Saving schema...")
    saved = unreal.EditorAssetLibrary.save_asset(schema_path)
    if saved:
        log("✓ Schema saved")
    else:
        log("⚠ Save returned False")
        
except Exception as e:
    log(f"✗ ERROR creating schema: {e}")
    import traceback
    log(traceback.format_exc())
    raise

# Step 4: Create Database
log("\nStep 4: Creating PoseSearchDatabase...")
database_path = "/Game/MotionMatching/MannyMotionDatabase"

try:
    # Check if it already exists
    existing_db = unreal.EditorAssetLibrary.load_asset(database_path)
    if existing_db:
        log(f"  Database already exists: {existing_db.get_name()}")
        database = existing_db
    else:
        # Create new database
        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", unreal.PoseSearchDatabase.static_class())
        
        log(f"  Creating database at: {database_path}")
        database = asset_tools.create_asset(
            "MannyMotionDatabase",
            "/Game/MotionMatching",
            unreal.PoseSearchDatabase,
            factory
        )
        
        if database:
            log(f"✓ Database created: {database.get_name()}")
        else:
            log("✗ ERROR: create_asset returned None")
            raise Exception("Database creation failed")
    
    # Set schema
    log("  Setting schema property...")
    database.set_editor_property("schema", schema)
    
    # Save
    log("  Saving database...")
    saved = unreal.EditorAssetLibrary.save_asset(database_path)
    if saved:
        log("✓ Database saved")
    else:
        log("⚠ Save returned False")
        
except Exception as e:
    log(f"✗ ERROR creating database: {e}")
    import traceback
    log(traceback.format_exc())
    raise

log("\n" + "=" * 80)
log("✅ SUCCESS!")
log("=" * 80)
log(f"\nCreated:")
log(f"  Schema: {schema_path}")
log(f"  Database: {database_path}")
log(f"\nLog: {LOG_FILE}")
