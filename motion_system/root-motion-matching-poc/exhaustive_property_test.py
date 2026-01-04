"""
Exhaustive Animation Assets Property Test

This script tries EVERY possible way to access and modify animation_assets:
- Different property names
- Different access methods
- Different data structures
- Different wrapper approaches
- All combinations
"""
import unreal
import sys
import os
import time
import glob

# Delete old logs
try:
    old_logs = glob.glob(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\exhaustive_test_*.log")
    for old_log in old_logs:
        try:
            os.remove(old_log)
        except:
            pass
except:
    pass

timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = rf"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\exhaustive_test_{timestamp}.log"

def log(msg):
    print(msg)
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except:
        pass

with open(log_file, 'w', encoding='utf-8') as f:
    f.write(f"Exhaustive Animation Assets Property Test\n")
    f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*80 + "\n\n")

log(f"Log: {log_file}\n")


def test_all_property_names(database):
    """Test all possible property name variations"""
    log("="*80)
    log("TEST 1: All Property Name Variations")
    log("="*80)
    
    property_names = [
        # Documented names
        "animation_assets",
        "AnimationAssets",
        "ANIMATION_ASSETS",
        
        # UE 5.0 names
        "sequences",
        "Sequences",
        "simple_sequences",
        "SimpleSequences",
        
        # Possible variations
        "anim_assets",
        "AnimAssets",
        "animation_sequences",
        "AnimationSequences",
        "database_sequences",
        "DatabaseSequences",
        
        # Internal names
        "_animation_assets",
        "m_animation_assets",
        "AnimationAssetsInternal",
    ]
    
    for prop_name in property_names:
        try:
            value = database.get_editor_property(prop_name)
            log(f"  ✓ SUCCESS: {prop_name} = {type(value).__name__}")
            log(f"    Value: {value}")
            return prop_name, value  # Return first success
        except Exception as e:
            log(f"  ✗ {prop_name}: {str(e)[:80]}")
    
    return None, None


def test_all_access_methods(database):
    """Test all possible ways to access properties"""
    log("\n" + "="*80)
    log("TEST 2: All Access Methods")
    log("="*80)
    
    methods = [
        ("get_editor_property", lambda db, name: db.get_editor_property(name)),
        ("getattr", lambda db, name: getattr(db, name)),
        ("__dict__", lambda db, name: db.__dict__.get(name)),
        ("get", lambda db, name: getattr(db, 'get', lambda x: None)(name)),
    ]
    
    for method_name, method_func in methods:
        log(f"\n--- Method: {method_name} ---")
        for prop_name in ["animation_assets", "sequences", "simple_sequences"]:
            try:
                value = method_func(database, prop_name)
                log(f"  ✓ {method_name}('{prop_name}') = {type(value).__name__}")
                if value is not None:
                    log(f"    Value: {value}")
                    return method_name, prop_name, value
            except Exception as e:
                log(f"  ✗ {method_name}('{prop_name}'): {str(e)[:60]}")
    
    return None, None, None


def test_direct_attribute_access(database):
    """Test direct attribute access"""
    log("\n" + "="*80)
    log("TEST 3: Direct Attribute Access")
    log("="*80)
    
    # List all attributes
    attrs = [a for a in dir(database) if not a.startswith('__')]
    log(f"\nAll attributes ({len(attrs)}):")
    
    # Look for animation-related attributes
    anim_attrs = [a for a in attrs if 'anim' in a.lower() or 'seq' in a.lower()]
    log(f"\nAnimation-related attributes ({len(anim_attrs)}):")
    for attr in anim_attrs:
        try:
            value = getattr(database, attr)
            if not callable(value):
                log(f"  ✓ {attr} = {type(value).__name__}")
        except Exception as e:
            log(f"  ✗ {attr}: {str(e)[:60]}")


