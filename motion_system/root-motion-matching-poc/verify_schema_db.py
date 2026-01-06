"""
Verify Schema and Database Creation

Simple script to check if the schema and database were created successfully.
"""

import unreal
import os

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
LOG_FILE = os.path.join(LOG_DIR, "verify_schema_db.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

log("=" * 80)
log("VERIFYING SCHEMA AND DATABASE")
log("=" * 80)

schema_path = "/Game/MotionMatching/MannyMotionSchema"
database_path = "/Game/MotionMatching/MannyMotionDatabase"

# Check Schema
log("\nChecking Schema...")
try:
    schema = unreal.EditorAssetLibrary.load_asset(schema_path)
    if schema:
        log(f"✓ Schema EXISTS: {schema.get_name()}")
        log(f"  Type: {type(schema)}")
        log(f"  Path: {schema.get_path_name()}")
        
        # Check skeleton property
        try:
            skel = schema.get_editor_property("skeleton")
            if skel:
                log(f"  Skeleton: {skel.get_name()}")
            else:
                log("  ⚠ Skeleton property is None")
        except:
            log("  ⚠ Could not read skeleton property")
    else:
        log(f"✗ Schema NOT FOUND at {schema_path}")
except Exception as e:
    log(f"✗ ERROR loading schema: {e}")

# Check Database
log("\nChecking Database...")
try:
    database = unreal.EditorAssetLibrary.load_asset(database_path)
    if database:
        log(f"✓ Database EXISTS: {database.get_name()}")
        log(f"  Type: {type(database)}")
        log(f"  Path: {database.get_path_name()}")
        
        # Check schema property
        try:
            db_schema = database.get_editor_property("schema")
            if db_schema:
                log(f"  Schema: {db_schema.get_name()}")
            else:
                log("  ⚠ Schema property is None")
        except:
            log("  ⚠ Could not read schema property")
        
        # Check animation count
        try:
            lib = unreal.AAANKPoseBlueprintLibrary
            count = lib.get_animation_count(database)
            log(f"  Animation count: {count}")
        except Exception as e:
            log(f"  Could not get animation count: {e}")
    else:
        log(f"✗ Database NOT FOUND at {database_path}")
except Exception as e:
    log(f"✗ ERROR loading database: {e}")

log("\n" + "=" * 80)
log("VERIFICATION COMPLETE")
log("=" * 80)
log(f"\nLog: {LOG_FILE}")
