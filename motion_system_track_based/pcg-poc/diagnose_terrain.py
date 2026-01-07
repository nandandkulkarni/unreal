"""
Diagnostic script to check ISM component properties and try to force visibility
"""
import unreal

def diagnose_terrain():
    print("=" * 80)
    print("TERRAIN ISM DIAGNOSTIC")
    print("=" * 80)
    
    world = unreal.EditorLevelLibrary.get_editor_world()
    all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    
    terrain_manager = None
    for actor in all_actors:
        if "Garden_Terrain_Manager" in actor.get_actor_label():
            terrain_manager = actor
            break
    
    if not terrain_manager:
        print("✗ Terrain Manager not found!")
        return
    
    print(f"✓ Found Terrain Manager at: {terrain_manager.get_actor_location()}")
    print(f"  Actor Hidden in Game: {terrain_manager.is_hidden_ed()}")
    print(f"  Actor Visible: {terrain_manager.is_actor_being_destroyed()}")
    
    # Get ISM components
    ism_comps = terrain_manager.get_components_by_class(unreal.InstancedStaticMeshComponent)
    print(f"\n✓ Found {len(ism_comps)} ISM Components")
    
    for ism in ism_comps:
        print(f"\n  Component: {ism.get_name()}")
        print(f"    Instance Count: {ism.get_instance_count()}")
        print(f"    Static Mesh: {ism.static_mesh.get_name() if ism.static_mesh else 'None'}")
        print(f"    Visible: {ism.is_visible()}")
        print(f"    Mobility: {ism.mobility}")
        print(f"    Collision Enabled: {ism.get_collision_enabled()}")
        print(f"    Cast Shadow: {ism.cast_shadow}")
        
        # Try to get bounds
        if ism.get_instance_count() > 0:
            # Get first instance transform
            success, transform = ism.get_instance_transform(0, world_space=True)
            if success:
                print(f"    First Instance Location: {transform.translation}")
                print(f"    First Instance Scale: {transform.scale3d}")
    
    print("\n" + "=" * 80)
    print("Attempting to force visibility refresh...")
    
    # Try various methods to force visibility
    for ism in ism_comps:
        ism.set_visibility(True, propagate_to_children=True)
        ism.mark_render_state_dirty()
    
    # Force viewport refresh
    unreal.EditorLevelLibrary.editor_invalidate_viewports()
    print("✓ Viewports invalidated")
    
    print("=" * 80)

if __name__ == "__main__":
    diagnose_terrain()