def test_set_methods(database, test_anim):
    """Test all possible ways to set/add animations"""
    log("\n" + "="*80)
    log("TEST 4: All Set/Add Methods")
    log("="*80)
    
    # Create test data structures
    db_seq = unreal.PoseSearchDatabaseSequence()
    db_seq.set_editor_property("sequence", test_anim)
    
    # Test 1: set_editor_property with different structures
    log("\n--- Test 4.1: set_editor_property variations ---")
    test_structures = [
        ("Empty list", []),
        ("List with PoseSearchDatabaseSequence", [db_seq]),
        ("Tuple with PoseSearchDatabaseSequence", (db_seq,)),
        ("Single PoseSearchDatabaseSequence", db_seq),
        ("List with AnimSequence", [test_anim]),
    ]
    
    for desc, structure in test_structures:
        for prop_name in ["animation_assets", "sequences", "simple_sequences"]:
            try:
                database.set_editor_property(prop_name, structure)
                log(f"  ✓ SUCCESS: set_editor_property('{prop_name}', {desc})")
                # Verify
                count = database.get_num_animation_assets()
                log(f"    New count: {count}")
                return True
            except Exception as e:
                log(f"  ✗ set_editor_property('{prop_name}', {desc}): {str(e)[:60]}")
    
    # Test 2: set_editor_properties (plural)
    log("\n--- Test 4.2: set_editor_properties (plural) ---")
    for prop_name in ["animation_assets", "sequences", "simple_sequences"]:
        try:
            database.set_editor_properties({prop_name: [db_seq]})
            log(f"  ✓ SUCCESS: set_editor_properties({{'{prop_name}': [...]}})")
            count = database.get_num_animation_assets()
            log(f"    New count: {count}")
            return True
        except Exception as e:
            log(f"  ✗ set_editor_properties({{'{prop_name}': ...}}): {str(e)[:60]}")
    
    # Test 3: Direct attribute assignment
    log("\n--- Test 4.3: Direct attribute assignment ---")
    for prop_name in ["animation_assets", "sequences", "simple_sequences"]:
        try:
            setattr(database, prop_name, [db_seq])
            log(f"  ✓ SUCCESS: setattr(database, '{prop_name}', [...])")
            count = database.get_num_animation_assets()
            log(f"    New count: {count}")
            return True
        except Exception as e:
            log(f"  ✗ setattr(database, '{prop_name}', ...): {str(e)[:60]}")
    
    return False


def test_call_method_variations(database, test_anim):
    """Test call_method with all variations"""
    log("\n" + "="*80)
    log("TEST 5: call_method Variations")
    log("="*80)
    
    db_seq = unreal.PoseSearchDatabaseSequence()
    db_seq.set_editor_property("sequence", test_anim)
    
    # Method names to try
    method_names = [
        "AddAnimationAsset",
        "AddAnimation",
        "AddSequence",
        "AddAnimSequence",
        "AppendAnimation",
        "InsertAnimation",
        "PushAnimation",
        "add_animation_asset",
        "add_animation",
        "add_sequence",
    ]
    
    # Argument variations
    arg_variations = [
        ("PoseSearchDatabaseSequence", (db_seq,)),
        ("AnimSequence", (test_anim,)),
        ("PoseSearchDatabaseSequence, index", (db_seq, 0)),
        ("AnimSequence, index", (test_anim, 0)),
    ]
    
    for method_name in method_names:
        for arg_desc, args in arg_variations:
            try:
                result = database.call_method(method_name, *args)
                log(f"  ✓ SUCCESS: call_method('{method_name}', {arg_desc})")
                log(f"    Result: {result}")
                count = database.get_num_animation_assets()
                log(f"    New count: {count}")
                return True
            except Exception as e:
                log(f"  ✗ call_method('{method_name}', {arg_desc}): {str(e)[:60]}")
    
    return False


def test_modify_then_set(database, test_anim):
    """Test calling modify() before setting"""
    log("\n" + "="*80)
    log("TEST 6: modify() + set Combinations")
    log("="*80)
    
    db_seq = unreal.PoseSearchDatabaseSequence()
    db_seq.set_editor_property("sequence", test_anim)
    
    # Test with modify() first
    try:
        database.modify()
        log("  ✓ Called modify()")
        
        # Now try setting
        for prop_name in ["animation_assets", "sequences", "simple_sequences"]:
            try:
                database.set_editor_property(prop_name, [db_seq])
                log(f"  ✓ SUCCESS: modify() + set_editor_property('{prop_name}')")
                count = database.get_num_animation_assets()
                log(f"    New count: {count}")
                return True
            except Exception as e:
                log(f"  ✗ modify() + set_editor_property('{prop_name}'): {str(e)[:60]}")
    except Exception as e:
        log(f"  ✗ modify() failed: {e}")
    
    return False


