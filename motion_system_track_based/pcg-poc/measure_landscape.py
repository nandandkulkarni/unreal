"""
Get Iceland Landscape Dimensions
Measures the exact size of the landscape
"""
import unreal

print("=" * 80)
print("ICELAND LANDSCAPE DIMENSIONS")
print("=" * 80)

world = unreal.EditorLevelLibrary.get_editor_world()
landscapes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Landscape)

if not landscapes:
    print("\n✗ No landscape found - make sure Iceland level is open")
else:
    landscape = landscapes[0]
    print(f"\n🏔️  Landscape: {landscape.get_name()}")
    
    # Get bounds
    bounds = landscape.get_actor_bounds(only_colliding_components=False)
    origin, extent = bounds
    
    # Calculate dimensions
    width = extent.x * 2  # Extent is half-size
    length = extent.y * 2
    height = extent.z * 2
    
    print("\n📏 DIMENSIONS:")
    print(f"   Width (X):  {width:,.0f} units ({width/100:,.0f} meters)")
    print(f"   Length (Y): {length:,.0f} units ({length/100:,.0f} meters)")
    print(f"   Height (Z): {height:,.0f} units ({height/100:,.0f} meters)")
    
    print("\n📍 CENTER POINT:")
    print(f"   X: {origin.x:,.0f}")
    print(f"   Y: {origin.y:,.0f}")
    print(f"   Z: {origin.z:,.0f}")
    
    print("\n📦 BOUNDING BOX:")
    print(f"   Min X: {origin.x - extent.x:,.0f}")
    print(f"   Max X: {origin.x + extent.x:,.0f}")
    print(f"   Min Y: {origin.y - extent.y:,.0f}")
    print(f"   Max Y: {origin.y + extent.y:,.0f}")
    print(f"   Min Z: {origin.z - extent.z:,.0f}")
    print(f"   Max Z: {origin.z + extent.z:,.0f}")
    
    print("\n" + "=" * 80)
    print("FOR ROAD PLANNING:")
    print("=" * 80)
    print(f"✓ You have {width/100:,.0f}m x {length/100:,.0f}m of terrain to work with")
    print(f"✓ Elevation varies by {height/100:,.0f}m")
    print("✓ Use these bounds when defining road waypoints")
