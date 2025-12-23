"""
Check MovieScene3DTransformTrack for look-at properties
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
log("MovieScene3DTransformTrack - Properties Check")
log("=" * 60)

# Check track class
log("\nMovieScene3DTransformTrack attributes with 'look', 'track', 'camera':")
all_attrs = dir(unreal.MovieScene3DTransformTrack)
keywords = ['look', 'camera', 'constraint']
for keyword in keywords:
    matches = [x for x in all_attrs if keyword.lower() in x.lower() and not x.startswith('_')]
    if matches:
        log(f"\n'{keyword}' matches in Track:")
        for m in matches:
            log(f"  {m}")

# Check if section has it
log("\n" + "=" * 60)
log("MovieScene3DTransformSection properties (editor properties):")
log("=" * 60)
log("\nNote: Need to check this from actual section instance during script run")
log("The main script now includes get_editor_property_names() call")

print("\nDone!")
