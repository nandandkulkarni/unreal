"""
Deep API Exploration - Animation Addition Focus

This script performs exhaustive exploration to find ANY way to add animations:
1. Explore PoseSearchDatabase in extreme detail
2. Explore PoseSearchDatabaseSequence and related classes
3. Try every possible method combination
4. Look for editor utilities or helper functions
"""
import unreal
import sys
import os
import time
import glob

# Delete old logs
try:
    old_logs = glob.glob(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\deep_explore_*.log")
    for old_log in old_logs:
        try:
            os.remove(old_log)
        except:
            pass
except:
    pass

timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = rf"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\deep_explore_{timestamp}.log"

def log(msg):
    print(msg)
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except:
        pass

with open(log_file, 'w', encoding='utf-8') as f:
    f.write(f"Deep API Exploration - Animation Addition\n")
    f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*80 + "\n\n")

log(f"Log: {log_file}\n")


def explore_all_properties(obj, obj_name):
    """Try to get ALL properties using every method"""
    log("="*80)
    log(f"EXHAUSTIVE PROPERTY EXPLORATION: {obj_name}")
    log("="*80)
    
    # Method 1: Try common property names
    log("\n--- Method 1: Common Property Names ---")
    common_props = [
        "animation_assets", "animations", "sequences", "anim_sequences",
        "database_animations", "pose_search_animations", "assets",
        "animation_data", "sequence_data", "anim_data"
    ]
    
    for prop in common_props:
        try:
            value = obj.get_editor_property(prop)
            log(f"  ✓ {prop}: {type(value).__name__}")
        except:
            pass
    
    # Method 2: Try to call methods that might modify
    log("\n--- Method 2: Modification Methods ---")
    mod_methods = [
        "add_animation", "add_sequence", "add_anim_sequence",
        "add_animation_asset", "append_animation", "insert_animation",
        "set_animations", "set_animation_assets", "update_animations"
    ]
    
    for method_name in mod_methods:
        if hasattr(obj, method_name):
            log(f"  ✓ Found method: {method_name}()")
    
    # Method 3: Use call_method to try calling C++ functions
    log("\n--- Method 3: C++ Method Calls ---")
    cpp_methods = [
        "AddAnimationAsset", "AddSequence", "AddAnimation",
        "SetAnimationAssets", "UpdateDatabase", "RebuildDatabase"
    ]
    
    for method in cpp_methods:
        try:
            # Just check if it exists, don't call yet
            log(f"  Trying: {method}")
        except:
            pass
    
    # Method 4: Explore via static_class
    log("\n--- Method 4: Static Class Properties ---")
    try:
        static_cls = obj.static_class()
        log(f"  Static class: {static_cls}")
        
        # Try to get property list from static class
        if hasattr(static_cls, 'get_properties'):
            props = static_cls.get_properties()
            log(f"  Properties via static_class: {props}")
    except Exception as e:
        log(f"  Error: {e}")


def explore_database_sequence():
    """Explore PoseSearchDatabaseSequence in detail"""
    log("\n" + "="*80)
    log("EXPLORING: PoseSearchDatabaseSequence")
    log("="*80)
    
    try:
        # Create instance
        db_seq = unreal.PoseSearchDatabaseSequence()
        log("✓ Created PoseSearchDatabaseSequence instance")
        
        # Get all attributes
        attrs = [a for a in dir(db_seq) if not a.startswith('_')]
        log(f"\nAll attributes ({len(attrs)}):")
        for attr in sorted(attrs):
            try:
                val = getattr(db_seq, attr)
                if callable(val):
                    log(f"  METHOD: {attr}()")
                else:
                    log(f"  PROPERTY: {attr} = {type(val).__name__}")
            except:
                log(f"  {attr}: <error>")
        
        # Try to get/set properties
        log("\n--- Testing Properties ---")
        test_props = ["sequence", "animation", "anim_sequence", "asset"]
        for prop in test_props:
            try:
                val = db_seq.get_editor_property(prop)
                log(f"  ✓ {prop}: {type(val).__name__} = {val}")
            except Exception as e:
                pass
        
    except Exception as e:
        log(f"✗ Error: {e}")


