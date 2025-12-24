"""
Force reload of all motion_system modules
Run this before tests to ensure latest code is loaded
"""
import sys
import importlib

# Remove cached motion_system modules
modules_to_reload = [m for m in sys.modules.keys() if 'sequence_setup' in m or 'motion_' in m or 'logger' in m or 'cleanup' in m]

for module_name in modules_to_reload:
    print(f"Removing cached module: {module_name}")
    del sys.modules[module_name]

print("\n✓ Python module cache cleared")
print("Modules can now be freshly imported")
