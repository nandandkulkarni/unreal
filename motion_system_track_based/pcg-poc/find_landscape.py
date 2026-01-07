"""
Find and Measure ALL Actors in Current Level
"""
import unreal

output_file = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\level_info.txt"

with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("CURRENT LEVEL INFORMATION\n")
    f.write("=" * 80 + "\n\n")
    
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    # Get world name
    world_name = world.get_name() if world else "Unknown"
    f.write(f"World: {world_name}\n\n")
    
    # Get ALL actors
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    f.write(f"Total Actors in Level: {len(all_actors)}\n\n")
    
    # Find landscapes specifically
    f.write("SEARCHING FOR LANDSCAPES:\n")
    f.write("-" * 80 + "\n")
    
    landscape_found = False
    for actor in all_actors:
        actor_class = actor.get_class().get_name()
        if 'Landscape' in actor_class:
            landscape_found = True
            actor_name = actor.get_name()
            f.write(f"\nFound: {actor_name} ({actor_class})\n")
            
            # Get bounds
            try:
                bounds = actor.get_actor_bounds(only_colliding_components=False)
                origin, extent = bounds
                
                width = extent.x * 2
                length = extent.y * 2
                height = extent.z * 2
                
                f.write(f"\nDIMENSIONS:\n")
                f.write(f"  Width:  {width:,.0f} units = {width/100:,.1f} meters\n")
                f.write(f"  Length: {length:,.0f} units = {length/100:,.1f} meters\n")
                f.write(f"  Height: {height:,.0f} units = {height/100:,.1f} meters\n")
                
                f.write(f"\nBOUNDS:\n")
                f.write(f"  X: {origin.x - extent.x:,.0f} to {origin.x + extent.x:,.0f}\n")
                f.write(f"  Y: {origin.y - extent.y:,.0f} to {origin.y + extent.y:,.0f}\n")
                f.write(f"  Z: {origin.z - extent.z:,.0f} to {origin.z + extent.z:,.0f}\n")
                
                print(f"✓ Found landscape: {width/100:.0f}m x {length/100:.0f}m")
                
            except Exception as e:
                f.write(f"  Error getting bounds: {e}\n")
    
    if not landscape_found:
        f.write("\nNo landscape actors found!\n")
        f.write("\nAll actor types in level:\n")
        actor_types = {}
        for actor in all_actors[:50]:  # First 50
            actor_class = actor.get_class().get_name()
            actor_types[actor_class] = actor_types.get(actor_class, 0) + 1
        
        for actor_type, count in sorted(actor_types.items()):
            f.write(f"  {actor_type}: {count}\n")

print(f"✓ Saved to: {output_file}")