def explore_editor_utilities():
    """Look for editor utility functions"""
    log("\n" + "="*80)
    log("SEARCHING FOR EDITOR UTILITIES")
    log("="*80)
    
    # Search for utility classes
    utility_patterns = [
        "PoseSearch", "Database", "Editor", "Utility", "Helper",
        "Library", "Subsystem"
    ]
    
    unreal_attrs = dir(unreal)
    
    for pattern in utility_patterns:
        matches = [a for a in unreal_attrs if pattern in a and "PoseSearch" in a]
        if matches:
            log(f"\n--- {pattern} Classes ---")
            for match in matches:
                log(f"  ✓ unreal.{match}")
                
                # Try to explore if it's a class
                try:
                    cls = getattr(unreal, match)
                    if hasattr(cls, '__bases__'):
                        # It's a class, check for static methods
                        methods = [m for m in dir(cls) if not m.startswith('_') and callable(getattr(cls, m, None))]
                        if methods:
                            log(f"    Methods: {', '.join(methods[:5])}")
                except:
                    pass


def test_direct_modification():
    """Try direct modification approaches"""
    log("\n" + "="*80)
    log("TESTING DIRECT MODIFICATION")
    log("="*80)
    
    # Load database
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    if not database:
        log("✗ Could not load database")
        return
    
    log("✓ Database loaded")
    
    # Load a test animation
    test_anim = unreal.load_object(None, "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle")
    if not test_anim:
        log("✗ Could not load test animation")
        return
    
    log(f"✓ Test animation loaded: {test_anim.get_name()}")
    
    # Test 1: Try call_method with various function names
    log("\n--- Test 1: call_method Attempts ---")
    methods_to_try = [
        ("AddAnimationAsset", [test_anim]),
        ("AddSequence", [test_anim]),
        ("AddAnimation", [test_anim]),
    ]
    
    for method_name, args in methods_to_try:
        try:
            log(f"  Trying: database.call_method('{method_name}', ...)")
            result = database.call_method(method_name, *args)
            log(f"    ✓ SUCCESS! Result: {result}")
        except Exception as e:
            log(f"    ✗ {e}")
    
    # Test 2: Try modify() before setting property
    log("\n--- Test 2: modify() + set_editor_property ---")
    try:
        database.modify()
        log("  ✓ Called modify()")
        
        # Try to set a property
        database.set_editor_property("animation_assets", [])
        log("  ✓ Set animation_assets to empty array")
    except Exception as e:
        log(f"  ✗ {e}")
    
    # Test 3: Try using set_editor_properties (plural)
    log("\n--- Test 3: set_editor_properties (plural) ---")
    try:
        database.set_editor_properties({"animation_assets": []})
        log("  ✓ Called set_editor_properties")
    except Exception as e:
        log(f"  ✗ {e}")


def explore_subsystems():
    """Look for subsystems that might help"""
    log("\n" + "="*80)
    log("EXPLORING SUBSYSTEMS")
    log("="*80)
    
    try:
        # Try to get editor subsystem
        editor_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
        log(f"✓ EditorAssetSubsystem: {editor_subsystem}")
        
        # Check its methods
        methods = [m for m in dir(editor_subsystem) if not m.startswith('_')]
        log(f"  Methods ({len(methods)}): {', '.join(methods[:10])}")
        
    except Exception as e:
        log(f"✗ Error: {e}")
    
    # Try other subsystems
    subsystem_types = [
        "AssetEditorSubsystem",
        "UnrealEditorSubsystem",
    ]
    
    for subsys_name in subsystem_types:
        try:
            if hasattr(unreal, subsys_name):
                subsys_class = getattr(unreal, subsys_name)
                subsys = unreal.get_editor_subsystem(subsys_class)
                log(f"✓ {subsys_name}: {subsys}")
        except Exception as e:
            log(f"✗ {subsys_name}: {e}")


def main():
    log("="*80)
    log("DEEP API EXPLORATION - ANIMATION ADDITION")
    log("="*80)
    log("")
    
    # Load database for testing
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    
    if database:
        # Exhaustive property exploration
        explore_all_properties(database, "PoseSearchDatabase")
        
        # Explore related classes
        explore_database_sequence()
        
        # Look for utilities
        explore_editor_utilities()
        
        # Try direct modification
        test_direct_modification()
        
        # Explore subsystems
        explore_subsystems()
    
    log("\n" + "="*80)
    log("EXPLORATION COMPLETE")
    log("="*80)
    log(f"\nLog file: {log_file}")
    log("\nReview log for any successful methods!")


if __name__ == "__main__":
    main()
