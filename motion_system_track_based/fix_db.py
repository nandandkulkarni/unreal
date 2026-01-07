
import unreal
import sys
import os

LOG_FILE = "C:/UnrealProjects/coding/unreal/motion_system_track_based/fix_db_log.txt"

def log(msg):
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(str(msg) + "\n")
    except:
        pass

def fix_database():
    with open(LOG_FILE, 'w') as f:
        f.write("Starting DB Fix (Guess Mode)...\n")

    log("--- Fixing MannyMotionDatabase ---")
    
    # 1. Load Database
    db_path = "/Game/MotionMatching/MannyMotionDatabase"
    db = unreal.load_object(None, db_path)
    if not db:
        log(f"Error: Database {db_path} not found.")
        return False
        
    log(f"Database loaded: {db.get_name()}")
    
    # 2. Key Animations needed for test
    # Broad search for Run
    log("Searching for animations...")
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    filter = unreal.ARFilter(
        class_names=["AnimSequence"],
        recursive_paths=True,
        package_paths=["/Game/Characters/Mannequins"]
    )
    assets = asset_registry.get_assets(filter)
    
    walk_anim = None
    run_anim = None
    jog_anim = None
    
    for data in assets:
        name = str(data.asset_name)
        if not walk_anim and "Walk_Fwd" in name and "Unarmed" in name:
            walk_anim = data.get_asset()
            log(f"Found Walk: {name}")
        if not jog_anim and "Jog_Fwd" in name and "Unarmed" in name:
            jog_anim = data.get_asset()
            log(f"Found Jog: {name}")
        if not run_anim and "Run_Fwd" in name: # Broaden search
            run_anim = data.get_asset()
            log(f"Found Run: {name}")
            
    anims_to_add = []
    if walk_anim: anims_to_add.append(walk_anim)
    if jog_anim: anims_to_add.append(jog_anim)
    if run_anim: anims_to_add.append(run_anim)
    
    if not anims_to_add:
        log("No animations found to add.")
        return False

    # 3. Add to Database
    log("Attempting to add animations...")
    
    # Try getting the list property
    # Candidates: "AnimationAssets", "Assets", "Sequences"
    target_prop = None
    db_seqs = []
    
    try_props = ["AnimationAssets", "Assets", "Sequences", "Databases"]
    
    for prop in try_props:
        try:
            val = db.get_editor_property(prop)
            target_prop = prop
            db_seqs = list(val) # ensure usage as list
            log(f"Found property: {prop} (Count: {len(db_seqs)})")
            break
        except:
            pass
            
    if not target_prop:
        log("Could not find array property on Database.")
        return False
        
    # Prepare new entries
    # Candidates for struct property: "Animation", "Sequence", "AnimSequence"
    struct_prop = "Sequence" # Default guess
    
    # Test struct property name
    dummy = unreal.PoseSearchDatabaseSequence()
    found_struct_prop = False
    
    for p_name in ["sequence", "animation", "anim_sequence"]:
        try:
            dummy.get_editor_property(p_name)
            struct_prop = p_name
            found_struct_prop = True
            log(f"Found struct property: {struct_prop}")
            break
        except:
            continue
            
    if not found_struct_prop:
        log("Warning: Could not determine struct property, trying default 'sequence'...")

    # Add new Items
    for anim in anims_to_add:
        try:
            new_entry = unreal.PoseSearchDatabaseSequence()
            new_entry.set_editor_property(struct_prop, anim)
            
            # Check for duplication? (Skip for now, safe to add)
            db_seqs.append(new_entry)
            log(f"Prepared entry for {anim.get_name()}")
            
        except Exception as e:
            log(f"Error preparing entry: {e}")

    # Set back
    if db_seqs:
        try:
            db.set_editor_property(target_prop, db_seqs)
            log("Successfully set property back to DB!")
        except Exception as e:
             log(f"Error setting DB property: {e}")
             
    # Save
    unreal.EditorAssetLibrary.save_loaded_asset(db)
    
    # Verify count
    try:
        count = len(db.get_editor_property(target_prop))
        log(f"Final DB Count: {count}")
    except:
        pass
    
    return True

if __name__ == "__main__":
    fix_database()
