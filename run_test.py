"""Run test_extension.py in Unreal Engine"""
from unreal_connection import UnrealRemote

unreal = UnrealRemote()

if not unreal.is_connected():
    print("✗ Cannot connect to Unreal Engine!")
    exit(1)

print("Running test_extension.py in Unreal...")
success, result = unreal.execute_python_file("test_extension.py")

if success:
    print("\n✓ Test executed successfully!")
else:
    print(f"\n✗ Failed: {result}")
