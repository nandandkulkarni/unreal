"""
Test the simple C++ plugin

This verifies the C++ to Python workflow works
"""
import unreal

def test_simple_plugin():
    print("="*60)
    print("Testing Simple C++ Plugin")
    print("="*60)
    
    # Try to load the library
    try:
        lib = unreal.TestPythonLibrary()
        print("✓ Plugin library loaded successfully!")
    except Exception as e:
        print(f"✗ Failed to load library: {e}")
        print("\nMake sure:")
        print("1. Project is converted to C++")
        print("2. Solution is built")
        print("3. Plugin is enabled in Edit → Plugins")
        print("4. Editor has been restarted")
        return False
    
    print()
    
    # Test 1: Say Hello
    try:
        result = lib.say_hello("Python")
        print(f"Test 1 - SayHello:")
        print(f"  Result: {result}")
        print(f"  ✓ PASS")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False
    
    print()
    
    # Test 2: Add Numbers
    try:
        result = lib.add_numbers(42, 58)
        expected = 100
        print(f"Test 2 - AddNumbers:")
        print(f"  42 + 58 = {result}")
        if result == expected:
            print(f"  ✓ PASS (expected {expected})")
        else:
            print(f"  ✗ FAIL (expected {expected}, got {result})")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False
    
    print()
    
    # Test 3: Get Current Time
    try:
        result = lib.get_current_time()
        print(f"Test 3 - GetCurrentTime:")
        print(f"  Current time: {result}")
        print(f"  ✓ PASS")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False
    
    print()
    print("="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print()
    print("C++ to Python workflow is working!")
    print("You can now proceed with the PoseSearch plugin.")
    
    return True


if __name__ == "__main__":
    success = test_simple_plugin()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
