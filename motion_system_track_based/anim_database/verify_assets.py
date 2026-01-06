"""
Verify Animation Assets

Checks if the animation paths generated in the MannySpeedDemo output actually exist
and can be loaded by Unreal.
"""

import unreal
import json
import os

DIST_FOLDER = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\dist\MannySpeedDemo"
OUTPUT_FILE = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\verify_assets_output.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear output
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("")

log("=" * 80)
log("VERIFYING ANIMATION ASSETS")
log("=" * 80)

# Check Walker
walker_anim_path = os.path.join(DIST_FOLDER, "Walker", "animation.json")
if os.path.exists(walker_anim_path):
    with open(walker_anim_path, 'r') as f:
        anims = json.load(f)
    
    log(f"\nChecking Walker animations ({len(anims)}):")
    for anim in anims:
        name = anim.get("name")
        # We need to resolve the full path. 
        # The JSON only has the name "MF_Pistol_Walk_Fwd"
        # The loader has the full path. We need to verify if we can find it.
        
        # Load database to verify path
        log(f"  Name: {name}")
        
        # Try to find asset
        found = False
        
        # Method 1: Check known database path (hardcoded check for demo)
        known_base = "/Game/Characters/Mannequins/Anims/Pistol/Walk"
        full_path = f"{known_base}/{name}.{name}"
        
        if unreal.EditorAssetLibrary.does_asset_exist(full_path):
             log(f"    ✓ Found at: {full_path}")
             asset = unreal.EditorAssetLibrary.load_asset(full_path)
             log(f"      Loaded: {asset}")
             found = True
        else:
             # Try other variant
             known_base_jog = "/Game/Characters/Mannequins/Anims/Pistol/Jog"
             full_path_jog = f"{known_base_jog}/{name}.{name}"
             if unreal.EditorAssetLibrary.does_asset_exist(full_path_jog):
                 log(f"    ✓ Found at: {full_path_jog}")
                 asset = unreal.EditorAssetLibrary.load_asset(full_path_jog)
                 log(f"      Loaded: {asset}")
                 found = True
        
        if not found:
            log(f"    ✗ NOT FOUND")

# Check Jogger
jogger_anim_path = os.path.join(DIST_FOLDER, "Jogger", "animation.json")
if os.path.exists(jogger_anim_path):
    with open(jogger_anim_path, 'r') as f:
        anims = json.load(f)
        
    log(f"\nChecking Jogger animations ({len(anims)}):")
    for anim in anims:
        name = anim.get("name")
        log(f"  Name: {name}")
        
        # Quick check in Jog folder
        known_base_jog = "/Game/Characters/Mannequins/Anims/Pistol/Jog"
        full_path_jog = f"{known_base_jog}/{name}.{name}"
        
        if unreal.EditorAssetLibrary.does_asset_exist(full_path_jog):
             log(f"    ✓ Found at: {full_path_jog}")
        else:
             log(f"    ✗ NOT FOUND at expected path")

log("\n" + "=" * 80)
