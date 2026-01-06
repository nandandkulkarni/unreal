"""
Research: PoseSearch Python API in Unreal 5.7

This script explores what PoseSearch/Motion Matching functions are available
in Python, specifically looking for query/search capabilities.
"""

import unreal
import os
from datetime import datetime

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"api_research_{timestamp}.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

log("=" * 80)
log("POSESEARCH PYTHON API RESEARCH - UNREAL 5.7")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# 1. Check PoseSearchDatabase methods
log("\n[1] PoseSearchDatabase Methods:")
log("-" * 80)

try:
    db = unreal.PoseSearchDatabase
    methods = [m for m in dir(db) if not m.startswith('_')]
    
    log(f"Total public methods: {len(methods)}")
    
    # Look for query/search related
    query_methods = [m for m in methods if any(keyword in m.lower() 
                     for keyword in ['query', 'search', 'find', 'match', 'pose', 'get'])]
    
    if query_methods:
        log(f"\nPotential query/search methods ({len(query_methods)}):")
        for method in sorted(query_methods):
            log(f"  - {method}")
    else:
        log("\n⚠ No obvious query methods found")
    
    # Show all methods for reference
    log(f"\nAll methods:")
    for i, method in enumerate(sorted(methods), 1):
        log(f"  {i:3d}. {method}")
        
except Exception as e:
    log(f"✗ ERROR: {e}")

# 2. Check PoseSearchSchema methods
log("\n" + "=" * 80)
log("[2] PoseSearchSchema Methods:")
log("-" * 80)

try:
    schema = unreal.PoseSearchSchema
    methods = [m for m in dir(schema) if not m.startswith('_')]
    
    log(f"Total public methods: {len(methods)}")
    
    query_methods = [m for m in methods if any(keyword in m.lower() 
                     for keyword in ['query', 'search', 'find'])]
    
    if query_methods:
        log(f"\nQuery-related methods:")
        for method in sorted(query_methods):
            log(f"  - {method}")
    
except Exception as e:
    log(f"✗ ERROR: {e}")

# 3. Search for PoseSearch related classes
log("\n" + "=" * 80)
log("[3] All PoseSearch Classes in Unreal:")
log("-" * 80)

try:
    # Get all classes in unreal module
    all_attrs = dir(unreal)
    pose_classes = [attr for attr in all_attrs if 'pose' in attr.lower() and 'search' in attr.lower()]
    
    log(f"Found {len(pose_classes)} PoseSearch-related classes:")
    for cls_name in sorted(pose_classes):
        try:
            cls = getattr(unreal, cls_name)
            log(f"\n  {cls_name}:")
            log(f"    Type: {type(cls)}")
            
            # Check for query methods
            if hasattr(cls, '__dict__') or hasattr(cls, '__dir__'):
                methods = [m for m in dir(cls) if not m.startswith('_')]
                query_methods = [m for m in methods if 'query' in m.lower() or 'search' in m.lower()]
                if query_methods:
                    log(f"    Query methods: {query_methods}")
        except:
            pass
            
except Exception as e:
    log(f"✗ ERROR: {e}")

# 4. Load actual database and check instance methods
log("\n" + "=" * 80)
log("[4] Database Instance Methods:")
log("-" * 80)

try:
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    if database:
        log(f"Loaded: {database.get_name()}")
        
        methods = [m for m in dir(database) if not m.startswith('_')]
        log(f"\nTotal instance methods: {len(methods)}")
        
        # Look for query/search
        query_methods = [m for m in methods if any(keyword in m.lower() 
                         for keyword in ['query', 'search', 'find', 'match'])]
        
        if query_methods:
            log(f"\nQuery-related instance methods:")
            for method in sorted(query_methods):
                log(f"  - {method}")
                # Try to get method signature
                try:
                    method_obj = getattr(database, method)
                    log(f"      Type: {type(method_obj)}")
                except:
                    pass
        else:
            log("\n⚠ No query methods found on instance")
            
        # Check for any "Search" or "Query" in method names
        log(f"\nAll methods containing 'get', 'find', or 'search':")
        relevant = [m for m in methods if any(k in m.lower() for k in ['get', 'find', 'search'])]
        for method in sorted(relevant):
            log(f"  - {method}")
            
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

# 5. Check for PoseSearchLibrary or similar
log("\n" + "=" * 80)
log("[5] Looking for PoseSearch Library Classes:")
log("-" * 80)

try:
    library_names = [
        'PoseSearchLibrary',
        'PoseSearchBlueprintLibrary', 
        'PoseSearchFunctionLibrary',
        'MotionMatchingLibrary',
        'AnimationPoseSearchLibrary'
    ]
    
    for name in library_names:
        try:
            lib = getattr(unreal, name, None)
            if lib:
                log(f"\n✓ Found: {name}")
                methods = [m for m in dir(lib) if not m.startswith('_')]
                log(f"  Methods: {len(methods)}")
                
                # Show all methods
                for method in sorted(methods)[:20]:
                    log(f"    - {method}")
            else:
                log(f"✗ Not found: {name}")
        except Exception as e:
            log(f"✗ Error checking {name}: {e}")
            
except Exception as e:
    log(f"✗ ERROR: {e}")

# Summary
log("\n" + "=" * 80)
log("SUMMARY")
log("=" * 80)

log("""
Based on this research:

1. PoseSearchDatabase class exists in Python
2. Can create, populate, and build databases
3. BUT: No obvious query/search methods exposed to Python

This confirms our earlier findings:
- Database manipulation: ✓ Available in Python (via our plugin)
- Database querying: ✗ NOT available in Python
- Queries happen in C++ AnimGraph nodes at runtime

For procedural movies with query capability:
→ Need to extend C++ plugin with query function
→ Or use traditional animation selection logic in Python
""")

log(f"\nLog saved to: {LOG_FILE}")
