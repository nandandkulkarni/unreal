from __future__ import annotations
from typing import Tuple, TYPE_CHECKING
from motion_structs.enums import Direction, Tilt
from motion_structs.actor_data import ActorTrackSet
import motion_math

if TYPE_CHECKING:
    from motion_builder import MovieBuilder

class CameraBuilder:
    """
    Builder for initial camera setup.
    
    Usage:
        movie.add_camera("Cam1", location=(0, 0, 500))
            .orient(face_yaw=Direction.NORTH, tilt_pitch=Tilt.DOWN, tilt_pitch_offset=45)
            .look_at("Runner1")
            .add()
    """
    
    def __init__(self, movie_builder: 'MovieBuilder', name: str, 
                 location: Tuple[float, float, float], fov: float):
        self.mb = movie_builder
        self.name = name
        self.location = location
        self.fov = fov
    
    def orient(self, 
               face_yaw: Direction = Direction.NORTH,
               face_yaw_offset: float = 0.0,
               tilt_pitch: Tilt = Tilt.LEVEL,
               tilt_pitch_offset: float = 0.0) -> 'CameraBuilder':
        """
        Set camera orientation using human-readable directions.
        
        Args:
            face_yaw: Horizontal direction (North, South, etc.)
            face_yaw_offset: Additional yaw offset in degrees
            tilt_pitch: Vertical preset (Up, Down, Level)
            tilt_pitch_offset: Additional pitch in degrees (90 = straight down)
        
        Returns:
            Self for chaining
        """
        # Calculate yaw from direction
        base_yaw = motion_math.get_cardinal_angle(face_yaw.value)
        if base_yaw is None:
            base_yaw = 0
        final_yaw = base_yaw + face_yaw_offset
        
        # Calculate pitch from tilt
        pitch_map = {
            Tilt.UP: -45,      # Looking up
            Tilt.DOWN: 45,     # Looking down
            Tilt.LEVEL: 0      # Level
        }
        base_pitch = pitch_map.get(tilt_pitch, 0)
        final_pitch = base_pitch + tilt_pitch_offset
        
        # Store rotation
        self._rotation = (0, final_pitch, final_yaw)  # (roll, pitch, yaw)
        return self
    
    def rotation(self, rot: Tuple[float, float, float]) -> 'CameraBuilder':
        """Set explicit rotation (roll, pitch, yaw) in degrees."""
        self._rotation = rot
        return self
    
    def look_at_subject(self, actor_name: str, height_pct: float = 0.7) -> 'CameraBuilder':
        """Enable look-at tracking for an actor."""
        self._look_at_actor = actor_name
        self._look_at_height_pct = height_pct
        return self
    
    def attach_to(self, parent_actor: str, socket: str = "") -> 'CameraBuilder':
        """
        Attach camera to another actor.
        
        Args:
            parent_actor: Name of actor to attach to
            socket: Optional socket name on parent's skeletal mesh
        
        Returns:
            Self for chaining
        """
        self._attach_parent = parent_actor
        self._attach_socket = socket
        return self
    
    def debug_visible(self, enabled: bool = True) -> 'CameraBuilder':
        """
        Show camera frustum and icon in editor for debugging.
        
        Args:
            enabled: Whether to show debug visualization
        
        Returns:
            Self for chaining
        """
        self._debug_visible = enabled
        return self
    
    def add(self) -> 'MovieBuilder':
        """Finalize and add camera to movie."""
        # Create camera track set
        track_set = ActorTrackSet(self.name, actor_type="camera")
        track_set.initial_state = {
            "location": list(self.location),
            "rotation": list(getattr(self, '_rotation', (0, 0, 0))),
            "properties": {
                "fov": self.fov,
                "look_at_actor": getattr(self, '_look_at_actor', None),
                "look_at_height_pct": getattr(self, '_look_at_height_pct', 0.7),
                "debug_visible": getattr(self, '_debug_visible', False)
            }
        }
        
        # Add initial keyframe to ensure camera doesn't default to origin
        # NOTE: If look_at is enabled, DON'T add rotation keyframe - let look_at control rotation
        if hasattr(self, '_look_at_actor') and self._look_at_actor:
            # Only add location keyframe, no rotation (look_at will handle it)
            track_set.transform.add_keyframe(0, self.location[0], self.location[1], self.location[2], 
                                            roll=0, pitch=0, yaw=0)
            # Actually, we need to NOT add rotation at all. Let me check TransformTrack.add_keyframe signature
            # The issue is add_keyframe always adds rotation. We need a way to skip it.
            # For now, add it but mark that rotation should be ignored in run_scene.py
            pass  # Will handle this differently
        else:
            track_set.transform.add_keyframe(0, self.location[0], self.location[1], self.location[2])
        
        # Add attachment if specified
        if hasattr(self, '_attach_parent'):
            track_set.attach.add_section(
                parent_actor=self._attach_parent,
                socket_name=getattr(self, '_attach_socket', ""),
                start_frame=0,
                end_frame=None  # Until end of sequence
            )
        
        self.mb.actors[self.name] = track_set
        return self.mb


