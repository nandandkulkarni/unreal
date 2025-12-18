"""
Diagnose mannequin spawning to check if it has a skeletal mesh component.
This script is pure Unreal Python and should be run through unreal_connection.py
"""

import unreal

def main():
    print("\n" + "=" * 70)
    print("MANNEQUIN DIAGNOSTIC SCRIPT")
    print("=" * 70)
    
    # Try loading the blueprint
    blueprint_path = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C"
    print(f"\n1. Loading blueprint: {blueprint_path}")
    
    mannequin_class = unreal.load_object(None, blueprint_path)
    
    if not mannequin_class:
        print(f"✗ ERROR: Could not load blueprint at {blueprint_path}")
        return
    
    print(f"✓ Blueprint loaded successfully")
    print(f"  Type: {type(mannequin_class)}")
    print(f"  Name: {mannequin_class.get_name()}")
    
    # Spawn the actor
    print("\n2. Spawning actor...")
    location = unreal.Vector(0, 0, 0)
    rotation = unreal.Rotator(0, 0, 0)
    
    mannequin = unreal.EditorLevelLibrary.spawn_actor_from_class(
        mannequin_class,
        location,
        rotation
    )
    
    if not mannequin:
        print("✗ ERROR: Failed to spawn actor")
        return
    
    print(f"✓ Actor spawned successfully")
    print(f"  Type: {type(mannequin)}")
    print(f"  Name: {mannequin.get_name()}")
    print(f"  Label: {mannequin.get_actor_label()}")
    
    # Check components
    print("\n3. Checking components...")
    components = mannequin.get_components_by_class(unreal.ActorComponent)
    print(f"  Total components: {len(components)}")
    
    for i, component in enumerate(components):
        print(f"  [{i}] {component.get_name()} - Type: {type(component).__name__}")
    
    # Check for skeletal mesh component specifically
    print("\n4. Checking for SkeletalMeshComponent...")
    skeletal_mesh_components = mannequin.get_components_by_class(unreal.SkeletalMeshComponent)
    
    if skeletal_mesh_components:
        print(f"✓ Found {len(skeletal_mesh_components)} SkeletalMeshComponent(s)")
        
        for i, skel_comp in enumerate(skeletal_mesh_components):
            print(f"\n  SkeletalMeshComponent [{i}]: {skel_comp.get_name()}")
            
            # Check if it has a skeletal mesh assigned
            skel_mesh = skel_comp.get_editor_property('skeletal_mesh')
            if skel_mesh:
                print(f"    ✓ Skeletal Mesh assigned: {skel_mesh.get_name()}")
                print(f"      Path: {skel_mesh.get_path_name()}")
            else:
                print(f"    ✗ NO Skeletal Mesh assigned!")
                print(f"    ⚠ This is why the mannequin is invisible!")
            
            # Check materials
            materials = skel_comp.get_materials()
            if materials:
                print(f"    Materials: {len(materials)} material slots")
                for j, mat in enumerate(materials):
                    if mat:
                        print(f"      [{j}] {mat.get_name()}")
                    else:
                        print(f"      [{j}] None")
            else:
                print(f"    Materials: None")
    else:
        print("✗ NO SkeletalMeshComponent found!")
        print("  This explains why mannequin has no shape.")
    
    # Check for static mesh component as fallback
    print("\n5. Checking for StaticMeshComponent (fallback)...")
    static_mesh_components = mannequin.get_components_by_class(unreal.StaticMeshComponent)
    
    if static_mesh_components:
        print(f"  Found {len(static_mesh_components)} StaticMeshComponent(s)")
    else:
        print("  No StaticMeshComponent found")
    
    # Try to get the skeletal mesh from the blueprint CDO (Class Default Object)
    print("\n6. Checking blueprint default components...")
    try:
        cdo = unreal.get_default_object(mannequin_class)
        if cdo:
            print(f"✓ Got CDO: {cdo.get_name()}")
            cdo_components = cdo.get_components_by_class(unreal.SkeletalMeshComponent)
            if cdo_components:
                print(f"  CDO has {len(cdo_components)} SkeletalMeshComponent(s)")
                for comp in cdo_components:
                    skel_mesh = comp.get_editor_property('skeletal_mesh')
                    if skel_mesh:
                        print(f"    Default mesh: {skel_mesh.get_name()}")
                        print(f"    Path: {skel_mesh.get_path_name()}")
            else:
                print("  CDO has no SkeletalMeshComponent")
    except Exception as e:
        print(f"  ⚠ Could not get CDO: {e}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
