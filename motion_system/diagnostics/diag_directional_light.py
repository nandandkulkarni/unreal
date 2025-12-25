"""
Diagnostic script to test directional light creation in Unreal Engine
Simple test to verify directional light spawning and basic properties
"""
import unreal

def test_directional_light():
    """Create a simple directional light to test visibility"""
    
    print("=" * 60)
    print("DIRECTIONAL LIGHT DIAGNOSTIC TEST")
    print("=" * 60)
    
    # First, delete any existing DiagTestLight
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for actor in all_actors:
        if actor.get_actor_label() == "DiagTestLight":
            unreal.EditorLevelLibrary.destroy_actor(actor)
            print("✓ Deleted existing DiagTestLight")
    
    # Spawn a directional light actor
    location = unreal.Vector(0, 0, 1000)  # High up for visibility
    rotation = unreal.Rotator(pitch=-10, yaw=-90, roll=0)  # From west, low angle (sunset)
    
    light_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        location,
        rotation
    )
    
    if light_actor:
        # Set a label for easy identification
        light_actor.set_actor_label("DiagTestLight")
        
        # Get the light component
        light_component = light_actor.light_component
        
        # Set sunset properties
        light_component.set_editor_property("intensity", 8.0)  # Softer than midday
        light_component.set_editor_property("light_color", unreal.Color(r=255, g=153, b=77))  # Deep sunset orange/red
        light_component.set_editor_property("cast_shadows", True)
        light_component.set_editor_property("atmosphere_sun_light", True)
        light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        
        print(f"✓ Directional light created: {light_actor.get_actor_label()}")
        print(f"  Location: {location}")
        print(f"  Rotation: Pitch={rotation.pitch}°, Yaw={rotation.yaw}° (SUNSET)")
        print(f"  Intensity: 8.0 (softer)")
        print(f"  Color: Deep Sunset (255, 153, 77) - Reddish Orange")
        print(f"  Atmosphere Sun: Enabled")
        print(f"  Cast Shadows: Enabled")
        print(f"  Atmosphere Sun: Enabled")
        print(f"  Cast Shadows: Enabled")
        print("")
        print("Check your Unreal viewport - you should see:")
        print("  1. A directional light icon in the scene")
        print("  2. Warm lighting from the west at 45° angle")
        print("  3. Shadows being cast (if you have objects in scene)")
        print("  4. Sky color affected by atmosphere system")
        
        return light_actor
    else:
        print("✗ Failed to create directional light")
        return None

if __name__ == "__main__":
    test_directional_light()
