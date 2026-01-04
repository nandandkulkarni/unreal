"""
Test C++ Plugin - PoseSearch Python Extensions

This script tests the C++ plugin functions
"""
import unreal

def test_cpp_plugin():
    print("="*80)
    print("Testing C++ Plugin - PoseSearch Python Extensions")
    print("="*80)
    
    # Load the library
    try:
        lib = unreal.PoseSearchPythonExtensionsLibrary()
        print("✓ Plugin library loaded")
    except Exception as e:
        print(f"✗ Could not load plugin library: {e}")
        print("\nMake sure:")
        print("1. Plugin is compiled")
        print("2. Plugin is enabled in Edit → Plugins")
        print("3. Editor has been restarted")
        return False
    
    # Load database
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    if not database:
        print("✗ Could not load database")
        return False
    print(f"✓ Database loaded: {database.get_name()}")
    
    # Test: Get database info
    try:
        info = lib.get_database_info(database)
        print(f"\nDatabase Info:\n{info}")
    except Exception as e:
        print(f"✗ get_database_info failed: {e}")
    
    # Test: Get animation count (before)
    try:
        count_before = lib.get_animation_count(database)
        print(f"\n✓ Animation count (before): {count_before}")
    except Exception as e:
        print(f"✗ get_animation_count failed: {e}")
        return False
    
    # Load test animation
    anim = unreal.load_object(None, "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle")
    if not anim:
        print("✗ Could not load test animation")
        return False
    print(f"✓ Test animation loaded: {anim.get_name()}")
    
    # Test: Add single animation
    try:
        success = lib.add_animation_to_database(database, anim)
        print(f"\n✓ Add animation: {success}")
    except Exception as e:
        print(f"✗ add_animation_to_database failed: {e}")
        print("\nThis might be due to:")
        print("1. Incorrect C++ implementation")
        print("2. UE version-specific API differences")
        print("3. Missing dependencies")
        return False
    
    # Test: Get animation count (after)
    try:
        count_after = lib.get_animation_count(database)
        print(f"✓ Animation count (after): {count_after}")
        
        if count_after > count_before:
            print(f"✓ Successfully added {count_after - count_before} animation(s)!")
        else:
            print("⚠ Animation count didn't increase - check implementation")
    except Exception as e:
        print(f"✗ get_animation_count failed: {e}")
    
    # Test: Build database
    try:
        built = lib.build_database(database)
        print(f"\n✓ Build database: {built}")
    except Exception as e:
        print(f"✗ build_database failed: {e}")
        return False
    
    # Test: Load multiple animations
    print("\n" + "="*80)
    print("Testing bulk animation addition")
    print("="*80)
    
    # Find animations
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    filter = unreal.ARFilter(
        class_names=["AnimSequence"],
        package_paths=["/Game/Characters/Mannequins/Anims/Unarmed"],
        recursive_paths=True
    )
    
    assets = asset_registry.get_assets(filter)
    animations = []
    
    for asset_data in assets[:5]:  # Test with first 5
        anim = asset_data.get_asset()
        if anim:
            animations.append(anim)
    
    print(f"Found {len(animations)} test animations")
    
    # Test: Add multiple animations
    if animations:
        try:
            added_count = lib.add_animations_to_database(database, animations)
            print(f"✓ Added {added_count}/{len(animations)} animations")
        except Exception as e:
            print(f"✗ add_animations_to_database failed: {e}")
    
    # Final count
    try:
        final_count = lib.get_animation_count(database)
        print(f"\n✓ Final animation count: {final_count}")
    except Exception as e:
        print(f"✗ get_animation_count failed: {e}")
    
    print("\n" + "="*80)
    print("✓ C++ PLUGIN TEST COMPLETE!")
    print("="*80)
    
    return True


if __name__ == "__main__":
    result = test_cpp_plugin()
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
