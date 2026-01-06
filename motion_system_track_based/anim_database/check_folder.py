"""
Check specific folder for animations
"""
import unreal

OUTPUT_FILE = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\check_folder_output.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear output
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("")

folder = "/Game/Characters/Mannequins/Anims"

log("=" * 80)
log(f"CHECKING FOLDER: {folder}")
log("=" * 80)

# Check if folder exists
if unreal.EditorAssetLibrary.does_directory_exist(folder):
    log(f"\n✓ Folder exists!")
    
    # List assets
    try:
        assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False)
        log(f"\nFound {len(assets)} assets:")
        
        anim_count = 0
        for asset_path in assets[:20]:  # Show first 20
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            if asset:
                asset_name = asset.get_name()
                asset_class = asset.get_class().get_name()
                
                if "AnimSequence" in asset_class:
                    anim_count += 1
                    log(f"  [{asset_class}] {asset_name}")
        
        log(f"\n✓ Found {anim_count} AnimSequence assets")
        
    except Exception as e:
        log(f"\n✗ Error listing assets: {e}")
else:
    log(f"\n✗ Folder does not exist")

log("\n" + "=" * 80)
