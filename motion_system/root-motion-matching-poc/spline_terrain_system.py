"""
Spline Terrain System

Provides tools for creating and sampling splines for character movement.
Supports both manual 3D points and automatic terrain conforming.
"""

import unreal

class SplinePathBuilder:
    """
    Builder for creating character movement paths using SplineComponents.
    """
    
    def __init__(self):
        self._points = []
        self._spline_actor = None
        
    def add_point(self, location):
        """
        Add a point to the path.
        Args:
            location: unreal.Vector or tuple (x, y, z)
        """
        if isinstance(location, (tuple, list)):
            location = unreal.Vector(*location)
        self._points.append(location)
        
    def build_spline(self, world=None):
        """
        Build the spline actor in the world from the added points.
        """
        if not self._points:
            raise ValueError("No points added to builder")
            
        # Get/Create world if needed (though usually we just spawn in the current editor world)
        if not world:
            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            world = editor_subsystem.get_editor_world()
            
        # Spawn an actor to hold the spline
        # We can use a generic actor or a specific helper blueprint if we had one.
        # For python, spawning a basic TargetPoint or EmptyActor and adding a component is strictly 
        # harder than just using an actor that has one, but we can try creating a temporary SplineMesh actor 
        # or checking if we can just spawn a SplineActor. 
        # Actually, best way in Editor python is typically to spawn a generic actor and add a SplineComponent.
        
        # NOTE: Working with Components dynamically in Python can be tricky. 
        # A simpler way often used is to load a Blueprint that already has a SplineComponent.
        # But let's try to spawn a basic actor and add the component.
        
        # Strategy: Spawn a generic actor using EditorLevelLibrary
        actor_class = unreal.Actor
        self._spline_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, self._points[0], unreal.Rotator(0,0,0))
        self._spline_actor.set_actor_label("ProceduralPathSpline")
        
        # Strategy: Create component using constructor and assign via set_editor_property
        self._spline_comp = unreal.SplineComponent(name="SplineComp", outer=self._spline_actor)
        self._spline_actor.set_editor_property("root_component", self._spline_comp)
        
        # Clear default points
        self._spline_comp.clear_spline_points()
        
        # Add our points
        for i, pt in enumerate(self._points):
            self._spline_comp.add_spline_point(pt, unreal.SplineCoordinateSpace.WORLD)
            # Make the curve smooth
            self._spline_comp.set_spline_point_type(i, unreal.SplinePointType.CURVE)
            
        self._spline_comp.update_spline()
        
        return self._spline_comp

    def sample_spline(self, distance):
        """
        Sample position and tangent at a given distance along the spline.
        Returns:
            (position, direction_vector)
        """
        if not self._spline_actor or not self._spline_comp:
            raise RuntimeError("Spline not built yet")
            
        location = self._spline_comp.get_location_at_distance_along_spline(
            distance, unreal.SplineCoordinateSpace.WORLD
        )
        tangent = self._spline_comp.get_tangent_at_distance_along_spline(
            distance, unreal.SplineCoordinateSpace.WORLD
        )
        
        # Normalize tangent to get direction
        direction = tangent.normal()
        
        return location, direction
        
    def get_length(self):
        """Return total length of the spline"""
        if self._spline_comp:
            return self._spline_comp.get_spline_length()
        return 0.0

    def cleanup(self):
        """Destroy the temporary spline actor"""
        if self._spline_actor:
            try:
                self._spline_actor.destroy_actor()
            except:
                pass
            self._spline_actor = None
            self._spline_comp = None
