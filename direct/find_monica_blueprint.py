import unreal

print("\n" + "="*60)
print("FINDING MONICA'S BLUEPRINT")
print("="*60 + "\n")

# Search for any Blueprint or spawnable version of Monica
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
all_assets = asset_registry.get_all_assets()

print("Searching for Monica-related Blueprints...\n")

monica_blueprints = []
for asset in all_assets:
    asset_name = str(asset.asset_name).lower()
    package_name = str(asset.package_name).lower()
    
    if 'monica' in asset_name or 'monica' in package_name:
        asset_class = str(asset.asset_class_path.asset_name)
        # Look for Blueprint classes
        if 'Blueprint' in asset_class or asset_class == 'BlueprintGeneratedClass':
            monica_blueprints.append(asset)
            print(f"Found: {asset.package_name}.{asset.asset_name}")
            print(f"  Type: {asset_class}\n")

if not monica_blueprints:
    print("⚠ No Monica Blueprint found")
    print("\nThe MetaHumanCharacter asset needs to be converted to a Blueprint.")
    print("\nTo create a spawnable Monica Blueprint:")
    print("  1. In Content Browser, right-click on MHC_Monica")
    print("  2. Select 'Create Blueprint' or 'Create MetaHuman Blueprint'")
    print("  3. Name it 'BP_Monica'")
    print("  4. Save the Blueprint")
    print("  5. Then you can spawn it with Python\n")
    
    print("Alternatively, try dragging Monica directly into the viewport:")
    print("  1. Open Content Browser")
    print("  2. Navigate to /Game/Fab/MetaHuman/")
    print("  3. Drag MHC_Monica into the viewport")
    print("  4. Unreal will create a Blueprint automatically\n")
else:
    print(f"✓ Found {len(monica_blueprints)} Monica Blueprint(s)")
    print("\nTrying to spawn the first Blueprint...\n")
    
    # Try to spawn the first blueprint found
    first_bp_asset = monica_blueprints[0]
    bp_path = f"{first_bp_asset.package_name}.{first_bp_asset.asset_name}"
    
    print(f"Loading: {bp_path}")
    bp = unreal.load_object(None, bp_path)
    
    if bp:
        print(f"✓ Blueprint loaded: {bp.get_name()}\n")
        
        # Spawn it
        location = unreal.Vector(0, 0, 100)
        rotation = unreal.Rotator(0, 0, 0)
        
        print("Spawning Monica...")
        actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
            bp,
            location,
            rotation
        )
        
        if actor:
            print(f"✓ SUCCESS! Monica spawned: {actor.get_name()}\n")
            
            # Inspect components
            skel_comps = actor.get_components_by_class(unreal.SkeletalMeshComponent)
            print(f"Components found: {len(skel_comps)} skeletal mesh components")
            
            for comp in skel_comps:
                print(f"  - {comp.get_name()}")
        else:
            print("✗ Failed to spawn from Blueprint")

print("\n" + "="*60)
print("SEARCH COMPLETE")
print("="*60 + "\n")
