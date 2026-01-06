from __future__ import annotations
import math
from typing import Union, Tuple, TYPE_CHECKING
from motion_structs.enums import Direction
import motion_math
if TYPE_CHECKING:
    from motion_builder import MovieBuilder

class ActorBuilder:
    """
    Fluent builder for actor commands within a movie context.
    
    Provides methods like move_straight(), stay(), face() that
    generate keyframes on the actor's tracks.
    """
    
    def __init__(self, movie_builder: 'MovieBuilder', actor_name: str, start_time: float = 0.0):
        self.mb = movie_builder
        self.actor_name = actor_name
        self.track_set = movie_builder.actors.get(actor_name)
        self._current_time = start_time  # Local timeline cursor
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Update actor's local time and global time."""
        # Update Actor's Local Time
        self.track_set.current_time = self._current_time
        
        # Update Global Time (to max extended)
        if self._current_time > self.mb.current_time:
            self.mb.current_time = self._current_time
    
    def move_straight(self) -> 'MotionCommandBuilder':
        """
        Begin a movement command.
        
        Returns:
            MotionCommandBuilder for fluent configuration
        """
        return MotionCommandBuilder(self)
    
    def stay(self) -> 'StayCommandBuilder':
        """
        Begin a stationary command.
        
        Returns:
            StayCommandBuilder for fluent configuration
        """
        return StayCommandBuilder(self)
    
    def face(self, direction: Direction, duration: float = 1.0) -> 'ActorBuilder':
        """
        Rotate actor to face a direction.
        
        Args:
            direction: Target direction (Direction enum)
            duration: Time to complete rotation
        
        Returns:
            Self for chaining
        """
        if not isinstance(direction, Direction):
            raise ValueError(f"direction must be a Direction Enum. Got: {direction}")
        
        # Get target yaw from direction
        target_yaw_logical = motion_math.get_cardinal_angle(direction.value)
        if target_yaw_logical is None:
            raise ValueError(f"Invalid direction: {direction}")
            
        # Apply persistent mesh offset
        target_yaw = target_yaw_logical + self.track_set.mesh_yaw_offset
        
        # Get current rotation from track set
        current_yaw = self.track_set.initial_state["rotation"][1]  # [roll, pitch, yaw]
        
        # Calculate shortest path
        final_yaw = motion_math.get_shortest_path_yaw(current_yaw, target_yaw)
        
        # Add rotation keyframes
        start_frame = int(self._current_time * self.mb.fps)
        end_frame = int((self._current_time + duration) * self.mb.fps)
        
        # Get current location
        loc = self.track_set.initial_state["location"]
        
        # Start keyframe (current rotation)
        self.track_set.transform.add_keyframe(start_frame, loc[0], loc[1], loc[2], 0, 0, current_yaw)
        
        # End keyframe (new rotation)
        self.track_set.transform.add_keyframe(end_frame, loc[0], loc[1], loc[2], 0, 0, final_yaw)
        
        # Update state
        self.track_set.initial_state["rotation"][1] = final_yaw
        self._current_time += duration
        
        return self
    
    def wait(self, seconds: float) -> 'ActorBuilder':
        """
        Wait without moving or animating.
        
        Args:
            seconds: Duration to wait
        
        Returns:
            Self for chaining
        """
        self._current_time += seconds
        return self
    
    def wait_until(self, time_sec: float) -> 'ActorBuilder':
        """
        Wait until a specific time in the sequence.
        
        Args:
            time_sec: Target time in seconds
        
        Returns:
            Self for chaining
        """
        if time_sec > self._current_time:
            self._current_time = time_sec
        return self
    
    def face_actor(self, target_actor_name: str, duration: float = 1.0) -> 'ActorBuilder':
        """
        Rotate actor to face another actor.
        
        Args:
            target_actor_name: Name of target actor to face
            duration: Time to complete rotation
        
        Returns:
            Self for chaining
        """
        if target_actor_name not in self.mb.actors:
            raise ValueError(f"Target actor '{target_actor_name}' not found")
        
        target_state = self.mb.actors[target_actor_name].initial_state
        target_loc = target_state["location"]
        
        current_loc = self.track_set.initial_state["location"]
        
        # Calculate angle to target
        dx = target_loc[0] - current_loc[0]
        dy = target_loc[1] - current_loc[1]
        target_yaw = math.degrees(math.atan2(dy, dx))
        
        current_yaw = self.track_set.initial_state["rotation"][1]
        final_yaw = motion_math.get_shortest_path_yaw(current_yaw, target_yaw)
        
        # Add rotation keyframes
        start_frame = int(self._current_time * self.mb.fps)
        end_frame = int((self._current_time + duration) * self.mb.fps)
        
        loc = current_loc
        self.track_set.transform.add_keyframe(start_frame, loc[0], loc[1], loc[2], 0, 0, current_yaw)
        self.track_set.transform.add_keyframe(end_frame, loc[0], loc[1], loc[2], 0, 0, final_yaw)
        
        self.track_set.initial_state["rotation"][1] = final_yaw
        self._current_time += duration
        
        return self
        
    def move_along_spline(self, spline_name: str) -> 'SplineMotionCommandBuilder':
        """
        Begin movement along a spline path.
        
        Args:
            spline_name: Name of existing spline actor
            
        Returns:
            SplineMotionCommandBuilder
        """
        if spline_name not in self.mb.actors:
             raise ValueError(f"Spline '{spline_name}' not found. Add it with movie.add_spline() first.")
             
        spline_actor = self.mb.actors[spline_name]
        from motion_structs.actor_data import SplineActor
        if not isinstance(spline_actor, SplineActor):
             raise ValueError(f"Actor '{spline_name}' is not a SplineActor.")
             
        from motion_cmds.splines import SplineMotionCommandBuilder
        return SplineMotionCommandBuilder(self, spline_actor)


