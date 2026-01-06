"""
Flexible test script for AAANKPose plugin - discovers actual class and function names

This script will search for any classes with "AAANK" or "Pose" in the name
and test calling any functions it finds.

Run with: python run_remote.py test_aaankpose_discover.py
"""

import unreal
import os
from datetime import datetime

# Log file path
LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc"
LOG_FILE = os.path.join(LOG_DIR, "test_aaankpose_discover.log")

def log(message):
    """Write message to both console and log file"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def discover_and_test():
    """Discover AAANKPose plugin classes and test them"""
    
    # Clear previous log
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    log("=" * 80)
    log("AAANKPose PLUGIN DISCOVERY TEST")
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    log("")
    
    # Strategy 1: Try direct class access with common variations
    log("Strategy 1: Trying common class name variations...")
    class_variations = [
        "AAANKPose",
        "AAANKPoseLibrary",
        "UAAANKPose",
        "UAAANKPoseLibrary",
        "AAANKPoseBlueprintLibrary",
        "AAANKPoseFunctionLibrary"
    ]
    
    found_class = None
    for class_name in class_variations:
        try:
            cls = getattr(unreal, class_name, None)
            if cls:
                log(f"✓ FOUND: unreal.{class_name}")
                log(f"  Type: {type(cls)}")
                found_class = (class_name, cls)
                break
        except Exception as e:
            log(f"  ✗ {class_name}: {e}")
    
    log("")
    
    # Strategy 2: Search through unreal module
    if not found_class:
        log("Strategy 2: Searching unreal module for AAANK classes...")
        try:
            all_attrs = dir(unreal)
            aaank_attrs = [attr for attr in all_attrs if 'aaank' in attr.lower() or 'pose' in attr.lower()]
            
            if aaank_attrs:
                log(f"Found {len(aaank_attrs)} potential matches:")
                for attr in aaank_attrs[:50]:  # Show first 50
                    try:
                        obj = getattr(unreal, attr)
                        log(f"  - {attr}: {type(obj)}")
                        # If it looks like a class, try it
                        if 'aaank' in attr.lower():
                            found_class = (attr, obj)
                            log(f"  ✓ Using this one!")
                            break
                    except:
                        pass
            else:
                log("  No matches found")
        except Exception as e:
            log(f"  Error: {e}")
    
    log("")
    
    # If we found a class, test it
    if found_class:
        class_name, cls = found_class
        log("=" * 80)
        log(f"TESTING CLASS: {class_name}")
        log("=" * 80)
        log("")
        
        # List all methods
        log("Available methods and attributes:")
        try:
            members = dir(cls)
            # Filter out private/internal
            public_members = [m for m in members if not m.startswith('_')]
            
            for member in public_members:
                try:
                    attr = getattr(cls, member)
                    log(f"  - {member}: {type(attr)}")
                except:
                    log(f"  - {member}: (could not access)")
            
            log("")
            
            # Try to find and call "hello world" function
            log("Looking for 'hello world' function...")
            hello_functions = [m for m in public_members if 'hello' in m.lower() or 'world' in m.lower() or 'test' in m.lower()]
            
            if hello_functions:
                log(f"Found potential functions: {hello_functions}")
                for func_name in hello_functions:
                    try:
                        func = getattr(cls, func_name)
                        log(f"\nTrying to call: {func_name}()")
                        result = func()
                        log(f"✓ SUCCESS!")
                        log(f"  Result: {result}")
                        log(f"  Type: {type(result)}")
                    except Exception as e:
                        log(f"  ✗ Error calling {func_name}: {e}")
            else:
                log("No obvious hello/world/test functions found")
                log("Trying first few callable methods...")
                
                # Try first few methods that look callable
                for member in public_members[:10]:
                    try:
                        attr = getattr(cls, member)
                        if callable(attr):
                            log(f"\nTrying: {member}()")
                            result = attr()
                            log(f"  Result: {result}")
                    except Exception as e:
                        log(f"  Skipped {member}: {e}")
                        
        except Exception as e:
            log(f"Error exploring class: {e}")
    else:
        log("=" * 80)
        log("❌ PLUGIN NOT FOUND")
        log("=" * 80)
        log("")
        log("The plugin is not accessible from Python. This means:")
        log("1. Plugin is not enabled (Edit → Plugins)")
        log("2. Plugin did not compile successfully")
        log("3. Editor was not restarted after enabling plugin")
        log("")
        log("Please:")
        log("1. Check Edit → Plugins in Unreal Editor")
        log("2. Enable 'AAANKPose' plugin")
        log("3. Restart the editor")
        log("4. Run this test again")
    
    log("")
    log("=" * 80)
    log("DISCOVERY TEST COMPLETE")
    log("=" * 80)
    log(f"\nFull results saved to: {LOG_FILE}")

if __name__ == "__main__":
    discover_and_test()
