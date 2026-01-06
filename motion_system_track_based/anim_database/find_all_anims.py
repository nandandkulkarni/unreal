"""
Find All Animation Folders in Project

Searches the entire project for animation folders to help locate character animations.
"""

import unreal

OUTPUT_FILE = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\find_anims_output.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear output
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("")

log("=" * 80)
log("SEARCHING FOR ANIMATION FOLDERS IN PROJECT")
log("=" * 80)

# Search in /Game
log("\nSearching /Game...")
try:
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    all_assets = asset_registry.get_all_assets()
    
    anim_folders = set()
    anim_count = 0
    
    for asset_data in all_assets:
        asset_class = str(asset_data.asset_class)
        package_path = str(asset_data.package_path)
        
        if "AnimSequence" in asset_class or "AnimMontage" in asset_class:
            anim_count += 1
            # Extract folder path
            folder = '/'.join(package_path.split('/')[:-1])
            anim_folders.add(folder)
    
    log(f"\nFound {anim_count} animation assets in {len(anim_folders)} folders")
    
    log("\nAnimation Folders:")
    for folder in sorted(anim_folders):
        log(f"  {folder}")
        
except Exception as e:
    log(f"Error: {e}")
    import traceback
    log(traceback.format_exc())

log("\n" + "=" * 80)
log(f"Output saved to: {OUTPUT_FILE}")
