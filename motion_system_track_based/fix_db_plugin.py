
import unreal
import sys
import os

LOG_FILE = "C:/UnrealProjects/coding/unreal/motion_system_track_based/fix_db_plugin_log.txt"

def log(msg):
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(str(msg) + "\n")
    except:
        pass

def fix_database_with_plugin():
    # Clear log
    with open(LOG_FILE, 'w') as f:
        f.write("Starting DB Fix (Plugin Mode)...\n")
    
    log("--- Fixing MannyMotionDatabase with AAANKPosePlugin ---")
    
    # 1. Check Plugin
    try:
        lib = unreal.AAANKPoseBlueprintLibrary
        log("AAANKPoseBlueprintLibrary found.")
    except AttributeError:
        log("Error: AAANKPoseBlueprintLibrary NOT found. Plugin missing?")
        return False

    # 2. Load Database
    db_path = "/Game/MotionMatching/MannyMotionDatabase"
    db = unreal.load_object(None, db_path)
    if not db:
        log(f"Error: Database {db_path} not found.")
        return False
    
    log(f"Database loaded: {db.get_name()}")
    
    # 3. Find Animations
    anims_to_add = []
    
    # Specific paths that likely exist
    candidates = [
        "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd",
        "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd",
        "/Game/Characters/Mannequins/Anims/Unarmed/Run/MF_Unarmed_Run_Fwd",
        # Fallback or additional
        "/Game/Characters/Mannequins/Anims/Manny/Run/MF_Manny_Run_Fwd" 
    ]
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    for path in candidates:
        anim = unreal.load_object(None, path)
        if anim:
            anims_to_add.append(anim)
            log(f"Found asset: {anim.get_name()}")
        else:
            log(f"Asset not found at: {path}")
            
    # Search fallback if Run missing
    has_run = any("Run" in a.get_name() for a in anims_to_add)
    if not has_run:
        log("Searching for any Run animation...")
        filter = unreal.ARFilter(
            class_names=["AnimSequence"],
            recursive_paths=True,
            package_paths=["/Game/Characters/Mannequins"]
        )
        assets = asset_registry.get_assets(filter)
        for data in assets:
            if "Run_Fwd" in str(data.asset_name):
                anim = data.get_asset()
                anims_to_add.append(anim)
                log(f"Found Run via search: {anim.get_name()}")
                break

    if not anims_to_add:
        log("No animations to add.")
        return False
        
    # 4. Add to Database
    count_added = 0
    for anim in anims_to_add:
        try:
            # The plugin function: add_animation_to_database(database, animation) -> bool
            result = lib.add_animation_to_database(db, anim)
            if result:
                log(f"Successfully added: {anim.get_name()}")
                count_added += 1
            else:
                log(f"Failed to add (returned False): {anim.get_name()}")
        except Exception as e:
            log(f"Error calling plugin for {anim.get_name()}: {e}")
            
    log(f"Total Added: {count_added}")
    
    # 5. Build Database (Optional but good)
    try:
        if hasattr(lib, "build_database"):
             lib.build_database(db)
             log("Database build triggered.")
    except Exception as e:
        log(f"Build error: {e}")

    # Save
    unreal.EditorAssetLibrary.save_loaded_asset(db)
    
    # Verify count
    try:
        final_count = lib.get_animation_count(db)
        log(f"Final Count via Plugin: {final_count}")
    except:
        pass
        
    return True

if __name__ == "__main__":
    fix_database_with_plugin()