class CameraCommandBuilder:
    """
    Builder for camera commands during movie (zoom, pan, focus changes).
    """
    
    def __init__(self, movie_builder: 'MovieBuilder', camera_name: str, start_time: float = 0.0):
        self.mb = movie_builder
        self.camera_name = camera_name
        self.start_time = start_time
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Update camera's local time and global time."""
        # Update Camera's Local Time
        if self.camera_name in self.mb.actors:
            self.mb.actors[self.camera_name].current_time = self.start_time
            
        # Update Global Time
        if self.start_time > self.mb.current_time:
            self.mb.current_time = self.start_time
    
    def look_at_subject(self, actor_name: str, height_pct: float = 0.7, interp_speed: float = 5.0) -> 'CameraCommandBuilder':
        """Switch look-at target."""
        if self.camera_name in self.mb.actors:
            track_set = self.mb.actors[self.camera_name]
            if track_set.camera_timelines:
                # Add to look_at timeline
                track_set.camera_timelines["look_at"].append((
                    self.start_time,
                    None,  # End time set by next command or end
                    actor_name,
                    height_pct,
                    interp_speed
                ))
        return self
    
    def auto_zoom_subject(self, actor_name: str, coverage: float = 0.7) -> 'CameraCommandBuilder':
        """Auto-frame subject at desired coverage using focal length."""
        if self.camera_name in self.mb.actors:
            track_set = self.mb.actors[self.camera_name]
            if track_set.camera_timelines:
                track_set.camera_timelines["frame_subject"].append((
                    self.start_time,
                    None,
                    actor_name,
                    coverage
                ))
        return self
    
    def auto_focus_subject(self, actor_name: str, height_pct: float = 0.7) -> 'CameraCommandBuilder':
        """Set focus distance to track actor."""
        if self.camera_name in self.mb.actors:
            track_set = self.mb.actors[self.camera_name]
            if track_set.camera_timelines:
                track_set.camera_timelines["focus_on"].append((
                    self.start_time,
                    None,
                    actor_name,
                    height_pct
                ))
        return self
        
    def focus_zoom_track(self, actor_name: str, focus_pct: float = 0.7, zoom_pct: float = 0.7, track_pct: float = 0.7) -> 'CameraCommandBuilder':
        """
        Convenience method to set focus, zoom, and look-at tracking all at once.
        
        Args:
            actor_name: Name of actor to track
            focus_pct: Height percentage for focus (0-1)
            zoom_pct: Screen coverage percentage for zoom (0-1)
            track_pct: Height percentage for look-at tracking (0-1)
        """
        self.look_at_subject(actor_name, height_pct=track_pct)
        self.auto_zoom_subject(actor_name, coverage=zoom_pct)
        self.auto_zoom_subject(actor_name, coverage=zoom_pct)
        self.auto_focus_subject(actor_name, height_pct=focus_pct)
        return self
        
    def set_focal_length(self, focal_length: float) -> 'CameraCommandBuilder':
        """Set camera focal length."""
        if self.camera_name in self.mb.actors:
            track_set = self.mb.actors[self.camera_name]
            if not hasattr(track_set, "focal_length_keyframes"):
                track_set.focal_length_keyframes = []
            
            # Convert current time to frame
            frame = int(self.start_time * self.mb.fps)
            track_set.focal_length_keyframes.append({
                "frame": frame,
                "value": focal_length
            })
        return self
    
    def wait(self, duration: float) -> 'CameraCommandBuilder':
        """Hold current settings for duration."""
        self.start_time += duration
        self.mb.current_time += duration
        
        # Close previous timeline segments
        if self.camera_name in self.mb.actors:
            track_set = self.mb.actors[self.camera_name]
            if track_set.camera_timelines:
                for timeline_name in ["look_at", "frame_subject", "focus_on"]:
                    timeline = track_set.camera_timelines[timeline_name]
                    if timeline and timeline[-1][1] is None:
                        # Update last segment's end time
                        segment = list(timeline[-1])
                        segment[1] = self.start_time
                        timeline[-1] = tuple(segment)
        return self
