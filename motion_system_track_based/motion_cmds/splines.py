from __future__ import annotations
import math
from typing import Tuple, List, TYPE_CHECKING
from motion_structs.actor_data import SplineActor
import motion_math

if TYPE_CHECKING:
    from motion_builder import MovieBuilder
    from motion_cmds.actions import ActorBuilder

class SplineBuilder:
    """
    Builder for Spline configuration.
    """
    def __init__(self, movie_builder: 'MovieBuilder', name: str, points: List[Tuple[float, float, float]], closed: bool):
        self.mb = movie_builder
        self.spline = SplineActor(name, points, closed)
        self.mb.actors[name] = self.spline
        
    def color(self, color_name: str) -> 'SplineBuilder':
        """Set debug color (e.g. 'Red', 'Blue')."""
        self.spline.initial_state["properties"]["color"] = color_name
        return self
        
    def tension(self, value: float) -> 'SplineBuilder':
        """Set spline tension (0.0=sharp, 1.0=loose). Default 0.5"""
        self.spline.tension = value
        self.spline.initial_state["properties"]["tension"] = value
        return self
        
    def thickness(self, value: float) -> 'SplineBuilder':
        """Set debug line thickness."""
        self.spline.initial_state["properties"]["thickness"] = value
        return self

class SplineMotionCommandBuilder:
    """
    Builder for moving along a spline.
    """
    def __init__(self, actor_builder: 'ActorBuilder', spline_actor: SplineActor):
        self.ab = actor_builder
        self.spline = spline_actor
        self._speed_val = 5.0 # m/s default
        self._start_distance = 0.0 # meters
        self._end_distance = None # None = full length
        self._reverse = False
        self._anim_name = None
        self._anim_speed = 1.0
        self._use_motion_matching = False
        self._anim_db = "belica"  # Default animation database
        
    def speed(self, mps: float) -> 'SplineMotionCommandBuilder':
        """Set movement speed in meters per second."""
        self._speed_val = mps
        return self
        
    def reverse(self) -> 'SplineMotionCommandBuilder':
        """Move backwards along spline."""
        self._reverse = True
        return self
        
    def range(self, start_dist_m: float = 0.0, end_dist_m: float = None) -> 'SplineMotionCommandBuilder':
        """Set distance range on spline to traverse (in meters)."""
        self._start_distance = start_dist_m
        self._end_distance = end_dist_m
        return self
        
    def anim(self, name: str, speed_multiplier: float = 1.0) -> 'SplineMotionCommandBuilder':
        """Set explicit animation to loop."""
        self._anim_name = name
        self._anim_speed = speed_multiplier
        self._use_motion_matching = False
        return self

    def use_motion_match(self, anim_db: str = "belica") -> 'SplineMotionCommandBuilder':
        """Use Motion Matching to select animations based on speed.
        
        Args:
            anim_db: Animation database to use ("belica" or "manny")
        """
        self._use_motion_matching = True
        self._anim_db = anim_db
        return self # Terminal call is done separately? No this is builder.
        
    def run(self) -> 'ActorBuilder':
        """Terminal: Execute the move."""
        # 1. Sample the spline path
        # Estimate total length first to handle end_dist=None
        # Simple chord sum
        total_len = 0.0
        pts = self.spline.points
        if len(pts) > 1:
            for i in range(len(pts)-1):
                d = math.sqrt(sum((pts[i+1][k]-pts[i][k])**2 for k in range(3)))
                total_len += d
        # Convert to meters for interface
        total_len_m = total_len / 100.0
        
        target_end_m = self._end_distance if self._end_distance is not None else total_len_m
        if target_end_m > total_len_m: target_end_m = total_len_m
        
        dist_to_travel_m = abs(target_end_m - self._start_distance)
        duration = dist_to_travel_m / self._speed_val if self._speed_val > 0 else 0
        
        # Sample interval: every 10cm or so for smoothness
        samples = motion_math.sample_spline_path(
            self.spline.points,
            distance_total=total_len, # raw units
            sample_interval=10.0, # 10 cm
            closed=self.spline.closed,
            tension=self.spline.tension
        )
        
        # Filter samples to range
        start_cm = self._start_distance * 100.0
        end_cm = target_end_m * 100.0
        
        if self._reverse:
            # Logic for reverse traversal if needed
            pass # TODO
            
        # Select samples within range
        route_samples = [s for s in samples if start_cm <= s["distance"] <= end_cm]
        
        if not route_samples:
            return self.ab
            
        # Generate keyframes
        start_time = self.ab._current_time
        fps = self.ab.mb.fps
        
        for i, sample in enumerate(route_samples):
            # Calculate time for this sample based on constant speed
            # dist from start of ROUTE
            dist_from_route_start = sample["distance"] - start_cm
            t_offset = (dist_from_route_start / 100.0) / self._speed_val
            
            frame = int((start_time + t_offset) * fps)
            
            # Position
            pos = sample["pos"]
            
            # Orientation (Tangent)
            tangent = sample["tangent"]
            yaw = math.degrees(math.atan2(tangent[1], tangent[0]))
            
            # Pitch from slope
            # slope is stored in sample by motion_math
            pitch = sample.get("slope", 0.0)
            
            self.ab.track_set.transform.add_keyframe(
                frame, pos[0], pos[1], pos[2], 0.0, pitch, yaw
            )
            
            # Animation Handling
            # If simple anim:
            if self._anim_name:
                # Add segment if this is start or if gap?
                # Actually AnimationTrack uses start/end segments.
                # We can just add one big segment for the whole move if it's a loop.
                pass 
        
        # Add single animation segment for the whole move
        start_frame = int(start_time * fps)
        end_frame = int((start_time + duration) * fps)
        
        if self._use_motion_matching:
            # HYBRID MOTION MATCHING APPROACH
            # - Transform controls position (precise spline following)
            # - Animation speed matches movement speed (no foot sliding)
            # - Motion matching selects appropriate animation based on SPEED
            
            # Load animation database
            from motion_structs.anim_loader import find_animation_by_type
            
            # Select animation type based on movement speed
            # Walk: < 2.0 m/s
            # Jog: 2.0 - 4.5 m/s
            # Run: > 4.5 m/s
            if self._speed_val < 2.0:
                anim_type = "walk"
            elif self._speed_val < 4.5:
                anim_type = "jog"
            else:
                anim_type = "run"
            
            # Get animation from database
            anim_data = find_animation_by_type(anim_type, "forward", character=self._anim_db)
            
            # Smart Fallback: If RUN mapping fails (e.g. Manny has no run), try JOG
            if not anim_data and anim_type == "run":
                anim_data = find_animation_by_type("jog", "forward", character=self._anim_db)
            
            if anim_data:
                # Use full path if available (preferred), otherwise short name
                anim_name = anim_data.get("path", anim_data["name"])
                natural_speed = anim_data.get("natural_speed_mps", 3.5)
            else:
                # Ultimate Fallback if database totally fails
                print(f"Warning: No {anim_type} (or fallback) animation found in {self._anim_db} database.")
                # Try to guess a reasonable default for the character
                if self._anim_db == "manny":
                     # Use full path for fallback too
                     anim_name = "/Game/Characters/Mannequins/Anims/Pistol/Jog/MF_Pistol_Jog_Fwd.MF_Pistol_Jog_Fwd"
                else:
                     anim_name = "Jog_Fwd"
                natural_speed = 3.5
            
            # HYBRID: Calculate speed multiplier to match movement speed
            # speed_multiplier = actual_speed / natural_animation_speed
            speed_multiplier = self._speed_val / natural_speed if natural_speed > 0 else 1.0
            
            # Apply single animation for entire path
            self.ab.track_set.animation.add_segment(start_frame, end_frame, anim_name, speed_multiplier)
            
        elif self._anim_name:
            start_frame = int(start_time * fps)
            self.ab.track_set.animation.add_segment(start_frame, end_frame, self._anim_name, self._anim_speed)

        # Update actor state
        last_sample = route_samples[-1]
        self.ab.track_set.initial_state["location"] = list(last_sample["pos"])
        # Update rotation
        tangent = last_sample["tangent"]
        yaw = math.degrees(math.atan2(tangent[1], tangent[0]))
        self.ab.track_set.initial_state["rotation"] = [0, 0, yaw] # roll, pitch, yaw
        
        self.ab._current_time += duration
        return self.ab
