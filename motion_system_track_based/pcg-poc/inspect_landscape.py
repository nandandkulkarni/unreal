"""
Iceland Landscape Property Inspector
Shows what data and properties the landscape has
"""
import unreal

print("=" * 80)
print("ICELAND LANDSCAPE INSPECTOR")
print("=" * 80)

# Get current level
world = unreal.EditorLevelLibrary.get_editor_world()

# Find landscape actors
landscapes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Landscape)

if not landscapes:
    print("\n✗ No landscape found in current level")
    print("  Make sure you have the Iceland level open")
else:
    for i, landscape in enumerate(landscapes):
        print(f"\n🏔️  LANDSCAPE #{i+1}: {landscape.get_name()}")
        print("-" * 80)
        
        # Basic properties
        location = landscape.get_actor_location()
        scale = landscape.get_actor_scale3d()
        
        print(f"📍 Location: X={location.x:.1f}, Y={location.y:.1f}, Z={location.z:.1f}")
        print(f"📏 Scale: X={scale.x:.2f}, Y={scale.y:.2f}, Z={scale.z:.2f}")
        
        # Landscape-specific properties
        try:
            # Get landscape component
            components = landscape.get_components_by_class(unreal.LandscapeComponent)
            print(f"\n🔧 Components: {len(components)} landscape sections")
            
            # Material
            material = landscape.get_editor_property("landscape_material")
            if material:
                print(f"🎨 Material: {material.get_name()}")
            
            # Try to get bounds
            bounds = landscape.get_actor_bounds(only_colliding_components=False)
            if bounds:
                origin, extent = bounds
                print(f"\n📦 Bounds:")
                print(f"   Origin: X={origin.x:.1f}, Y={origin.y:.1f}, Z={origin.z:.1f}")
                print(f"   Extent: X={extent.x:.1f}, Y={extent.y:.1f}, Z={extent.z:.1f}")
                print(f"   Size: {extent.x*2:.1f} x {extent.y*2:.1f} units")
                print(f"   Height range: {extent.z*2:.1f} units")
            
        except Exception as e:
            print(f"⚠️  Could not get some properties: {e}")
        
        print("\n✅ This is REAL 3D GEOMETRY, not a JPEG!")
        print("   You can:")
        print("   • Query elevation at any X,Y coordinate")
        print("   • Place objects on the surface")
        print("   • Generate roads that follow the terrain")
        print("   • Add collision and physics")

print("\n" + "=" * 80)
print("WHAT THIS MEANS FOR ROAD GENERATION")
print("=" * 80)
print("✓ We can sample terrain height at any point")
print("✓ Roads can follow the actual 3D surface")
print("✓ We can detect slopes and avoid steep areas")
print("✓ Everything is real geometry with physics!")
