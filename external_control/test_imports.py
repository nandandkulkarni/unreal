"""
Test if motion_system imports work in Unreal
"""
import unreal
import sys
import os

print("=" * 60)
print("TESTING IMPORTS")
print("=" * 60)

# Show current sys.path
print("\nCurrent sys.path:")
for i, p in enumerate(sys.path):
    print(f"  [{i}] {p}")

# Try to add motion_system to path
script_dir = r"C:\UnrealProjects\Coding\unreal\tests"
parent_dir = os.path.dirname(script_dir)
motion_system_dir = os.path.join(parent_dir, "motion_system")

print(f"\nMotion system dir: {motion_system_dir}")
print(f"Exists: {os.path.exists(motion_system_dir)}")

if motion_system_dir not in sys.path:
    sys.path.insert(0, motion_system_dir)
    print(f"Added to sys.path")

# Try imports
print("\nTrying imports...")
try:
    import logger
    print("  ✓ logger imported")
except Exception as e:
    print(f"  ✗ logger failed: {e}")

try:
    import debug_db
    print("  ✓ debug_db imported")
except Exception as e:
    print(f"  ✗ debug_db failed: {e}")

try:
    import motion_planner
    print("  ✓ motion_planner imported")
except Exception as e:
    print(f"  ✗ motion_planner failed: {e}")

print("\n" + "=" * 60)
print("IMPORT TEST COMPLETE")
print("=" * 60)
