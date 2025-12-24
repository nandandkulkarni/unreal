"""
Execute Integrated Motion Test via Remote Control
Runs the test suite remotely and displays results
"""
import requests
import os
import sys

BASE_URL = "http://localhost:30010/remote"

def execute_unreal_python_file(script_path):
    """Execute a Python file in Unreal's Python interpreter"""
    
    # Convert to absolute path and use forward slashes
    abs_path = os.path.abspath(script_path).replace('\\', '/')
    
    # Build Python command to execute the file
    python_command = f"exec(open(r'{abs_path}').read())"
    
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": python_command}
    }
    
    response = requests.put(f"{BASE_URL}/object/call", json=payload)
    
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def main():
    print("=" * 80)
    print("REMOTE EXECUTION: INTEGRATED MOTION TEST SUITE")
    print("=" * 80)
    
    # Path to integrated test
    script_path = r"C:\UnrealProjects\Coding\unreal\motion_system\tests\run_integrated_test.py"
    
    if not os.path.exists(script_path):
        print(f"\n✗ Error: Script not found at {script_path}")
        return
    
    print(f"\n[1] Connecting to Unreal Remote Control...")
    print(f"    URL: {BASE_URL}/object/call")
    
    try:
        # Test connection with a simple command
        test_payload = {
            "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
            "functionName": "ExecutePythonCommand",
            "parameters": {"PythonCommand": "print('Remote Control Connected')"}
        }
        response = requests.put(f"{BASE_URL}/object/call", json=test_payload)
        if response.status_code != 200:
            print(f"\n✗ Error: HTTP {response.status_code}")
            print(f"    Response: {response.text}")
            return
        print(f"    ✓ Connected")
    except Exception as e:
        print(f"\n✗ Connection Error:")
        print(f"    {type(e).__name__}: {e}")
        return
    
    print(f"\n[2] Executing integrated test suite...")
    print(f"    Script: {script_path}")
    print(f"    This will run 5 automated tests")
    print()
    
    success, result = execute_unreal_python_file(script_path)
    
    if success:
        print("\n" + "=" * 80)
        print("✓ TEST SUITE EXECUTED REMOTELY")
        print("=" * 80)
        print()
        print("Check the following for results:")
        print("  1. Unreal Output Log - Real-time test progress")
        print("  2. output/troubleshooting_log_*.txt - Detailed diagnostics")
        print("  3. output/motion_debug.db - SQLite database")
        print()
        print("Result from Unreal:")
        print(result)
        print()
        print("=" * 80)
        print("To analyze results, run:")
        print("  python external_control/query_test_results.py")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("✗ EXECUTION FAILED")
        print("=" * 80)
        print(f"Error: {result}")
        print()
        print("Troubleshooting:")
        print("  - Check Unreal Output Log for Python errors")
        print("  - Ensure Remote Control is enabled in Unreal")
        print("  - Verify script path is correct")
        print("=" * 80)

if __name__ == "__main__":
    main()
