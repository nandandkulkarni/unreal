from __future__ import annotations
from typing import List, TYPE_CHECKING
from motion_structs.actor_data import GroupTargetActor
from motion_includes.assets import Shapes
from motion_cmds.actions import ActorBuilder

if TYPE_CHECKING:
    from motion_builder import MovieBuilder

class GroupTargetBuilder:
    """
    Builder for GroupTargetActor configuration.
    """
    def __init__(self, movie_builder: 'MovieBuilder', name: str, members: List[str]):
        self.mb = movie_builder
        # Create actor immediately
        self.actor = GroupTargetActor(name, members)
        self.mb.actors[name] = self.actor
    
    def color(self, color_val: str) -> 'GroupTargetBuilder':
        """Set visualization color (e.g., 'Blue')."""
        if "properties" not in self.actor.initial_state:
            self.actor.initial_state["properties"] = {}
        self.actor.initial_state["properties"]["color"] = color_val
        return self
        
    def shape(self, shape_val: str) -> 'GroupTargetBuilder':
        """Set visualization shape (e.g., 'Cylinder')."""
        if "properties" not in self.actor.initial_state:
            self.actor.initial_state["properties"] = {}
        self.actor.initial_state["properties"]["shape"] = shape_val
        self.actor.initial_state["properties"]["actor_type"] = "marker"  # Ensure actor_type is set
        
        # Auto-map common shapes
        if shape_val.lower() == "cylinder":
            self.actor.initial_state["properties"]["mesh_path"] = Shapes.CYLINDER
            # Auto-scale to approx 10cm radius/width (Base is large)
            self.actor.initial_state["properties"]["mesh_scale"] = [0.1, 0.1, 1.0]  # Changed from "scale" to "mesh_scale"
        elif shape_val.lower() == "cube":
            self.actor.initial_state["properties"]["mesh_path"] = Shapes.CUBE
            # Default to 1m cube scale
            self.actor.initial_state["properties"]["mesh_scale"] = [1.0, 1.0, 1.0]
        
        return self

    def mesh_scale(self, x: float, y: float, z: float) -> 'GroupTargetBuilder':
        """Set explicit mesh scale."""
        if "properties" not in self.actor.initial_state:
            self.actor.initial_state["properties"] = {}
        self.actor.initial_state["properties"]["mesh_scale"] = [x, y, z]
        return self

    def interval(self, ms: float) -> 'GroupTargetBuilder':
        """Set recalculation interval in milliseconds."""
        self.actor.computation_interval_ms = ms
        return self

    def height(self, h_cm: float) -> 'GroupTargetBuilder':
        """Set marker height in cm."""
        if "properties" not in self.actor.initial_state:
            self.actor.initial_state["properties"] = {}
        
        # Default scale is 1.0 (100cm)
        scale_val = h_cm / 100.0
        
        if "mesh_scale" not in self.actor.initial_state["properties"]:
            self.actor.initial_state["properties"]["mesh_scale"] = [0.1, 0.1, scale_val]
        else:
            self.actor.initial_state["properties"]["mesh_scale"][2] = scale_val
            
        return self

    def radius(self, r_cm: float) -> 'GroupTargetBuilder':
        """Set marker radius in cm (sets X and Y scale)."""
        if "properties" not in self.actor.initial_state:
            self.actor.initial_state["properties"] = {}
        
        # Basis: 1.0 scale = 100cm diameter (50cm radius)
        # So scale = (r_cm * 2) / 100.0
        scale_val = (r_cm * 2) / 100.0
        
        if "mesh_scale" not in self.actor.initial_state["properties"]:
            self.actor.initial_state["properties"]["mesh_scale"] = [scale_val, scale_val, 1.0]
        else:
            self.actor.initial_state["properties"]["mesh_scale"][0] = scale_val
            self.actor.initial_state["properties"]["mesh_scale"][1] = scale_val
            
        return self


class SimultaneousContext:
    """
    Context manager for parallel actor scripting.
    
    All actors scripted within this context start at the same time.
    The context exits when the longest actor timeline completes.
    """
    
    def __init__(self, movie_builder: 'MovieBuilder'):
        self.mb = movie_builder
        self._start_time = movie_builder.current_time
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Set global time to longest actor completion."""
        # Find max time from all actors
        max_time = self._start_time
        for actor_name, track_set in self.mb.actors.items():
            # Estimate actor end time from last keyframe
            if track_set.transform.keyframes:
                last_frame = max(kf.frame for kf in track_set.transform.keyframes)
                actor_time = last_frame / self.mb.fps
                max_time = max(max_time, actor_time)
        self.mb.current_time = max_time
    
    def for_actor(self, actor_name: str) -> ActorBuilder:
        """Get actor builder within simultaneous context."""
        if actor_name not in self.mb.actors:
            raise ValueError(f"Actor '{actor_name}' not found.")
        builder = ActorBuilder(self.mb, actor_name)
        builder._current_time = self._start_time  # Reset to simultaneous start time
        return builder
