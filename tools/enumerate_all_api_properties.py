"""
Enumerate ALL Unreal Python API Properties and Methods
Saves a comprehensive reference file for all objects we use

Run this ONCE to generate api_reference.txt, then refer to it when looking for properties
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

output_file = os.path.join(script_dir, "api_reference.txt")

def write_line(f, line=""):
    """Write line to file and print to console"""
    f.write(line + "\n")
    print(line)

def enumerate_class(f, class_obj, class_name):
    """Enumerate all properties and methods of a class"""
    write_line(f, "=" * 80)
    write_line(f, f"{class_name}")
    write_line(f, "=" * 80)
    
    all_attrs = dir(class_obj)
    
    # Filter out private/magic methods
    public_attrs = [x for x in all_attrs if not x.startswith('_')]
    
    # Categorize
    properties = []
    methods = []
    
    for attr in public_attrs:
        try:
            obj = getattr(class_obj, attr)
            if callable(obj):
                methods.append(attr)
            else:
                properties.append(attr)
        except:
            properties.append(attr)  # If we can't get it, assume property
    
    if properties:
        write_line(f, "\nProperties:")
        for prop in sorted(properties):
            write_line(f, f"  {prop}")
    
    if methods:
        write_line(f, "\nMethods:")
        for method in sorted(methods):
            write_line(f, f"  {method}()")
    
    write_line(f, "")

def enumerate_instance_properties(f, instance, instance_name):
    """Enumerate editor properties of an actual instance"""
    write_line(f, "=" * 80)
    write_line(f, f"{instance_name} - INSTANCE PROPERTIES")
    write_line(f, "=" * 80)
    
    try:
        prop_names = instance.get_editor_property_names()
        write_line(f, f"\nEditor Properties ({len(prop_names)}):")
        for prop in prop_names:
            write_line(f, f"  {prop}")
    except Exception as e:
        write_line(f, f"  Could not get editor properties: {e}")
    
    write_line(f, "")

log("=" * 80)
log("GENERATING COMPREHENSIVE API REFERENCE")
log("=" * 80)

with open(output_file, 'w', encoding='utf-8') as f:
    write_line(f, "UNREAL PYTHON API REFERENCE")
    write_line(f, "Generated for camera tracking and sequencer automation")
    write_line(f, "=" * 80)
    write_line(f, "")
    
    # CAMERA CLASSES
    write_line(f, "\n" + "━" * 80)
    write_line(f, "CAMERA CLASSES")
    write_line(f, "━" * 80 + "\n")
    
    enumerate_class(f, unreal.CineCameraActor, "CineCameraActor")
    enumerate_class(f, unreal.CineCameraComponent, "CineCameraComponent")
    enumerate_class(f, unreal.CameraComponent, "CameraComponent")
    enumerate_class(f, unreal.CameraLookatTrackingSettings, "CameraLookatTrackingSettings")
    
    # SEQUENCER CLASSES
    write_line(f, "\n" + "━" * 80)
    write_line(f, "SEQUENCER CLASSES")
    write_line(f, "━" * 80 + "\n")
    
    enumerate_class(f, unreal.LevelSequence, "LevelSequence")
    enumerate_class(f, unreal.MovieSceneSequence, "MovieSceneSequence")
    enumerate_class(f, unreal.MovieSceneSequenceExtensions, "MovieSceneSequenceExtensions")
    enumerate_class(f, unreal.MovieSceneBindingExtensions, "MovieSceneBindingExtensions")
    enumerate_class(f, unreal.MovieSceneTrackExtensions, "MovieSceneTrackExtensions")
    enumerate_class(f, unreal.MovieSceneSectionExtensions, "MovieSceneSectionExtensions")
    
    # TRACK CLASSES
    write_line(f, "\n" + "━" * 80)
    write_line(f, "TRACK CLASSES")
    write_line(f, "━" * 80 + "\n")
    
    enumerate_class(f, unreal.MovieScene3DTransformTrack, "MovieScene3DTransformTrack")
    enumerate_class(f, unreal.MovieScene3DTransformSection, "MovieScene3DTransformSection")
    enumerate_class(f, unreal.MovieSceneCameraCutTrack, "MovieSceneCameraCutTrack")
    enumerate_class(f, unreal.MovieSceneCameraCutSection, "MovieSceneCameraCutSection")
    enumerate_class(f, unreal.MovieSceneSkeletalAnimationTrack, "MovieSceneSkeletalAnimationTrack")
    
    # CONSTRAINT/TRACKING CLASSES
    write_line(f, "\n" + "━" * 80)
    write_line(f, "CONSTRAINT & TRACKING CLASSES")
    write_line(f, "━" * 80 + "\n")
    
    # Search for constraint-related classes
    constraint_classes = [x for x in dir(unreal) if 'constraint' in x.lower() and not x.startswith('_')]
    for cls_name in sorted(constraint_classes[:10]):
        try:
            cls = getattr(unreal, cls_name)
            enumerate_class(f, cls, cls_name)
        except:
            pass
    
    # ACTOR CLASSES
    write_line(f, "\n" + "━" * 80)
    write_line(f, "ACTOR CLASSES")
    write_line(f, "━" * 80 + "\n")
    
    enumerate_class(f, unreal.Actor, "Actor")
    enumerate_class(f, unreal.SkeletalMeshActor, "SkeletalMeshActor")
    
    # EDITOR LIBRARIES
    write_line(f, "\n" + "━" * 80)
    write_line(f, "EDITOR LIBRARIES")
    write_line(f, "━" * 80 + "\n")
    
    enumerate_class(f, unreal.EditorAssetLibrary, "EditorAssetLibrary")
    enumerate_class(f, unreal.LevelSequenceEditorBlueprintLibrary, "LevelSequenceEditorBlueprintLibrary")
    
    # INSTANCE EXAMPLES (need to create actual instances)
    write_line(f, "\n" + "━" * 80)
    write_line(f, "INSTANCE EXAMPLES")
    write_line(f, "━" * 80 + "\n")
    write_line(f, "Note: Run this during scene creation to get instance properties")
    write_line(f, "      Add enumerate_instance_properties() calls in your main script")
    
    # Create example instances
    try:
        lookat = unreal.CameraLookatTrackingSettings()
        enumerate_instance_properties(f, lookat, "CameraLookatTrackingSettings Instance")
    except Exception as e:
        write_line(f, f"Could not create CameraLookatTrackingSettings instance: {e}")
    
    write_line(f, "\n" + "=" * 80)
    write_line(f, "END OF API REFERENCE")
    write_line(f, "=" * 80)

log("\n" + "=" * 80)
log(f"✓ API Reference saved to: {output_file}")
log("=" * 80)
log("\nRefer to this file when looking for property names!")
print("\nDone!")
