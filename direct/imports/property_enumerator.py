"""
Helper functions to enumerate instance properties during runtime
Add these calls to your main script to capture actual instance properties
"""
import os

def enumerate_to_file(instance, instance_name, append=True):
    """Enumerate instance properties and append to api_reference.txt"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "api_reference.txt")
    
    mode = 'a' if append else 'w'
    
    with open(output_file, mode, encoding='utf-8') as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"{instance_name} - RUNTIME INSTANCE\n")
        f.write("=" * 80 + "\n")
        
        # Get editor properties
        try:
            prop_names = instance.get_editor_property_names()
            f.write(f"\nEditor Properties ({len(prop_names)}):\n")
            for prop in sorted(prop_names):
                try:
                    value = instance.get_editor_property(prop)
                    f.write(f"  {prop} = {type(value).__name__}\n")
                except:
                    f.write(f"  {prop}\n")
        except Exception as e:
            f.write(f"  Could not get editor properties: {e}\n")
        
        # Get all attributes
        all_attrs = [x for x in dir(instance) if not x.startswith('_')]
        f.write(f"\nAll public attributes ({len(all_attrs)}):\n")
        for attr in sorted(all_attrs):
            f.write(f"  {attr}\n")
        
        f.write("\n")
    
    print(f"✓ Enumerated {instance_name} properties to api_reference.txt")

def enumerate_camera_properties(camera_actor):
    """Enumerate camera actor and component properties"""
    from logger import log
    
    log("\n📋 Enumerating camera properties to api_reference.txt...")
    enumerate_to_file(camera_actor, "CineCameraActor INSTANCE", append=True)
    
    try:
        camera_component = camera_actor.get_cine_camera_component()
        if camera_component:
            enumerate_to_file(camera_component, "CineCameraComponent INSTANCE", append=True)
    except Exception as e:
        log(f"  Could not get camera component: {e}")

def enumerate_sequence_properties(sequence, camera_binding, transform_section=None):
    """Enumerate sequence and binding properties"""
    from logger import log
    
    log("\n📋 Enumerating sequence properties to api_reference.txt...")
    enumerate_to_file(sequence, "LevelSequence INSTANCE", append=True)
    
    if camera_binding:
        enumerate_to_file(camera_binding, "MovieSceneBindingProxy INSTANCE", append=True)
    
    if transform_section:
        enumerate_to_file(transform_section, "MovieScene3DTransformSection INSTANCE", append=True)
