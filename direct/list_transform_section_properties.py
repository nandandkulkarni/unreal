"""
List all properties on MovieScene3DTransformSection to find look-at property
"""
import unreal
import sys
import os

# Add imports path
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(script_dir, "imports")
if module_path not in sys.path:
    sys.path.insert(0, module_path)

from logger import log

log("=" * 60)
log("MovieScene3DTransformSection - All Properties")
log("=" * 60)

# Get all attributes/methods
all_attrs = dir(unreal.MovieScene3DTransformSection)

log("\nAll attributes (filtered for relevance):")
for attr in sorted(all_attrs):
    # Skip private/magic methods
    if attr.startswith('_'):
        continue
    log(f"  {attr}")

log("\n" + "=" * 60)
log("Searching for 'look', 'track', 'camera', 'constraint' keywords:")
log("=" * 60)

keywords = ['look', 'track', 'camera', 'constraint', 'target', 'follow']
for keyword in keywords:
    matches = [x for x in all_attrs if keyword.lower() in x.lower() and not x.startswith('_')]
    if matches:
        log(f"\n'{keyword}' matches:")
        for m in matches:
            log(f"  {m}")

# Try to get editor property names if possible
log("\n" + "=" * 60)
log("Attempting to get editor property names:")
log("=" * 60)

try:
    # We need an actual instance to call get_editor_property_names
    # But we can check the static class
    log("\nNote: To get actual property names, we need a section instance.")
    log("The property might be on MovieScene3DTransformSection or its parent.")
except Exception as e:
    log(f"Error: {e}")

print("\nDone!")