def test_instanced_struct_variations(database, test_anim):
    """Test InstancedStruct with all variations"""
    log("\n" + "="*80)
    log("TEST 7: InstancedStruct Variations")
    log("="*80)
    
    db_seq = unreal.PoseSearchDatabaseSequence()
    db_seq.set_editor_property("sequence", test_anim)
    
    # Test 1: Create InstancedStruct
    try:
        instanced = unreal.InstancedStruct()
        log("  ✓ Created InstancedStruct")
        
        # Try different ways to set the value
        set_methods = [
            ("set_editor_property('value', ...)", lambda: instanced.set_editor_property("value", db_seq)),
            ("setattr(..., 'value', ...)", lambda: setattr(instanced, "value", db_seq)),
            ("set_editor_property('struct_value', ...)", lambda: instanced.set_editor_property("struct_value", db_seq)),
            ("set_editor_property('data', ...)", lambda: instanced.set_editor_property("data", db_seq)),
        ]
        
        for desc, method in set_methods:
            try:
                method()
                log(f"  ✓ {desc} succeeded")
                
                # Try to add to database
                try:
                    database.set_editor_property("animation_assets", [instanced])
                    log(f"    ✓ SUCCESS: Added InstancedStruct to database!")
                    count = database.get_num_animation_assets()
                    log(f"    New count: {count}")
                    return True
                except Exception as e:
                    log(f"    ✗ Could not add to database: {str(e)[:60]}")
            except Exception as e:
                log(f"  ✗ {desc}: {str(e)[:60]}")
    except Exception as e:
        log(f"  ✗ Could not create InstancedStruct: {e}")
    
    return False


def main():
    log("="*80)
    log("EXHAUSTIVE ANIMATION ASSETS PROPERTY TEST")
    log("="*80)
    log("")
    
    # Load database
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    if not database:
        log("✗ Could not load database")
        return False
    log("✓ Database loaded\n")
    
    # Load test animation
    test_anim = unreal.load_object(None, "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle")
    if not test_anim:
        log("✗ Could not load test animation")
        return False
    log("✓ Test animation loaded\n")
    
    # Run all tests
    success = False
    
    # Test 1: Property names
    prop_name, value = test_all_property_names(database)
    if prop_name:
        log(f"\n🎉 FOUND WORKING PROPERTY: {prop_name}")
        success = True
    
    # Test 2: Access methods
    method, prop, value = test_all_access_methods(database)
    if method:
        log(f"\n🎉 FOUND WORKING METHOD: {method}('{prop}')")
        success = True
    
    # Test 3: Direct attributes
    test_direct_attribute_access(database)
    
    # Test 4: Set methods
    if test_set_methods(database, test_anim):
        log("\n🎉 FOUND WORKING SET METHOD!")
        success = True
    
    # Test 5: call_method variations
    if test_call_method_variations(database, test_anim):
        log("\n🎉 FOUND WORKING call_method!")
        success = True
    
    # Test 6: modify() combinations
    if test_modify_then_set(database, test_anim):
        log("\n🎉 FOUND WORKING modify() + set combination!")
        success = True
    
    # Test 7: InstancedStruct variations
    if test_instanced_struct_variations(database, test_anim):
        log("\n🎉 FOUND WORKING InstancedStruct method!")
        success = True
    
    # Summary
    log("\n" + "="*80)
    log("TEST COMPLETE")
    log("="*80)
    log(f"Result: {'SUCCESS - Found working method!' if success else 'FAILED - No working method found'}")
    log(f"\nLog file: {log_file}")
    
    return success


if __name__ == "__main__":
    result = main()
    log(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
