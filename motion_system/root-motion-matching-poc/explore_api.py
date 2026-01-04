"""
Systematic API Exploration for PoseSearch

This script uses reflection to discover the actual Python API for:
1. PoseSearchSchema - channels and configuration
2. PoseSearchDatabase - animations and building
3. Related classes and methods

We'll systematically explore what's actually available.
"""
import unreal
import sys
import os
import time
import glob

# Delete old log files
try:
    old_logs = glob.glob(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\api_exploration_*.log")
    for old_log in old_logs:
        try:
            os.remove(old_log)
        except:
            pass
except:
    pass

# Create timestamped log file
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = rf"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\api_exploration_{timestamp}.log"

def log(msg):
    """Write to both console and log file"""
    print(msg)
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except:
        pass

# Initialize log
with open(log_file, 'w', encoding='utf-8') as f:
    f.write(f"PoseSearch API Exploration\n")
    f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*80 + "\n\n")

log(f"Log file: {log_file}\n")


def explore_class(cls, class_name):
    """Explore a class and log all its attributes and methods"""
    log("="*80)
    log(f"EXPLORING: {class_name}")
    log("="*80)
    
    # Get all attributes
    attrs = dir(cls)
    
    # Categorize attributes
    properties = []
    methods = []
    special = []
    
    for attr in attrs:
        if attr.startswith('__'):
            special.append(attr)
        elif callable(getattr(cls, attr, None)):
            methods.append(attr)
        else:
            properties.append(attr)
    
    log(f"\nTotal attributes: {len(attrs)}")
    log(f"Properties: {len(properties)}")
    log(f"Methods: {len(methods)}")
    log(f"Special: {len(special)}")
    
    # Log properties
    if properties:
        log("\n--- PROPERTIES ---")
        for prop in sorted(properties):
            try:
                value = getattr(cls, prop)
                log(f"  {prop}: {type(value).__name__}")
            except:
                log(f"  {prop}: <error accessing>")
    
    # Log methods
    if methods:
        log("\n--- METHODS ---")
        for method in sorted(methods):
            try:
                func = getattr(cls, method)
                # Try to get signature
                log(f"  {method}()")
            except:
                log(f"  {method}: <error accessing>")
    
    log("")


def explore_instance(obj, obj_name):
    """Explore an instance and its editor properties"""
    log("="*80)
    log(f"EXPLORING INSTANCE: {obj_name}")
    log("="*80)
    
    log(f"Type: {type(obj).__name__}")
    log(f"Class: {obj.__class__.__name__}")
    
    # Try to get editor properties
    log("\n--- EDITOR PROPERTIES (via get_editor_property) ---")
    
    # Common property names to try
    common_props = [
        "channels", "schema", "skeleton", "animation_assets", "animations",
        "sequences", "database", "bones", "trajectory", "sample_times",
        "weights", "name", "asset_name"
    ]
    
    for prop_name in common_props:
        try:
            value = obj.get_editor_property(prop_name)
            log(f"  ✓ {prop_name}: {type(value).__name__} = {value if not isinstance(value, (list, tuple)) or len(value) < 5 else f'[{len(value)} items]'}")
        except Exception as e:
            # log(f"  ✗ {prop_name}: {e}")
            pass
    
    # Try to list all editor properties
    log("\n--- ALL EDITOR PROPERTIES (via reflection) ---")
    try:
        # Get the class
        cls = obj.__class__
        
        # Try different approaches to get properties
        if hasattr(cls, 'get_editor_properties'):
            props = cls.get_editor_properties()
            log(f"  Found {len(props)} properties via get_editor_properties()")
            for prop in props:
                log(f"    - {prop}")
        
        # Try static_class approach
        if hasattr(obj, 'static_class'):
            static_cls = obj.static_class()
            log(f"  Static class: {static_cls}")
    except Exception as e:
        log(f"  Could not enumerate properties: {e}")
    
    log("")


def explore_posesearch_classes():
    """Explore all PoseSearch-related classes"""
    log("="*80)
    log("DISCOVERING POSESEARCH CLASSES")
    log("="*80)
    
    # Get all attributes from unreal module
    unreal_attrs = dir(unreal)
    
    # Find PoseSearch-related classes
    posesearch_classes = [
        attr for attr in unreal_attrs 
        if 'PoseSearch' in attr or 'MotionMatching' in attr
    ]
    
    log(f"\nFound {len(posesearch_classes)} PoseSearch-related classes:\n")
    for cls_name in sorted(posesearch_classes):
        try:
            cls = getattr(unreal, cls_name)
            log(f"  ✓ unreal.{cls_name}")
        except:
            log(f"  ✗ unreal.{cls_name} (error loading)")
    
    log("")
    return posesearch_classes