class MotionCommandBuilder:
    """
    Builder for movement commands.
    
    Fluent API:
        actor.move_straight()
            .direction(Direction.NORTH)
            .anim("Jog_Fwd")
            .distance_at_speed(100, 6)  # Terminal method
    """
    
    def __init__(self, actor_builder: ActorBuilder):
        self.ab = actor_builder
        self._direction = None  # Explicit direction required
        self._anim_name = None
        self._anim_speed = 1.0
    
    def direction(self, dir_enum: Direction) -> 'MotionCommandBuilder':
        """Set movement direction."""
        if not isinstance(dir_enum, Direction):
            raise ValueError(f"direction must be a Direction Enum. Got: {dir_enum}")
        self._direction = dir_enum
        return self
    
    def anim(self, name: str, speed_multiplier: float = 1.0) -> 'MotionCommandBuilder':
        """Set movement animation."""
        self._anim_name = name
        self._anim_speed = speed_multiplier
        return self
    
    def distance_at_speed(self, meters: Union[float, Tuple], 
                          speed_mps: Union[float, Tuple]) -> ActorBuilder:
        """
        Terminal: Move distance at speed (calculates duration).
        
        Generates transform and animation keyframes.
        
        Returns:
            ActorBuilder for continued chaining
        """
        # Handle unit tuples
        m_val = meters
        if isinstance(meters, tuple):
            m_val = meters[1] * meters[0].value
        
        sp_val = speed_mps
        if isinstance(speed_mps, tuple):
            sp_val = speed_mps[1] * speed_mps[0].value
        
        # Calculate duration
        duration = m_val / sp_val if sp_val > 0 else 0
        
        # Generate keyframes
        self._generate_movement_keyframes(m_val, duration)
        
        return self.ab
    
    def distance_in_time(self, meters: Union[float, Tuple],
                         seconds: Union[float, Tuple]) -> ActorBuilder:
        """
        Terminal: Move distance in time (calculates speed).
        
        Args:
            meters: Distance to move
            seconds: Duration of move
        """
        # Handle unit tuples
        m_val = meters
        if isinstance(meters, tuple):
            m_val = meters[1] * meters[0].value
            
        s_val = seconds
        if isinstance(seconds, tuple):
            s_val = seconds[1] * seconds[0].value
            
        self._generate_movement_keyframes(m_val, s_val)
        return self.ab
    
    def time_at_speed(self, seconds: Union[float, Tuple],
                      speed_mps: Union[float, Tuple]) -> ActorBuilder:
        """Terminal: Move for time at speed (calculates distance)."""
        # Handle unit tuples
        s_val = seconds
        if isinstance(seconds, tuple):
            s_val = seconds[1] * seconds[0].value
        
        sp_val = speed_mps
        if isinstance(speed_mps, tuple):
            sp_val = speed_mps[1] * speed_mps[0].value
        
        # Calculate distance
        m_val = s_val * sp_val
        
        # Generate keyframes
        self._generate_movement_keyframes(m_val, s_val)
        
        return self.ab
    
    def _generate_movement_keyframes(self, distance_m: float, duration_s: float):
        """Helper to generate transform and animation keyframes."""
        if self._direction is None:
            raise ValueError("Direction must be set explicitly (e.g. .direction(Direction.NORTH)). Relative 'Forward' is not supported.")
            
        # Get current state
        start_loc = self.ab.track_set.initial_state["location"]
        current_yaw = self.ab.track_set.initial_state["rotation"][1]
        
        # Calculate movement vector
        dir_vec = motion_math.calculate_direction_vector(self._direction.value, current_yaw)
        
        # Calculate end position (distance in meters, convert to cm for Unreal)
        distance_cm = distance_m * 100
        end_x = start_loc[0] + dir_vec["x"] * distance_cm
        end_y = start_loc[1] + dir_vec["y"] * distance_cm
        end_z = start_loc[2]  # Keep same height
        
        # Frame calculations
        start_frame = int(self.ab._current_time * self.ab.mb.fps)
        end_frame = int((self.ab._current_time + duration_s) * self.ab.mb.fps)
        
        # Add transform keyframes
        self.ab.track_set.transform.add_keyframe(
            start_frame, start_loc[0], start_loc[1], start_loc[2], 0, 0, current_yaw
        )
        self.ab.track_set.transform.add_keyframe(
            end_frame, end_x, end_y, end_z, 0, 0, current_yaw
        )
        
        # Add animation segment if specified
        if self._anim_name and self.ab.track_set.animation:
            self.ab.track_set.animation.add_segment(
                start_frame, end_frame, self._anim_name, self._anim_speed
            )
        
        # Update state
        self.ab.track_set.initial_state["location"] = [end_x, end_y, end_z]
        self.ab._current_time += duration_s


