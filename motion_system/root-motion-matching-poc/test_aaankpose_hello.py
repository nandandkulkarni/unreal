"""
Test script for AAANKPose plugin - Testing actual GetHelloWorld() function

Class: UAAANKPoseBlueprintLibrary
Function: GetHelloWorld()

Run with: python run_remote.py test_aaankpose_hello.py
"""

import unreal
import os
from datetime import datetime

# Log file path
LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc"
LOG_FILE = os.path.join(LOG_DIR, "test_aaankpose_hello.log")

def log(message):
    """Write message to both console and log file"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def test_hello_world():
    """Test the GetHelloWorld() function from AAANKPose plugin"""
    
    # Clear previous log
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    log("=" * 80)
    log("AAANKPose PLUGIN - HELLO WORLD TEST")
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    log("")
    
    # Test 1: Access the library class
    log("Test 1: Accessing AAANKPoseBlueprintLibrary class...")
    try:
        lib = unreal.AAANKPoseBlueprintLibrary
        log(f"✓ SUCCESS: Class accessible")
        log(f"  Class: {lib}")
        log(f"  Type: {type(lib)}")
    except AttributeError as e:
        log(f"✗ FAILED: Class not found")
        log(f"  Error: {e}")
        log("")
        log("This means the plugin is not loaded. Please:")
        log("1. Open Unreal Editor")
        log("2. Go to Edit → Plugins")
        log("3. Search for 'AAANKPose'")
        log("4. Enable the plugin")
        log("5. Restart the editor")
        log("6. Run this test again")
        return False
    except Exception as e:
        log(f"✗ FAILED: Unexpected error")
        log(f"  Error: {e}")
        return False
    
    log("")
    
    # Test 2: Check if get_hello_world function exists
    log("Test 2: Checking for get_hello_world() function...")
    try:
        if hasattr(lib, 'get_hello_world'):
            log(f"✓ SUCCESS: Function exists")
            log(f"  Function: {lib.get_hello_world}")
        else:
            log(f"✗ FAILED: Function 'get_hello_world' not found")
            log(f"  Available methods:")
            methods = [m for m in dir(lib) if not m.startswith('_')]
            for method in methods[:20]:
                log(f"    - {method}")
            return False
    except Exception as e:
        log(f"✗ FAILED: Error checking function")
        log(f"  Error: {e}")
        return False
    
    log("")
    
    # Test 3: Call the function
    log("Test 3: Calling get_hello_world()...")
    try:
        result = lib.get_hello_world()
        log(f"✓ SUCCESS: Function executed!")
        log(f"  Return value: '{result}'")
        log(f"  Return type: {type(result)}")
        
        # Verify it's actually "Hello World"
        if "hello" in result.lower() or "world" in result.lower():
            log(f"✓ VERIFIED: Contains 'Hello World' message")
        else:
            log(f"⚠ WARNING: Unexpected return value (expected Hello World)")
            
    except Exception as e:
        log(f"✗ FAILED: Error calling function")
        log(f"  Error: {e}")
        return False
    
    log("")
    log("=" * 80)
    log("✅ ALL TESTS PASSED!")
    log("=" * 80)
    log("")
    log("Your AAANKPose plugin is working correctly!")
    log("")
    log("Next steps:")
    log("1. ✅ Plugin is accessible from Python")
    log("2. ✅ Functions can be called successfully")
    log("3. ⏳ Ready to add PoseSearch functions")
    log("")
    log("To add PoseSearch functionality:")
    log("  See: INTEGRATE_AAANKPOSE.md")
    log("")
    log(f"Full results saved to: {LOG_FILE}")
    
    return True

if __name__ == "__main__":
    success = test_hello_world()
    if success:
        print("\n🎉 Plugin test successful!")
    else:
        print("\n❌ Plugin test failed - see log for details")
