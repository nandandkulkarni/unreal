"""
Find the Look At Tracking API in Unreal Python - Complete Exploration
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
log("Searching for Look At / Camera Track APIs")
log("=" * 60)

# Search for classes with "look" in the name
log("\nClasses with 'look' in name:")
look_classes = [x for x in dir(unreal) if 'look' in x.lower()]
for cls in look_classes[:20]:
    log(f"  {cls}")

# Search for classes with "track" and "camera"
log("\nClasses with 'camera' and 'track' in name:")
camera_track_classes = [x for x in dir(unreal) if 'camera' in x.lower() and 'track' in x.lower()]
for cls in camera_track_classes[:20]:
    log(f"  {cls}")

# Check if there's a MovieSceneCameraShake or similar
log("\nMovieScene camera-related classes:")
moviescene_camera = [x for x in dir(unreal) if x.startswith('MovieScene') and 'Camera' in x]
for cls in moviescene_camera[:30]:
    log(f"  {cls}")

# Check camera component for look at methods
log("\nChecking CineCameraComponent for look at methods:")
try:
    cine_camera_methods = [x for x in dir(unreal.CineCameraComponent) if 'look' in x.lower() or 'track' in x.lower()]
    for method in cine_camera_methods:
        log(f"  {method}")
except Exception as e:
    log(f"  Error: {e}")

# Check MovieScene3DTransformSection for look at properties
log("\nChecking MovieScene3DTransformSection for look at properties:")
try:
    transform_section_props = [x for x in dir(unreal.MovieScene3DTransformSection) if 'look' in x.lower() or 'track' in x.lower()]
    for prop in transform_section_props:
        log(f"  {prop}")
except Exception as e:
    log(f"  Error: {e}")

# === DEEP DIVE INTO CameraLookatTrackingSettings ===
log("\n" + "=" * 60)
log("EXPLORING CameraLookatTrackingSettings")
log("=" * 60)

try:
    # Get all properties and methods
    log("\nAll attributes of CameraLookatTrackingSettings:")
    attrs = [x for x in dir(unreal.CameraLookatTrackingSettings) if not x.startswith('_')]
    for attr in attrs:
        log(f"  {attr}")
    
    # Try to create an instance and see what properties it has
    log("\nTrying to inspect instance properties:")
    try:
        instance = unreal.CameraLookatTrackingSettings()
        log(f"  Instance created: {instance}")
        
        # Get editor properties
        log("\nEditor properties:")
        try:
            props = instance.get_editor_property_names()
            for prop in props:
                value = instance.get_editor_property(prop)
                log(f"  {prop} = {value}")
        except Exception as e:
            log(f"  Could not get editor properties: {e}")
            
    except Exception as e:
        log(f"  Could not create instance: {e}")
    
    # Check if MovieScene3DTransformSection has any lookat-related methods
    log("\nChecking MovieScene3DTransformSection ALL methods:")
    section_methods = [x for x in dir(unreal.MovieScene3DTransformSection) if not x.startswith('_')]
    for method in section_methods:
        log(f"  {method}")
        
except Exception as e:
    log(f"Error: {e}")
    import traceback
    log(traceback.format_exc())

log("\n" + "=" * 60)
log("Done!")
print("Results written to scene_setup.log")
