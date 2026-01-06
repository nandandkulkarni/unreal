"""
Test script to verify atmosphere and volumetrics implementation

Run this locally to test JSON generation before triggering in Unreal
"""

import json
from motion_builder import MovieBuilder

def test_basic_atmosphere():
    """Test basic atmosphere creation"""
    print("\n=== Test 1: Basic Atmosphere ===")
    
    with MovieBuilder("Test Atmosphere", fps=30) as movie:
        movie.add_atmosphere(
            fog_density="medium",
            fog_color="atmospheric",
            volumetric=True
        )
        movie.save_to_json("dist/test_atmosphere.json")
    
    # Verify JSON
    with open("dist/test_atmosphere.json", "r") as f:
        plan = json.load(f)
    
    assert len(plan["plan"]) == 1
    assert plan["plan"][0]["command"] == "add_atmosphere"
    assert plan["plan"][0]["fog_density"] == "medium"
    print("✓ Basic atmosphere test passed")


def test_light_with_god_rays():
    """Test directional light with god rays"""
    print("\n=== Test 2: Light with God Rays ===")
    
    with MovieBuilder("Test God Rays", fps=30) as movie:
        movie.add_atmosphere(fog_density="light", volumetric=True)
        movie.add_directional_light(
            actor_name="SunLight",
            direction_from="west",
            angle="low",
            cast_volumetric_shadow=True,
            light_shaft_bloom_scale="cinematic"
        )
        movie.save_to_json("dist/test_god_rays.json")
    
    # Verify JSON
    with open("dist/test_god_rays.json", "r") as f:
        plan = json.load(f)
    
    light_cmd = plan["plan"][1]
    assert light_cmd["command"] == "add_directional_light"
    assert light_cmd["cast_volumetric_shadow"] == True
    assert light_cmd["light_shaft_bloom_scale"] == "cinematic"
    print("✓ God rays test passed")


def test_animate_fog():
    """Test fog animation"""
    print("\n=== Test 3: Animated Fog ===")
    
    with MovieBuilder("Test Fog Animation", fps=30) as movie:
        movie.add_atmosphere(fog_density="heavy")
        movie.add_actor("Dummy", location=(0, 0, 0))
        
        with movie.for_actor("Dummy") as dummy:
            dummy.stay().for_time(3.0)
            dummy.stay().till_end()
        
        movie.animate_fog(target_density="light", duration=5.0)
        movie.save_to_json("dist/test_fog_animation.json")
    
    # Verify JSON
    with open("dist/test_fog_animation.json", "r") as f:
        plan = json.load(f)
    
    # Find animate_fog command
    fog_anim = [cmd for cmd in plan["plan"] if cmd["command"] == "animate_fog"][0]
    assert fog_anim["target_density"] == "light"
    assert fog_anim["duration"] == 5.0
    print("✓ Fog animation test passed")


def test_configure_light_shafts():
    """Test light shaft configuration command"""
    print("\n=== Test 4: Configure Light Shafts ===")
    
    with MovieBuilder("Test Light Shafts Config", fps=30) as movie:
        movie.add_directional_light(actor_name="Sun", direction_from="east", angle="low")
        movie.configure_light_shafts(
            light_actor="Sun",
            enable_light_shafts=True,
            bloom_scale="dramatic",
            cast_volumetric_shadow=True
        )
        movie.save_to_json("dist/test_light_shafts_config.json")
    
    # Verify JSON
    with open("dist/test_light_shafts_config.json", "r") as f:
        plan = json.load(f)
    
    shaft_cmd = plan["plan"][1]
    assert shaft_cmd["command"] == "configure_light_shafts"
    assert shaft_cmd["actor"] == "Sun"
    assert shaft_cmd["bloom_scale"] == "dramatic"
    print("✓ Light shafts configuration test passed")


def test_complete_scene():
    """Test complete atmospheric scene"""
    print("\n=== Test 5: Complete Scene ===")
    
    with MovieBuilder("Complete Atmospheric Scene", fps=30) as movie:
        # Atmosphere
        movie.add_atmosphere(
            fog_density="heavy",
            fog_color="atmospheric",
            fog_height_falloff=0.3,
            volumetric=True,
            volumetric_scattering=1.5
        )
        
        # Light with god rays
        movie.add_directional_light(
            actor_name="Sun",
            direction_from="east",
            angle="low",
            intensity="soft",
            color="golden",
            cast_volumetric_shadow=True,
            light_shaft_bloom_scale="cinematic"
        )
        
        # Character
        movie.add_actor("Hero", location=(0, 0, 0))
        with movie.for_actor("Hero") as hero:
            hero.stay().for_time(2.0)
            hero.stay().till_end()
        
        # Camera
        movie.add_camera("Cam", location=(500, -500, 200)).add()
        with movie.for_camera("Cam") as cam:
            cam.stay().till_end()
        
        movie.at_time(0.0).camera_cut("Cam")
        
        # Animate fog
        movie.animate_fog(target_density="light", target_color="warm_haze", duration=8.0)
        
        movie.save_to_json("dist/test_complete_scene.json")
    
    # Verify JSON structure
    with open("dist/test_complete_scene.json", "r") as f:
        plan = json.load(f)
    
    commands = [cmd["command"] for cmd in plan["plan"]]
    assert "add_atmosphere" in commands
    assert "add_directional_light" in commands
    assert "animate_fog" in commands
    print("✓ Complete scene test passed")


def test_presets():
    """Test all presets"""
    print("\n=== Test 6: Preset Values ===")
    
    with MovieBuilder("Test Presets", fps=30) as movie:
        # Test different density presets
        movie.add_atmosphere(fog_density="clear")
        movie.add_atmosphere(fog_density="light")
        movie.add_atmosphere(fog_density="medium")
        movie.add_atmosphere(fog_density="heavy")
        movie.add_atmosphere(fog_density="dense")
        
        # Test different color presets  
        movie.add_atmosphere(fog_color="atmospheric")
        movie.add_atmosphere(fog_color="warm_haze")
        movie.add_atmosphere(fog_color="mystical")
        movie.add_atmosphere(fog_color="forest")
        
        # Test light shaft presets
        movie.add_directional_light(actor_name="L1", light_shaft_bloom_scale="subtle")
        movie.add_directional_light(actor_name="L2", light_shaft_bloom_scale="cinematic")
        movie.add_directional_light(actor_name="L3", light_shaft_bloom_scale="dramatic")
        
        movie.save_to_json("dist/test_presets.json")
    
    print("✓ Preset test passed")


if __name__ == "__main__":
    print("="*60)
    print("ATMOSPHERE & VOLUMETRICS IMPLEMENTATION TESTS")
    print("="*60)
    
    try:
        test_basic_atmosphere()
        test_light_with_god_rays()
        test_animate_fog()
        test_configure_light_shafts()
        test_complete_scene()
        test_presets()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nNext steps:")
        print("1. Run one of the demo scripts:")
        print("   python movies/morning_fog_demo.py")
        print("   python movies/cathedral_god_rays.py")
        print("   python movies/mystical_forest.py")
        print("\n2. Trigger in Unreal:")
        print("   python trigger_movie.py dist/morning_fog_demo.json")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
