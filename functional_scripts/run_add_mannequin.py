"""
Runner Script - Add Mannequin to Sequence

This script runs from PowerShell and executes the pure Unreal Python script
inside Unreal Engine via the Remote Control API.

Usage:
    python run_add_mannequin.py
"""

from unreal_connection import UnrealRemote
import py_compile
import sys
import os


def main():
    """Execute the add mannequin script in Unreal"""
    
    # Path to the pure Unreal Python script
    script_path = os.path.join(os.path.dirname(__file__), "unreal_add_mannequin_to_sequence.py")
    
    # Verify syntax first
    print("Checking Python syntax...")
    try:
        py_compile.compile(script_path, doraise=True)
        print("✓ Syntax check passed\n")
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error found:")
        print(str(e))
        return False
    
    # Connect to Unreal
    unreal = UnrealRemote()
    
    if not unreal.is_connected():
        print("✗ Cannot connect to Unreal Engine!")
        print("Make sure:")
        print("  1. Unreal Engine is running")
        print("  2. WebControl server is started (console: WebControl.StartServer)")
        print("  3. Remote Control is configured in DefaultEngine.ini")
        return False
    
    print("=" * 60)
    print("Adding Mannequin to Sequence")
    print("=" * 60)
    print(f"\nExecuting script: {script_path}")
    print("(Running inside Unreal's Python interpreter)")
    
    # Execute the Python file inside Unreal
    success, result = unreal.execute_python_file(script_path)
    
    if success:
        print("\n✓ Script executed successfully!")
        print("\nCheck Unreal Engine for results:")
        print("  - Output Log (Window → Developer Tools → Output Log)")
        print("  - Sequencer window")
        print(f"  - Log file: C:\\RemoteProjects\\functional\\add_mannequin_log.txt")
        print("=" * 60)
        return True
    else:
        print(f"\n✗ Execution failed: {result}")
        print("\nTroubleshooting:")
        print("  - Check Unreal's Output Log for Python errors")
        print("  - Make sure TestMannequin1 exists in the level")
        print("  - Make sure at least one Test* sequence exists")
        print("=" * 60)
        return False


if __name__ == "__main__":
    main()