def test_schema_modification():
    """Test different approaches to modify schema"""
    log("="*80)
    log("TESTING SCHEMA MODIFICATION")
    log("="*80)
    
    # Load schema
    schema = unreal.load_object(None, "/Game/MotionMatching/MannyMotionSchema")
    if not schema:
        log("✗ Could not load schema")
        return
    
    log("✓ Schema loaded\n")
    
    # Test 1: Try to get channels
    log("Test 1: Getting channels array")
    try:
        channels = schema.get_editor_property("channels")
        log(f"  ✓ Got channels: {type(channels).__name__}, length: {len(channels) if channels else 0}")
        
        if channels:
            for i, ch in enumerate(channels):
                log(f"    Channel {i}: {type(ch).__name__}")
    except Exception as e:
        log(f"  ✗ Error: {e}")
    
    # Test 2: Try to create a channel
    log("\nTest 2: Creating channel instances")
    
    channel_types = [
        "PoseSearchFeatureChannel",
        "PoseSearchFeatureChannel_Position",
        "PoseSearchFeatureChannel_Velocity",
        "PoseSearchFeatureChannel_Trajectory",
    ]
    
    for ch_type in channel_types:
        try:
            if hasattr(unreal, ch_type):
                ch_class = getattr(unreal, ch_type)
                instance = ch_class()
                log(f"  ✓ Created {ch_type} instance")
                
                # Explore the instance
                log(f"    Attributes: {[a for a in dir(instance) if not a.startswith('_')][:10]}")
        except Exception as e:
            log(f"  ✗ {ch_type}: {e}")
    
    # Test 3: Try to modify channels array
    log("\nTest 3: Modifying channels array")
    try:
        channels = schema.get_editor_property("channels")
        if channels is None:
            channels = []
        
        log(f"  Current channels: {len(channels)}")
        
        # Try to append
        # We'll try this in the next iteration after exploring channel creation
        
    except Exception as e:
        log(f"  ✗ Error: {e}")
    
    log("")


def test_database_modification():
    """Test different approaches to modify database"""
    log("="*80)
    log("TESTING DATABASE MODIFICATION")
    log("="*80)
    
    # Load database
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    if not database:
        log("✗ Could not load database")
        return
    
    log("✓ Database loaded\n")
    
    # Test 1: Explore database methods
    log("Test 1: Database methods")
    db_methods = [m for m in dir(database) if not m.startswith('_') and callable(getattr(database, m, None))]
    log(f"  Found {len(db_methods)} methods:")
    for method in sorted(db_methods)[:20]:  # Show first 20
        log(f"    - {method}()")
    
    # Test 2: Look for build-related methods
    log("\nTest 2: Build-related methods")
    build_methods = [m for m in db_methods if 'build' in m.lower() or 'index' in m.lower() or 'compile' in m.lower()]
    if build_methods:
        log(f"  Found {len(build_methods)} build-related methods:")
        for method in build_methods:
            log(f"    ✓ {method}()")
    else:
        log("  ✗ No build methods found")
    
    # Test 3: Try to call potential build methods
    log("\nTest 3: Attempting to call build methods")
    for method_name in ['build', 'rebuild', 'build_index', 'compile', 'generate']:
        if hasattr(database, method_name):
            try:
                method = getattr(database, method_name)
                log(f"  Found {method_name}(), attempting to call...")
                # Don't actually call it yet, just log that it exists
                log(f"    ✓ Method exists and is callable")
            except Exception as e:
                log(f"    ✗ Error: {e}")
    
    log("")


def main():
    """Main exploration function"""
    log("="*80)
    log("POSESEARCH API SYSTEMATIC EXPLORATION")
    log("="*80)
    log("")
    
    # Step 1: Discover all PoseSearch classes
    posesearch_classes = explore_posesearch_classes()
    
    # Step 2: Explore key classes
    key_classes = [
        ("PoseSearchSchema", unreal.PoseSearchSchema),
        ("PoseSearchDatabase", unreal.PoseSearchDatabase),
    ]
    
    for class_name, cls in key_classes:
        if cls:
            explore_class(cls, class_name)
    
    # Step 3: Explore actual instances
    schema = unreal.load_object(None, "/Game/MotionMatching/MannyMotionSchema")
    if schema:
        explore_instance(schema, "MannyMotionSchema Instance")
    
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    if database:
        explore_instance(database, "MannyMotionDatabase Instance")
    
    # Step 4: Test modification approaches
    test_schema_modification()
    test_database_modification()
    
    # Summary
    log("="*80)
    log("EXPLORATION COMPLETE")
    log("="*80)
    log(f"\nLog file: {log_file}")
    log("\nNext: Review log to find working API methods")


if __name__ == "__main__":
    main()
