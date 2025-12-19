import unreal

print("\n" + "="*60)
print("SPAWNING MONICA METAHUMAN")
print("="*60 + "\n")

# Step 1: Load Monica's MetaHumanCharacter asset
print("[STEP 1] Loading Monica MetaHuman asset...")
monica_path = "/Game/Fab/MetaHuman/MHC_Monica.MHC_Monica"
monica_asset = unreal.load_object(None, monica_path)

if not monica_asset:
    print(f"✗ Failed to load Monica from: {monica_path}")
    print("Make sure Monica is properly imported from Fab")
else:
    print(f"✓ Monica loaded: {monica_asset.get_name()}")
    print(f"  Asset type: {monica_asset.get_class().get_name()}\n")
    
    # Step 2: Define spawn location
    print("[STEP 2] Defining spawn parameters...")
    spawn_location = unreal.Vector(0.0, 0.0, 100.0)
    spawn_rotation = unreal.Rotator(0.0, 0.0, 0.0)
    
    print(f"✓ Spawn location: X={spawn_location.x}, Y={spawn_location.y}, Z={spawn_location.z}")
    print(f"✓ Spawn rotation: Pitch={spawn_rotation.pitch}, Yaw={spawn_rotation.yaw}, Roll={spawn_rotation.roll}\n")
    
    # Step 3: Spawn Monica
    print("[STEP 3] Spawning Monica in the level...")
    
    # Try spawning with spawn_actor_from_object
    monica_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
        monica_asset,
        spawn_location,
        spawn_rotation
    )
    
    if monica_actor:
        print(f"✓ Monica spawned: {monica_actor.get_name()}")
        print(f"  Actor class: {monica_actor.get_class().get_name()}\n")
        
        # Step 4: Inspect Monica's components
        print("[STEP 4] Inspecting Monica's components...")
        print("-" * 60)
        
        all_components = monica_actor.get_components_by_class(unreal.ActorComponent)
        print(f"Total components: {len(all_components)}\n")
        
        # Find skeletal mesh components
        skel_components = monica_actor.get_components_by_class(unreal.SkeletalMeshComponent)
        print(f"Skeletal Mesh Components: {len(skel_components)}")
        
        for i, comp in enumerate(skel_components, 1):
            print(f"\n  Component {i}: {comp.get_name()}")
            print(f"    Class: {comp.get_class().get_name()}")
            
            # Get the skeletal mesh
            try:
                skel_mesh = comp.skeletal_mesh_asset if hasattr(comp, 'skeletal_mesh_asset') else None
                if skel_mesh:
                    print(f"    Skeletal Mesh: {skel_mesh.get_path_name()}")
                else:
                    print(f"    Skeletal Mesh: None")
            except:
                print(f"    Skeletal Mesh: Could not retrieve")
            
            # Get animation blueprint
            try:
                anim_mode = comp.get_animation_mode()
                print(f"    Animation Mode: {anim_mode}")
            except:
                pass
        
        # Summary
        print("\n" + "="*60)
        print("MONICA SPAWNED SUCCESSFULLY!")
        print("="*60)
        print(f"Actor Name:     {monica_actor.get_name()}")
        print(f"Actor Class:    {monica_actor.get_class().get_name()}")
        print(f"Location:       {spawn_location}")
        print(f"Components:     {len(all_components)} total")
        print(f"Body Parts:     {len(skel_components)} skeletal meshes")
        print("="*60 + "\n")
        
        print("✓ Monica is now in your level!")
        print("  You can find her in the World Outliner")
        print("  Select her to see all her components in the Details panel\n")
        
    else:
        print("✗ Failed to spawn Monica")
        print("\nTroubleshooting:")
        print("  1. Monica asset exists but may not be spawnable")
        print("  2. Try dragging Monica from Content Browser into the level manually")
        print("  3. MetaHumanCharacter assets may need special handling\n")

print("="*60)
print("SPAWN COMPLETE")
print("="*60 + "\n")
