"""Run unreal_add_keyframe.py in Unreal Engine"""
from unreal_connection import UnrealRemote
import py_compile
import sys

# Verify syntax first
print("Checking Python syntax...")
try:
    py_compile.compile("unreal_add_keyframe.py", doraise=True)
    print("✓ Syntax check passed\n")
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error found:")
    print(str(e))
    sys.exit(1)

unreal = UnrealRemote()

if not unreal.is_connected():
    print("✗ Cannot connect to Unreal Engine!")
    print("Make sure:")
    print("  1. Unreal Engine is running")
    print("  2. WebControl server is started (console: WebControl.StartServer)")
    exit(1)

print("=" * 60)
print("Adding Keyframe to Mannequin Track")
print("=" * 60)
print("\nExecuting script in Unreal...")

success, result = unreal.execute_python_file("unreal_add_keyframe.py")

if success:
    print("\n✓ Script executed successfully!")
    print("\nCheck Unreal Engine:")
    print("  - Open the sequence in Sequencer")
    print("  - Scrub to 5 seconds to see the keyframe")
    print("=" * 60)
else:
    print(f"\n✗ Failed: {result}")
    print("=" * 60)
