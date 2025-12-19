import unreal

print("\n" + "="*60)
print("SEARCHING FOR ALL METAHUMAN AND CHARACTER ASSETS")
print("="*60 + "\n")

# Get asset registry
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

print("Getting all assets (this may take a moment)...\n")
all_assets = asset_registry.get_all_assets()

# Search common Fab/Marketplace locations
search_terms = ["metahuman", "monica", "fab", "mhc"]

print("-" * 60)
print("SEARCHING FOR ASSETS...")
print("-" * 60)

found_assets = []
for term in search_terms:
    matches = [a for a in all_assets if term in str(a.package_name).lower()]
    found_assets.extend(matches)
    print(f"  '{term}': {len(matches)} matches")

# Remove duplicates by package_name
seen = set()
unique_assets = []
for a in found_assets:
    if a.package_name not in seen:
        seen.add(a.package_name)
        unique_assets.append(a)
found_assets = unique_assets

print(f"\nTotal unique assets found: {len(found_assets)}\n")

if found_assets:
    # Show unique folder paths
    print("-" * 60)
    print("ASSET FOLDERS FOUND:")
    print("-" * 60)
    paths = set(str(a.package_path) for a in found_assets)
    for path in sorted(paths):
        print(f"  {path}")
    
    # Filter skeletal meshes
    print("\n" + "-" * 60)
    print("SKELETAL MESHES:")
    print("-" * 60)
    skeletal_meshes = [a for a in found_assets if str(a.asset_class_path.asset_name) == "SkeletalMesh"]
    if skeletal_meshes:
        for asset in skeletal_meshes[:10]:  # Show first 10
            print(f"  {asset.package_name}.{asset.asset_name}")
    else:
        print("  None found")
    
    # Filter animation blueprints
    print("\n" + "-" * 60)
    print("ANIMATION BLUEPRINTS:")
    print("-" * 60)
    anim_bps = [a for a in found_assets if "Blueprint" in str(a.asset_class_path.asset_name)]
    if anim_bps:
        for asset in anim_bps[:10]:  # Show first 10
            print(f"  {asset.package_name}.{asset.asset_name}")
    else:
        print("  None found")

else:
    print("\n⚠ No MetaHuman or Monica assets found!")
    print("\nPossible reasons:")
    print("  1. Assets are still importing from Fab")
    print("  2. Project needs to be saved/restarted")
    print("  3. Assets were added to a different project")
    print("\nShowing all top-level folders in /Game:")
    print("-" * 60)
    game_paths = set()
    for a in all_assets:
        path = str(a.package_path)
        if path.startswith("/Game/"):
            parts = path.split("/")
            if len(parts) >= 3:
                game_paths.add("/".join(parts[:3]))
    
    for folder in sorted(game_paths)[:30]:
        print(f"  {folder}")

print("\n" + "="*60)
print("SEARCH COMPLETE")
print("="*60 + "\n")