class StayCommandBuilder:
    """
    Builder for stationary commands.
    
    Fluent API:
        actor.stay().for_time(2.0).anim("Idle")
        actor.stay().till_end().anim("Idle")
    """
    
    def __init__(self, actor_builder: ActorBuilder):
        self.ab = actor_builder
        self.start_time = self.ab._current_time
    
    def for_time(self, duration: float) -> 'StayCommandBuilder':
        """Stay for specified duration."""
        self._duration = duration
        
        # Apply the stay (add end keyframe)
        # We keep the SAME location and rotation
        end_time = self.start_time + duration
        end_frame = int(end_time * self.ab.mb.fps)
        
        # Ensure we have the current state captured at end frame
        loc = self.ab.track_set.initial_state["location"]
        rot = self.ab.track_set.initial_state["rotation"]
        
        self.ab.track_set.transform.add_keyframe(
            end_frame, 
            loc[0], loc[1], loc[2], 
            rot[0], rot[1], rot[2]
        )
        
        # Advance actor time
        self.ab._current_time = end_time
        
        return self
    
    def till_end(self) -> 'StayCommandBuilder':
        """Stay until movie ends (resolved at finalization)."""
        # Use a large duration - will be trimmed to sequence end by Unreal
        duration = 999.0
        return self.for_time(duration)
    
    def anim(self, name: str, speed_multiplier: float = 1.0) -> 'StayCommandBuilder':
        """Set idle animation during stay."""
        # Generate animation segment for stay duration
        if hasattr(self, '_duration') and self.ab.track_set.animation:
            start_frame = int(self.start_time * self.ab.mb.fps)
            end_frame = int((self.start_time + self._duration) * self.ab.mb.fps)
            self.ab.track_set.animation.add_segment(start_frame, end_frame, name, speed_multiplier)
        return self
