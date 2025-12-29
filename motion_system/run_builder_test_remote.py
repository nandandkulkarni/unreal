"""
Runner Script - Execute Builder Test
Triggers 'unreal_builder_test.py' inside Unreal via Remote Control
"""
import sys
import os

# Ensure we can import unreal_connection from parent dir
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from unreal_connection import UnrealRemote

def main():
    # Path to the actual script file that will run INSIDE Unreal
    # It is located in the same directory as this runner
    script_path = os.path.join(script_dir, "unreal_builder_test.py")
    
    print("=" * 60)
    print("RUNNING BUILDER TEST (REMOTE)")
    print("=" * 60)
    print(f"Target Script: {script_path}")
    
    unreal = UnrealRemote()
    if not unreal.is_connected():
        print("Error: Could not connect to Unreal Engine (WebControl).")
        return

    print("Sending script to Unreal...")
    success, result = unreal.execute_python_file(script_path)
    
    if success:
        print("\n✓ SUCCESS")
        print("Check Unreal Output Log for details.")
    else:
        print("\n✗ FAILED")
        print(f"Result: {result}")

if __name__ == "__main__":
    main()
