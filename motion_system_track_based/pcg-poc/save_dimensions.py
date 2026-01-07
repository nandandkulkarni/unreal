"""
Get Iceland Landscape Dimensions - Save to File
"""
import unreal

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\landscape_dimensions.txt"

with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("ICELAND LANDSCAPE DIMENSIONS\n")
    f.write("=" * 80 + "\n\n")
    
    world = unreal.EditorLevelLibrary.get_editor_world()
    landscapes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Landscape)
    
    if not landscapes:
        f.write("No landscape found\n")
        print("No landscape found")
    else:
        landscape = landscapes[0]
        f.write(f"Landscape: {landscape.get_name()}\n\n")
        
        bounds = landscape.get_actor_bounds(only_colliding_components=False)
        origin, extent = bounds
        
        width = extent.x * 2
        length = extent.y * 2
        height = extent.z * 2
        
        f.write("DIMENSIONS:\n")
        f.write(f"  Width (X):  {width:,.0f} units = {width/100:,.1f} meters\n")
        f.write(f"  Length (Y): {length:,.0f} units = {length/100:,.1f} meters\n")
        f.write(f"  Height (Z): {height:,.0f} units = {height/100:,.1f} meters\n\n")
        
        f.write("CENTER POINT:\n")
        f.write(f"  X: {origin.x:,.0f}\n")
        f.write(f"  Y: {origin.y:,.0f}\n")
        f.write(f"  Z: {origin.z:,.0f}\n\n")
        
        f.write("BOUNDING BOX:\n")
        f.write(f"  X Range: {origin.x - extent.x:,.0f} to {origin.x + extent.x:,.0f}\n")
        f.write(f"  Y Range: {origin.y - extent.y:,.0f} to {origin.y + extent.y:,.0f}\n")
        f.write(f"  Z Range: {origin.z - extent.z:,.0f} to {origin.z + extent.z:,.0f}\n\n")
        
        print(f"✓ Dimensions saved to: {output_file}")
        print(f"  Size: {width/100:,.1f}m x {length/100:,.1f}m")
        print(f"  Height variation: {height/100:,.1f}m")
