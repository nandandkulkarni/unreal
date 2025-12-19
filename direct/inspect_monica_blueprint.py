import unreal

print("\n" + "="*60)
print("FINDING MONICA'S ACTUAL ASSETS")
print("="*60 + "\n")

# Search for all assets in Monica's folder
monica_folder = "/Game/Fab/MetaHuman/MHC_Monica"
print(f"Searching folder: {monica_folder}\n")

# Check if folder exists
if not unreal.EditorAssetLibrary.does_directory_exist(monica_folder):
    print(f"✗ Folder doesn't exist: {monica_folder}")
    print("\nTrying parent folder...")
    monica_folder = "/Game/Fab/MetaHuman"

# List all assets in the folder
print(f"Listing all assets in: {monica_folder}\n")
assets = unreal.EditorAssetLibrary.list_assets(monica_folder, recursive=True, include_folder=False)

if not assets:
    print("✗ No assets found!")
else:
    print(f"Found {len(assets)} assets\n")
    
    print("-" * 60)
    print("SKELETAL MESHES:")
    print("-" * 60)
    for asset_path in assets:
        asset = unreal.load_asset(asset_path)
        if asset and isinstance(asset, unreal.SkeletalMesh):
            print(f"✓ {asset_path}")
            print(f"  Name: {asset.get_name()}")
            skeleton = asset.get_skeleton()
            if skeleton:
                print(f"  Skeleton: {skeleton.get_name()}")
            print()
    
    print("-" * 60)
    print("ANIMATION BLUEPRINTS:")
    print("-" * 60)
    for asset_path in assets:
        if "ABP_" in asset_path or "AnimBlueprint" in asset_path or "_AnimBP" in asset_path:
            asset = unreal.load_asset(asset_path)
            if asset:
                print(f"✓ {asset_path}")
                print(f"  Name: {asset.get_name()}")
                print(f"  Type: {asset.get_class().get_name()}")
                print()
    
    print("-" * 60)
    print("BLUEPRINTS:")
    print("-" * 60)
    for asset_path in assets:
        if "BP_" in asset_path or "Blueprint" in asset_path:
            asset = unreal.load_asset(asset_path)
            if asset and hasattr(asset, 'generated_class'):
                print(f"✓ {asset_path}")
                print(f"  Name: {asset.get_name()}")
                print(f"  Type: {asset.get_class().get_name()}")
                print()
    
    print("-" * 60)
    print("ALL ASSET TYPES IN MONICA FOLDER:")
    print("-" * 60)
    asset_types = {}
    for asset_path in assets:
        asset = unreal.load_asset(asset_path)
        if asset:
            asset_type = asset.get_class().get_name()
            if asset_type not in asset_types:
                asset_types[asset_type] = []
            asset_types[asset_type].append(asset_path)
    
    for asset_type, paths in sorted(asset_types.items()):
        print(f"\n{asset_type} ({len(paths)} assets):")
        for path in paths[:3]:  # Show first 3 of each type
            print(f"  {path}")
        if len(paths) > 3:
            print(f"  ... and {len(paths) - 3} more")

print("\n" + "="*60)
print("SEARCH COMPLETE")
print("="*60 + "\n")
