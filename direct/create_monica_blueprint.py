import unreal

print("\n" + "="*60)
print("CREATING MONICA BLUEPRINT FROM METAHUMAN ASSET")
print("="*60 + "\n")

# Load Monica's MetaHuman asset
monica_asset_path = "/Game/Fab/MetaHuman/MHC_Monica.MHC_Monica"
print(f"Loading Monica asset: {monica_asset_path}")

monica_asset = unreal.load_object(None, monica_asset_path)

if not monica_asset:
    print("✗ Failed to load Monica asset")
else:
    print(f"✓ Monica asset loaded: {monica_asset.get_name()}\n")
    
    # Try to create a Blueprint factory
    print("Attempting to create Blueprint from MetaHuman asset...")
    
    try:
        # Create blueprint factory
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", unreal.Actor)
        
        # Set output path for the new Blueprint
        blueprint_path = "/Game/Fab/MetaHuman/BP_Monica"
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        print(f"Creating Blueprint at: {blueprint_path}")
        
        # Create the Blueprint
        blueprint = asset_tools.create_asset(
            "BP_Monica",
            "/Game/Fab/MetaHuman",
            unreal.Blueprint,
            factory
        )
        
        if blueprint:
            print(f"✓ Blueprint created: {blueprint.get_name()}")
            print("\nNow trying to spawn the Blueprint...\n")
            
            # Spawn the Blueprint
            location = unreal.Vector(0, 0, 100)
            rotation = unreal.Rotator(0, 0, 0)
            
            actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
                blueprint,
                location,
                rotation
            )
            
            if actor:
                print(f"✓ SUCCESS! Spawned: {actor.get_name()}")
            else:
                print("✗ Failed to spawn Blueprint")
                print(f"But Blueprint exists at: {blueprint_path}")
                print("You can drag it into the level manually")
        else:
            print("✗ Failed to create Blueprint")
            
    except Exception as e:
        print(f"✗ Error creating Blueprint: {e}")
        print("\nTrying alternative method: Using EditorAssetLibrary...\n")
        
        try:
            # Alternative: Try to duplicate and convert
            new_path = "/Game/Fab/MetaHuman/BP_Monica_Generated"
            
            # This won't work directly but let's try
            success = unreal.EditorAssetLibrary.duplicate_asset(
                monica_asset_path,
                new_path
            )
            
            if success:
                print(f"✓ Asset duplicated to: {new_path}")
            else:
                print("✗ Duplication failed")
                
        except Exception as e2:
            print(f"✗ Alternative method also failed: {e2}")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("MetaHumanCharacter assets require special handling.")
print("\nManual method (easiest):")
print("  1. In main Unreal Editor, open Content Browser")
print("  2. Find MHC_Monica at /Game/Fab/MetaHuman/")
print("  3. RIGHT-CLICK on MHC_Monica")
print("  4. Look for 'Create Blueprint' or similar option")
print("  5. OR: Use File menu → Export → Blueprint")
print("\nIf manual method works, you'll have BP_Monica")
print("Then you can spawn it easily with Python!")
print("="*60 + "\n")
