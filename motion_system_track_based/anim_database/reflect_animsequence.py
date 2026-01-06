"""
AnimSequence API Reflection Script

Explores all available methods and properties on AnimSequence objects
to understand what's supported in this Unreal Engine version.
"""

import unreal

# Output file
OUTPUT_FILE = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\animsequence_api_reflection.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear output file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("")

log("=" * 80)
log("ANIMSEQUENCE API REFLECTION")
log("=" * 80)

# Load a sample animation
sample_anim_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations/Jog_Fwd.Jog_Fwd"
log(f"\nLoading sample animation: {sample_anim_path}")

try:
    anim = unreal.EditorAssetLibrary.load_asset(sample_anim_path)
    if not anim:
        log("✗ Failed to load animation")
    else:
        log(f"✓ Loaded: {anim.get_name()}")
        log(f"  Type: {type(anim)}")
        log(f"  Class: {anim.get_class().get_name()}")
        
        # Get all attributes
        log("\n" + "=" * 80)
        log("ALL ATTRIBUTES (dir)")
        log("=" * 80)
        
        all_attrs = dir(anim)
        methods = []
        properties = []
        
        for attr in sorted(all_attrs):
            if attr.startswith('_'):
                continue
            
            try:
                val = getattr(anim, attr)
                if callable(val):
                    methods.append(attr)
                else:
                    properties.append(attr)
            except:
                pass
        
        log(f"\nFound {len(methods)} methods and {len(properties)} properties")
        
        # List all methods
        log("\n" + "=" * 80)
        log(f"METHODS ({len(methods)})")
        log("=" * 80)
        for method in methods:
            log(f"  {method}()")
        
        # List all properties
        log("\n" + "=" * 80)
        log(f"PROPERTIES ({len(properties)})")
        log("=" * 80)
        for prop in properties:
            try:
                val = getattr(anim, prop)
                log(f"  {prop}: {type(val).__name__}")
            except Exception as e:
                log(f"  {prop}: <error: {e}>")
        
        # Test specific methods we care about
        log("\n" + "=" * 80)
        log("TESTING SPECIFIC METHODS")
        log("=" * 80)
        
        test_methods = [
            'get_number_of_frames',
            'get_number_of_keys',
            'get_frame_count',
            'get_total_frames',
            'get_length',
            'get_play_length',
            'get_duration',
        ]
        
        for method_name in test_methods:
            if hasattr(anim, method_name):
                try:
                    method = getattr(anim, method_name)
                    if callable(method):
                        result = method()
                        log(f"  ✓ {method_name}() = {result}")
                    else:
                        log(f"  ✓ {method_name} = {method} (property)")
                except Exception as e:
                    log(f"  ✗ {method_name}() failed: {e}")
            else:
                log(f"  ✗ {method_name} - NOT FOUND")
        
        # Test editor properties
        log("\n" + "=" * 80)
        log("TESTING EDITOR PROPERTIES")
        log("=" * 80)
        
        test_props = [
            'sequence_length',
            'number_of_frames',
            'frame_count',
            'num_frames',
            'total_frames',
            'duration',
            'play_length',
            'rate_scale',
            'target_frame_rate',
            'import_file_framerate',
        ]
        
        for prop_name in test_props:
            try:
                val = anim.get_editor_property(prop_name)
                log(f"  ✓ {prop_name} = {val} ({type(val).__name__})")
            except Exception as e:
                log(f"  ✗ {prop_name} - {e}")
        
        # Get class properties via static_class
        log("\n" + "=" * 80)
        log("CLASS PROPERTIES (via static_class)")
        log("=" * 80)
        
        try:
            static_class = anim.static_class()
            log(f"Static class: {static_class}")
            
            # Try to get property list
            if hasattr(static_class, 'get_properties'):
                props = static_class.get_properties()
                log(f"\nProperties from static_class: {props}")
        except Exception as e:
            log(f"Error getting static_class properties: {e}")
        
        log("\n" + "=" * 80)
        log("REFLECTION COMPLETE")
        log("=" * 80)
        log(f"\nOutput saved to: {OUTPUT_FILE}")
        
except Exception as e:
    log(f"\n✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())
