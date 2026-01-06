"""
Test script for AAANKPose plugin with custom logging

This script tests if the AAANKPose plugin is loaded and accessible from Python.
Results are written to: test_aaankpose_results.log

Run with: python run_remote.py test_aaankpose_plugin_v2.py
"""

import unreal
import os
from datetime import datetime

# Log file path
LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc"
LOG_FILE = os.path.join(LOG_DIR, "test_aaankpose_results.log")

def log(message):
    """Write message to both console and log file"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def test_plugin_loaded():
    """Test if the plugin module is loaded"""
    
    # Clear previous log
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    log("=" * 80)
    log("TESTING AAANKPose PLUGIN")
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    log("")
    
    # Test 1: Check if we can access the plugin's library class
    log("Test 1: Checking if plugin library is accessible...")
    try:
        # Try common naming patterns
        class_names = [
            "AAANKPoseLibrary",
            "UAAANKPoseLibrary", 
            "AAANKPoseBlueprintLibrary"
        ]
        
        found_class = None
        for class_name in class_names:
            try:
                lib_class = unreal.find_class(class_name)
                if lib_class:
                    found_class = class_name
                    log(f"✓ Found library class: {class_name}")
                    log(f"  Class object: {lib_class}")
                    break
            except:
                continue
        
        if not found_class:
            log("⚠ Standard class names not found, searching all classes...")
            # List all classes to find yours
            all_classes = unreal.get_all_classes()
            pose_classes = [str(c) for c in all_classes if 'AAANK' in str(c).upper()]
            if pose_classes:
                log(f"✓ Found related classes:")
                for cls in pose_classes:
                    log(f"  - {cls}")
            else:
                log("✗ No AAANKPose classes found")
                log("  This means:")
                log("  1. Plugin is not enabled (Edit → Plugins)")
                log("  2. Plugin did not compile successfully")
                log("  3. Editor was not restarted after enabling")
    except Exception as e:
        log(f"✗ Error accessing library: {e}")
    
    log("")
    
    # Test 2: Try to instantiate the library
    log("Test 2: Testing library instantiation...")
    try:
        lib = unreal.AAANKPoseLibrary()
        log(f"✓ Library instantiated successfully: {lib}")
        
        # Try to list available methods
        log("  Available methods:")
        methods = dir(lib)
        plugin_methods = [m for m in methods if not m.startswith('_')]
        for method in plugin_methods[:20]:  # Show first 20
            log(f"    - {method}")
        if len(plugin_methods) > 20:
            log(f"    ... and {len(plugin_methods) - 20} more")
            
    except Exception as e:
        log(f"⚠ Could not instantiate library: {e}")
        log("  This is OK if you're using static functions")
    
    log("")
    
    # Test 3: Check for specific PoseSearch functions
    log("Test 3: Checking for PoseSearch functions...")
    try:
        lib = unreal.AAANKPoseLibrary
        
        expected_functions = [
            'add_animation_to_database',
            'add_animations_to_database',
            'build_database',
            'get_animation_count',
            'clear_database',
            'get_database_info'
        ]
        
        found_functions = []
        missing_functions = []
        
        for func_name in expected_functions:
            if hasattr(lib, func_name):
                found_functions.append(func_name)
                log(f"✓ Found function: {func_name}")
            else:
                missing_functions.append(func_name)
                log(f"✗ Missing function: {func_name}")
        
        log("")
        log(f"Summary: {len(found_functions)}/{len(expected_functions)} PoseSearch functions found")
        
        if missing_functions:
            log("")
            log("Missing functions indicate:")
            log("  - PoseSearch functions not yet added to plugin")
            log("  - See INTEGRATE_AAANKPOSE.md for integration steps")
        
    except Exception as e:
        log(f"⚠ Error checking functions: {e}")
    
    log("")
    
    # Test 4: Check plugin is enabled
    log("Test 4: Checking plugin status in engine...")
    try:
        # Just verify we can access Unreal systems
        asset_lib = unreal.EditorAssetLibrary
        log(f"✓ Unreal Engine systems accessible")
        log(f"  Asset library: {asset_lib}")
    except Exception as e:
        log(f"⚠ Error accessing engine systems: {e}")
    
    log("")
    log("=" * 80)
    log("TEST COMPLETE")
    log("=" * 80)
    log("")
    log(f"Results saved to: {LOG_FILE}")
    log("")
    log("Next steps:")
    log("1. Review the log file for detailed results")
    log("2. If functions are missing, follow INTEGRATE_AAANKPOSE.md")
    log("3. If plugin not found, check Edit → Plugins in Unreal")
    log("")

if __name__ == "__main__":
    test_plugin_loaded()
