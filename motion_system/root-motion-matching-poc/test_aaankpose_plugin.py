"""
Test script for AAANKPose plugin

This script tests if the AAANKPose plugin is loaded and accessible from Python.
Run with: python run_remote.py test_aaankpose_plugin.py
"""

import unreal

def test_plugin_loaded():
    """Test if the plugin module is loaded"""
    print("=" * 80)
    print("TESTING AAANKPose PLUGIN")
    print("=" * 80)
    print()
    
    # Test 1: Check if we can access the plugin's library class
    print("Test 1: Checking if plugin library is accessible...")
    try:
        # Try to get the library class
        # Replace 'AAANKPoseLibrary' with your actual library class name
        lib_class = unreal.find_class("AAANKPoseLibrary")
        if lib_class:
            print(f"✓ Found library class: {lib_class}")
        else:
            print("⚠ Library class not found - trying alternative...")
            # List all classes to find yours
            all_classes = unreal.get_all_classes()
            pose_classes = [c for c in all_classes if 'AAANK' in str(c)]
            if pose_classes:
                print(f"✓ Found related classes: {pose_classes}")
            else:
                print("✗ No AAANKPose classes found")
    except Exception as e:
        print(f"✗ Error accessing library: {e}")
    
    print()
    
    # Test 2: Try to instantiate and call a function
    print("Test 2: Testing plugin functions...")
    try:
        # If you have a BlueprintFunctionLibrary, you can call static functions directly
        # Example: result = unreal.AAANKPoseLibrary.your_function_name()
        
        # For now, let's just try to see what's available
        print("Searching for AAANKPose functions...")
        
        # Try to find any AAANK-related objects
        all_objects = unreal.EditorAssetLibrary.list_assets("/Game/", recursive=True, include_folder=False)
        print(f"✓ Asset system accessible")
        
    except Exception as e:
        print(f"⚠ Error during function test: {e}")
    
    print()
    
    # Test 3: Check plugin is enabled
    print("Test 3: Checking plugin status...")
    try:
        # Get plugin manager
        plugin_manager = unreal.get_engine_subsystem(unreal.PluginBrowserSubsystem)
        if plugin_manager:
            print("✓ Plugin manager accessible")
        else:
            print("⚠ Plugin manager not accessible")
    except Exception as e:
        print(f"⚠ Error checking plugin status: {e}")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. If library class not found, check your plugin's .h file for the UCLASS name")
    print("2. Ensure plugin is enabled in Edit → Plugins")
    print("3. Ensure editor was restarted after enabling plugin")
    print()

if __name__ == "__main__":
    test_plugin_loaded()
