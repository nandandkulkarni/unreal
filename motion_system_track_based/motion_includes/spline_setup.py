import unreal

def create_spline_actor(name, points, closed=False, color="Green", thickness=5.0, show_debug=True):
    """
    Spawn an actor with a SplineComponent and populate it.
    
    Args:
        name: Actor label
        points: List of (x, y, z) tuples
        closed: Whether loop is closed
        color: Debug color name
        thickness: Debug line thickness
        show_debug: Whether to draw debug visualization
    
    Returns:
        The spawned Actor
    """
    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_subsystem.get_editor_world()
    
    location = unreal.Vector(0,0,0)
    rotation = unreal.Rotator(0,0,0)
    
    # Spawn empty actor
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, location, rotation)
    actor.set_actor_label(name)
    
    # Create Spline Component
    spline_comp = unreal.SplineComponent(name="SplineComp", outer=actor)
    
    # We must use set_editor_property for ReadOnly properties usually, 
    # but constructing it locally we might need to attach it.
    # standard workflow: actor.set_root_component(comp) - distinct in python
    
    # Attach to root
    # For a fresh actor, we can just making it the root or add it.
    # But usually a fresh 'Actor' has a 'SceneComponent' root or None? 
    # Just creating it doesn't attach.
    
    # The clean way in Editor Python:
    # Use AddComponent() equivalent via subobject or reflection?
    # Simple way: Just make a blueprint or use existing patterns.
    # Or:
    actor.set_editor_property("root_component", spline_comp)
    spline_comp.register_component() # Important!
    
    # Clear default points
    spline_comp.clear_spline_points()
    
    # Add points
    for i, p in enumerate(points):
        vec = unreal.Vector(p[0], p[1], p[2])
        spline_comp.add_spline_point(vec, unreal.SplineCoordinateSpace.LOCAL)
        
    spline_comp.set_closed_loop(closed)
    
    # Visualization
    if show_debug:
        # We can't easily force "Draw Debug" on a component permanently via Python 
        # unless we use `Duration` in DrawDebugLine per tick (which we can't do easily in Editor script).
        # HOWEVER, SplineComponent has 'bDrawDebug' or 'bShouldVisualizeScale'.
        # Actually usually it's only visible when selected.
        # To make it ALWAYS visible, we is tricky without a BP.
        # A trick: Add a SplineMesh? Or use DrawDebugLine for a long duration?
        # But DrawDebugLine clears.
        
        # Better approach for "Movie":
        # We will use `unreal.SystemLibrary.draw_debug_line` for a LONG duration (e.g. 1000s)
        # Iterate points and draw segments.
        draw_duration = 10000.0
        
        # Parse color
        # Basic mapping
        c = unreal.LinearColor(0, 1, 0, 1) # Green
        if color.lower() == "red": c = unreal.LinearColor(1, 0, 0, 1)
        elif color.lower() == "blue": c = unreal.LinearColor(0, 0, 1, 1)
        elif color.lower() == "yellow": c = unreal.LinearColor(1, 1, 0, 1)
        
        num_points = spline_comp.get_number_of_spline_points()
        for i in range(num_points - 1):
            p1 = spline_comp.get_location_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
            p2 = spline_comp.get_location_at_spline_point(i+1, unreal.SplineCoordinateSpace.WORLD)
            unreal.SystemLibrary.draw_debug_line(world, p1, p2, c, duration=draw_duration, thickness=thickness)
            
        if closed:
            p1 = spline_comp.get_location_at_spline_point(num_points-1, unreal.SplineCoordinateSpace.WORLD)
            p2 = spline_comp.get_location_at_spline_point(0, unreal.SplineCoordinateSpace.WORLD)
            unreal.SystemLibrary.draw_debug_line(world, p1, p2, c, duration=draw_duration, thickness=thickness)
            
    return actor
