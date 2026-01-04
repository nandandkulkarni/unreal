"""
Track-Based Motion Builder

This module provides a fluent API for defining motion sequences that are
stored in a track-based file structure (one JSON file per actor per property).

Architecture:
    MovieBuilder
    └── ActorTrackSet (per actor)
        ├── TransformTrack (location + rotation keyframes)
        ├── AnimationTrack (animation segments)
        └── SettingsTrack (actor-specific settings)

Output Structure:
    dist/movie_name/
    ├── meta.json           # {name, fps, duration, actors: [...]}
    ├── ActorName/
    │   ├── transform.json  # [{frame, x, y, z, roll, pitch, yaw}, ...]
    │   └── animation.json  # [{start_frame, end_frame, name, speed}, ...]
    └── CameraName/
        ├── transform.json
        └── settings.json   # [{frame, fov, focus_distance, look_at}, ...]
"""
import copy
from typing import Dict, List, Optional, Union, Tuple, Any
from enum import Enum
import math
import os
import json

from motion_includes.assets import Shapes
import motion_math


# =============================================================================
# ENUMS
# =============================================================================

class Direction(Enum):
    """Cardinal and diagonal directions for movement and facing."""
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    NORTH_EAST = "North_East"
    NORTH_WEST = "North_West"
    SOUTH_EAST = "South_East"
    SOUTH_WEST = "South_West"


class Tilt(Enum):
    """Vertical camera orientation presets."""
    UP = "Up"       # Looking upward (negative pitch)
    DOWN = "Down"   # Looking downward (positive pitch)
    LEVEL = "Level" # Horizontal (pitch = 0)


class DistanceUnit(Enum):
    """Distance units with conversion factor to meters."""
    Meters = 1.0
    Centimeters = 0.01
    Kilometers = 1000.0
    Feet = 0.3048


class LightType(Enum):
    POINT = "Point"
    DIRECTIONAL = "Directional"
    SPOT = "Spot"
    RECT = "Rect"
    SKY = "Sky"

class LightColor(Enum):
    # Standard Temps
    WHITE = (1.0, 1.0, 1.0)
    WARM_WHITE = (1.0, 0.9, 0.7)
    COOL_WHITE = (0.7, 0.8, 1.0)
    # Basic Colors
    RED = (1.0, 0.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    # Nature
    SUNLIGHT = (1.0, 0.95, 0.9)
    MOONLIGHT = (0.6, 0.7, 0.9)

class LightUnit(Enum):
    UNITLESS = 0
    LUMENS = 1
    CANDELAS = 2


class TimeUnit(Enum):
    """Time units with conversion factor to seconds."""
    Seconds = 1.0
    Minutes = 60.0
    Hours = 3600.0


class SpeedUnit(Enum):
    """Speed units with conversion factor to meters/second."""
    MetersPerSecond = 1.0
    KilometersPerHour = 0.277778
    MilesPerHour = 0.44704

# =============================================================================
# GLOBAL CONSTANTS
# =============================================================================
CHARACTER_HEIGHT = 180.0  # Standard human height in cm
MARKER_HEIGHT = 100.0     # Standard marker/sphere/cylinder height in cm


# =============================================================================
# TRACK DATA STRUCTURES
# =============================================================================

class Keyframe:
    """
    A single keyframe in a track.
    
    Attributes:
        frame: The frame number (integer, based on FPS)
        data: Dictionary of property values at this frame
    """
    def __init__(self, frame: int, **data):
        self.frame = frame
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {"frame": self.frame, **self.data}


class Track:
    """
    Base class for property tracks.
    
    A track contains a list of keyframes for a specific property
    (transform, animation, settings, etc.)
    
    Attributes:
        name: Track identifier (e.g., "transform", "animation")
        keyframes: List of Keyframe objects, sorted by frame
    """
    def __init__(self, name: str):
        self.name = name
        self.keyframes: List[Keyframe] = []
    
    def add_keyframe(self, frame: int, **data) -> 'Track':
        """
        Add a keyframe to this track.
        
        Args:
            frame: Frame number
            **data: Property values (e.g., x=100, y=200, z=0)
        
        Returns:
            Self for chaining
        """
        # TODO: Insert sorted, handle duplicates
        raise NotImplementedError("Subclass must implement")
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Serialize all keyframes to JSON-compatible list."""
        return [kf.to_dict() for kf in self.keyframes]
    
    def save(self, folder_path: str):
        """
        Save this track to a JSON file.
        
        Args:
            folder_path: Path to actor folder (e.g., dist/movie/Runner1/)
        """
        file_path = os.path.join(folder_path, f"{self.name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


class TransformTrack(Track):
    """
    Track for location and rotation keyframes.
    
    Keyframe data: {x, y, z, roll, pitch, yaw}
    """
    def __init__(self):
        super().__init__("transform")
    
    def get_location_at_frame(self, frame: float) -> Tuple[float, float, float]:
        """Interpolate location at a specific frame."""
        if not self.keyframes:
            return (0.0, 0.0, 0.0)
            
        # Boundary checks
        if frame <= self.keyframes[0].frame:
            d = self.keyframes[0].data
            return (d['x'], d['y'], d['z'])
        if frame >= self.keyframes[-1].frame:
            d = self.keyframes[-1].data
            return (d['x'], d['y'], d['z'])
            
        # Linear search (optimization: most queries are sequential)
        # TODO: Use binary search for large datasets
        for i in range(len(self.keyframes) - 1):
            k1 = self.keyframes[i]
            k2 = self.keyframes[i+1]
            if k1.frame <= frame <= k2.frame:
                if k2.frame == k1.frame:
                    t = 0
                else:
                    t = (frame - k1.frame) / (k2.frame - k1.frame)
                
                x = k1.data['x'] + (k2.data['x'] - k1.data['x']) * t
                y = k1.data['y'] + (k2.data['y'] - k1.data['y']) * t
                z = k1.data['z'] + (k2.data['z'] - k1.data['z']) * t
                return (x, y, z)
        return (0.0, 0.0, 0.0)

    def add_keyframe(self, frame: int, x: float, y: float, z: float,
                     roll: float = 0, pitch: float = 0, yaw: float = 0) -> 'TransformTrack':
        """Add a transform keyframe."""
        kf = Keyframe(frame, x=x, y=y, z=z, roll=roll, pitch=pitch, yaw=yaw)
        # Insert sorted by frame
        inserted = False
        for i, existing in enumerate(self.keyframes):
            if existing.frame == frame:
                # Replace existing keyframe at same frame
                self.keyframes[i] = kf
                inserted = True
                break
            elif existing.frame > frame:
                self.keyframes.insert(i, kf)
                inserted = True
                break
        if not inserted:
            self.keyframes.append(kf)
        return self


class AnimationTrack(Track):
    """
    Track for animation segments.
    
    Keyframe data: {start_frame, end_frame, name, speed_multiplier}
    Note: This track uses segments, not point keyframes.
    """
    def __init__(self):
        super().__init__("animation")
        self.segments: List[Dict[str, Any]] = []
    
    def add_segment(self, start_frame: int, end_frame: int, 
                    name: str, speed_multiplier: float = 1.0) -> 'AnimationTrack':
        """
        Add an animation segment.
        
        Args:
            start_frame: Start of animation
            end_frame: End of animation
            name: Animation asset name (e.g., "Jog_Fwd")
            speed_multiplier: Playback rate
        """
        segment = {
            "start_frame": start_frame,
            "end_frame": end_frame,
            "name": name,
            "speed_multiplier": speed_multiplier
        }
        self.segments.append(segment)
        return self
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Return segments list."""
        return self.segments


class CameraSettingsTrack(Track):
    """
    Track for camera-specific settings.
    
    Keyframe data: {fov, focal_length, focus_distance, look_at_actor}
    """
    def __init__(self):
        super().__init__("settings")
    
    def add_keyframe(self, frame: int, 
                     fov: float = None,
                     focal_length: float = None,
                     focus_distance: float = None,
                     look_at_actor: str = None) -> 'CameraSettingsTrack':
        """Add a camera settings keyframe."""
        data = {}
        if fov is not None:
            data["fov"] = fov
        if focal_length is not None:
            data["focal_length"] = focal_length
        if focus_distance is not None:
            data["focus_distance"] = focus_distance
        if look_at_actor is not None:
            data["look_at_actor"] = look_at_actor
        
        if data:  # Only add if there's actual data
            kf = Keyframe(frame, **data)
            # Insert sorted
            inserted = False
            for i, existing in enumerate(self.keyframes):
                if existing.frame == frame:
                    self.keyframes[i] = kf
                    inserted = True
                    break
                elif existing.frame > frame:
                    self.keyframes.insert(i, kf)
                    inserted = True
                    break
            if not inserted:
                self.keyframes.append(kf)
        return self


class AttachTrack(Track):
    """
    Track for actor attachment.
    
    1:1 mapping with Unreal's MovieScene3DAttachTrack.
    Output: attach.json
    """
    def __init__(self):
        super().__init__("attach")
        self.sections: List[Dict[str, Any]] = []
    
    def add_section(self, 
                    parent_actor: str,
                    socket_name: str = "",
                    start_frame: int = 0,
                    end_frame: int = None,
                    location_rule: str = "KEEP_RELATIVE",
                    rotation_rule: str = "KEEP_RELATIVE",
                    scale_rule: str = "KEEP_RELATIVE") -> 'AttachTrack':
        """
        Add an attachment section.
        
        Args:
            parent_actor: Name of parent actor to attach to
            socket_name: Optional socket on parent's skeletal mesh
            start_frame: Frame when attachment begins
            end_frame: Frame when attachment ends (None = until end)
            location_rule: KEEP_RELATIVE, KEEP_WORLD, or SNAP_TO_TARGET
            rotation_rule: KEEP_RELATIVE, KEEP_WORLD, or SNAP_TO_TARGET
            scale_rule: KEEP_RELATIVE, KEEP_WORLD, or SNAP_TO_TARGET
        """
        section = {
            "parent_actor": parent_actor,
            "socket_name": socket_name,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "location_rule": location_rule,
            "rotation_rule": rotation_rule,
            "scale_rule": scale_rule
        }
        self.sections.append(section)
        return self
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Return sections list."""
        return self.sections


class FocalLengthTrack(Track):
    """
    Track for camera focal length (zoom).
    
    1:1 mapping with Unreal's CineCameraComponent.CurrentFocalLength.
    Output: focal_length.json
    """
    def __init__(self):
        super().__init__("focal_length")
    
    def add_keyframe(self, frame: int, value: float) -> 'FocalLengthTrack':
        """Add focal length keyframe (in mm)."""
        kf = Keyframe(frame, value=value)
        self.keyframes.append(kf)
        return self


class FocusDistanceTrack(Track):
    """
    Track for camera focus distance (depth of field).
    
    1:1 mapping with Unreal's CineCameraComponent.FocusSettings.ManualFocusDistance.
    Output: focus_distance.json
    """
    def __init__(self):
        super().__init__("focus_distance")
    
    def add_keyframe(self, frame: int, value: float) -> 'FocusDistanceTrack':
        """Add focus distance keyframe (in cm)."""
        kf = Keyframe(frame, value=value)
        self.keyframes.append(kf)
        return self


# =============================================================================
# ACTOR TRACK SET
# =============================================================================

class ActorTrackSet:
    """
    Collection of all tracks for a single actor.
    
    Attributes:
        name: Actor name
        actor_type: "actor" or "camera"
        transform: TransformTrack instance
        animation: AnimationTrack instance (actors only)
        settings: CameraSettingsTrack instance (cameras only)
        initial_state: Starting position, rotation, etc.
    """
    def __init__(self, name: str, actor_type: str = "actor"):
        self.name = name
        self.actor_type = actor_type
        self.transform = TransformTrack()
        self.animation = AnimationTrack() if actor_type == "actor" else None
        self.settings = CameraSettingsTrack() if actor_type == "camera" else None
        self.attach = AttachTrack()
        self.mesh_yaw_offset = 0.0  # Persistent mesh correction offset
        self.initial_state = {
            "location": [0, 0, 0],
            "rotation": [0, 0, 0],  # [roll, pitch, yaw]
            "properties": {}       # radius, height, mesh_path, etc.
        }
        # Camera timelines for dynamic keyframe generation

        self.camera_timelines = {
            "look_at": [],      # [(start_time, end_time, actor, height_pct, interp_speed)]
            "frame_subject": [], # [(start_time, end_time, actor, coverage)]
            "focus_on": []       # [(start_time, end_time, actor, height_pct)]
        } if actor_type == "camera" else None
        
        # Local Time Cursor (tracks where this actor left off)
        self.current_time: float = 0.0
    
    def save(self, base_folder: str):
        """
        Save all tracks to actor subfolder.
        
        Creates: base_folder/actor_name/<track>.json
        """
        actor_folder = os.path.join(base_folder, self.name)
        os.makedirs(actor_folder, exist_ok=True)
        
        self.transform.save(actor_folder)
        if self.animation:
            self.animation.save(actor_folder)
        
        # SAVE PROPERTIES TO SETTINGS.JSON
        # Check if we have properties to save (including actor/camera/light/marker types)
        if self.initial_state.get("properties"):
            settings_data = self.initial_state["properties"].copy()
            
            # Add camera timeline data if present (CAMERA SPECIFIC)
            if self.actor_type == "camera" and self.camera_timelines:
                # Add look_at timeline if present
                if self.camera_timelines["look_at"]:
                    settings_data["look_at_timeline"] = []
                    for segment in self.camera_timelines["look_at"]:
                        start_time, end_time, actor, height_pct, interp_speed = segment
                        settings_data["look_at_timeline"].append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "actor": actor,
                            "height_pct": height_pct,
                            "interp_speed": interp_speed
                        })
                    # Also set initial values
                    if self.camera_timelines["look_at"]:
                        first_segment = self.camera_timelines["look_at"][0]
                        settings_data["look_at_actor"] = first_segment[2]  # actor
                        settings_data["look_at_height_pct"] = first_segment[3]  # height_pct
                        settings_data["look_at_interp_speed"] = first_segment[4]  # interp_speed
                
                # Add focus_on timeline if present
                if self.camera_timelines["focus_on"]:
                    settings_data["focus_on_timeline"] = []
                    for segment in self.camera_timelines["focus_on"]:
                        start_time, end_time, actor, height_pct = segment
                        settings_data["focus_on_timeline"].append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "actor": actor,
                            "height_pct": height_pct
                        })
                
                # Add frame_subject timeline
                if self.camera_timelines["frame_subject"]:
                    settings_data["frame_subject_timeline"] = []
                    for segment in self.camera_timelines["frame_subject"]:
                        start_time, end_time, actor, coverage = segment
                        settings_data["frame_subject_timeline"].append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "actor": actor,
                            "coverage": coverage
                        })
            
            # Ensure actor_type is in settings
            if "actor_type" not in settings_data:
                settings_data["actor_type"] = self.actor_type

            settings_path = os.path.join(actor_folder, "settings.json")
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)
                
        elif self.settings:
            self.settings.save(actor_folder)
            
        # Save attach track if it has sections
        if self.attach.sections:
            self.attach.save(actor_folder)


class GroupTargetActor(ActorTrackSet):
    """
    Actor that dynamically tracks the midpoint of other actors.
    """
    def __init__(self, name: str, members: List[str] = None):
        super().__init__(name, actor_type="marker")  # Use marker type, not mannequin
        self.members = members or []
        self.computation_interval_ms = 1000.0 # Default 1s
    
    def compute_track(self, movie_builder: 'MovieBuilder'):
        """Generate keyframes based on member positions."""
        if not self.members:
            return
            
        # 1. Determine time range from members
        max_frame = 0
        for member_name in self.members:
            if member_name in movie_builder.actors:
                member = movie_builder.actors[member_name]
                if member.transform.keyframes:
                    max_frame = max(max_frame, member.transform.keyframes[-1].frame)
        
        # 2. Iterate and interpolate
        fps = movie_builder.fps
        interval_sec = self.computation_interval_ms / 1000.0
        if interval_sec <= 0: interval_sec = 0.1 # Safety
        
        step_frames = interval_sec * fps
        current_frame = 0.0
        
        # Clear existing keyframes to avoid duplication if run multiple times
        self.transform.keyframes = []
        
        while current_frame <= max_frame + step_frames: # Go a bit past to ensure coverage
            # Calculate midpoint
            sum_x, sum_y, sum_z = 0.0, 0.0, 0.0
            count = 0
            
            for member_name in self.members:
                if member_name in movie_builder.actors:
                    loc = movie_builder.actors[member_name].transform.get_location_at_frame(current_frame)
                    sum_x += loc[0]
                    sum_y += loc[1]
                    sum_z += loc[2]
                    count += 1
            
            if count > 0:
                avg_x = sum_x / count
                avg_y = sum_y / count
                avg_z = sum_z / count
                
                # We assume no rotation for the target (identity)
                self.transform.add_keyframe(int(current_frame), avg_x, avg_y, avg_z)
            
            current_frame += step_frames


# =============================================================================
# BUILDER CLASSES
# =============================================================================

class LightBuilder:
    """
    Fluent API for configuring a light source.
    Auto-adds to movie when chain completes (no explicit .add() needed).
    """
    def __init__(self, movie_builder: 'MovieBuilder', name: str, light_type: LightType, location: Tuple[float, float, float]):
        self.mb = movie_builder
        self.name = name
        self.light_type = light_type
        self.location = location
        
        # Default properties
        self._rotation = (0, 0, 0)
        self._intensity = 5000.0
        self._intensity_unit = LightUnit.UNITLESS
        self._color = LightColor.WHITE
        self._attenuation_radius = 1000.0
        self._inner_cone = 0.0
        self._outer_cone = 44.0
        self._cast_shadows = True
        self._use_atmospheric_sun = False
        
        # Auto-add on creation (lights don't need explicit .add() call)
        self._finalize()

    def _finalize(self):
        """Internal: Add light to movie's actor list."""
        # Convert color to tuple if Enum
        rgb = self._color.value if isinstance(self._color, LightColor) else self._color
        
        track_set = ActorTrackSet(self.name, actor_type="light")
        track_set.initial_state = {
            "location": list(self.location),
            "rotation": list(self._rotation),
            "properties": {
                "light_type": self.light_type.value,
                "intensity": self._intensity,
                "intensity_unit": self._intensity_unit.name,
                "color": list(rgb),
                "attenuation_radius": self._attenuation_radius,
                "inner_cone_angle": self._inner_cone,
                "outer_cone_angle": self._outer_cone,
                "cast_shadows": self._cast_shadows,
                "use_as_atmospheric_sun": self._use_atmospheric_sun
            }
        }
        
        # Add attachment if specified
        if hasattr(self, '_attach_parent'):
            track_set.attach.add_section(
                parent_actor=self._attach_parent,
                socket_name=getattr(self, '_attach_socket', ""),
                start_frame=0,
                end_frame=None  # Until end of sequence
            )
        
        self.mb.actors[self.name] = track_set

    def intensity(self, value: float, unit: LightUnit = LightUnit.UNITLESS) -> 'LightBuilder':
        """Set the light's intensity."""
        self._intensity = value
        self._intensity_unit = unit
        self._finalize()  # Re-finalize with updated values
        return self

    def color(self, color: Union[LightColor, Tuple[float, float, float]]) -> 'LightBuilder':
        """Set the light's color."""
        self._color = color
        self._finalize()
        return self

    def rotation(self, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> 'LightBuilder':
        """Set the light's rotation (degrees)."""
        self._rotation = (roll, pitch, yaw)
        self._finalize()
        return self

    def attenuation_radius(self, radius: float) -> 'LightBuilder':
        """Set the light's attenuation radius (cm). Relevant for Point/Spot."""
        self._attenuation_radius = radius
        self._finalize()
        return self
    
    def cast_shadows(self, enable: bool) -> 'LightBuilder':
        """Enable or disable shadow casting for the light."""
        self._cast_shadows = enable
        self._finalize()
        return self

    def inner_cone_angle(self, angle: float) -> 'LightBuilder':
        """Set the inner cone angle (degrees). Relevant for Spot."""
        self._inner_cone = angle
        self._finalize()
        return self

    def outer_cone_angle(self, angle: float) -> 'LightBuilder':
        """Set the outer cone angle (degrees). Relevant for Spot."""
        self._outer_cone = angle
        self._finalize()
        return self
    
    def use_as_atmospheric_sun(self, enable: bool) -> 'LightBuilder':
        """Set whether this directional light acts as the atmospheric sun."""
        if self.light_type == LightType.DIRECTIONAL:
            self._use_atmospheric_sun = enable
            self._finalize()
        else:
            print(f"Warning: 'use_as_atmospheric_sun' is only applicable to Directional lights.")
        return self
    
    # Convenience methods
    def radius(self, value: float) -> 'LightBuilder':
        """Convenience alias for attenuation_radius()."""
        return self.attenuation_radius(value)
    
    def cone(self, inner: float, outer: float) -> 'LightBuilder':
        """
        Convenience method to set both cone angles at once.
        
        Args:
            inner: Inner cone angle in degrees
            outer: Outer cone angle in degrees
        """
        self._inner_cone = inner
        self._outer_cone = outer
        self._finalize()
        return self
    
    def attach_to(self, parent_actor: str, socket: str = "") -> 'LightBuilder':
        """
        Attach light to another actor.
        
        Args:
            parent_actor: Name of actor to attach to
            socket: Optional socket name on parent's skeletal mesh
        
        Returns:
            Self for chaining
        """
        self._attach_parent = parent_actor
        self._attach_socket = socket
        self._finalize()
        return self


# =============================================================================
# MOVIE BUILDER (Main API)
# =============================================================================

class MovieBuilder:
    """
    Main entry point for building track-based motion sequences.
    
    Usage:
        with MovieBuilder("MyMovie", fps=60) as movie:
            movie.add_actor("Runner1", location=(0, 0, 0))
            with movie.for_actor("Runner1") as r1:
                r1.move_straight().direction(Direction.NORTH).distance_at_speed(100, 6)
            movie.save_to_tracks("dist/")
        movie.run(to_unreal=True)
    
    Attributes:
        name: Movie name (used for output folder)
        fps: Frames per second
        actors: Dict[str, ActorTrackSet]
        current_time: Global timeline cursor
    """
    
    def __init__(self, name: str, fps: int = 60, create_new_level: bool = True):
        """
        Initialize a new movie builder.
        
        Args:
            name: Movie name (also output folder name)
            fps: Frame rate for keyframe calculations
            create_new_level: Whether to create new Unreal level
        """
        self.name = name
        self.fps = fps
        self.create_new_level = create_new_level
        self.actors: Dict[str, ActorTrackSet] = {}
        self.current_time = 0.0
        self._output_folder = None
        self._scene_commands: List[Dict[str, Any]] = [] # For floor, lights, etc.
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Finalize movie on context exit.
        
        - Resolve till_end() commands
        - Validate timeline gaps
        - Calculate final duration
        """
        # For now, just return success
        # TODO: Add till_end resolution and gap detection if needed
        return exc_type is None
    
    # -------------------------------------------------------------------------
    # Actor/Camera Creation
    # -------------------------------------------------------------------------
    
    def add_actor(self, name: str, 
                  location: Tuple[float, float, float] = (0, 0, 0),
                  yaw_offset: float = 0.0,
                  radius: float = 0.35,
                  height: float = 1.8,
                  mesh_path: str = None) -> 'MovieBuilder':
        """
        Add an actor to the movie.
        
        Args:
            name: Unique actor identifier
            location: Starting (x, y, z) in centimeters
            yaw_offset: Initial facing direction in degrees
            radius: Collision radius in meters
            height: Actor height in meters
            mesh_path: Optional skeletal mesh asset path
        
        Returns:
            Self for chaining
        """
        track_set = ActorTrackSet(name, actor_type="actor")
        track_set.mesh_yaw_offset = yaw_offset
        track_set.initial_state = {
            "location": list(location),
            "rotation": [0, 0, yaw_offset],  # [roll, pitch, yaw]
            "properties": {
                "radius": radius,
                "height": height,
                "mesh_path": mesh_path
            }
        }
        self.actors[name] = track_set
        return self
    
    def add_camera(self, name: str,
                   location: Tuple[float, float, float],
                   fov: float = 90.0) -> 'CameraBuilder':
        """
        Add a camera and return a builder for configuration.
        
        Args:
            name: Unique camera identifier
            location: Starting (x, y, z) in centimeters
            fov: Field of view in degrees
        
        Returns:
            CameraBuilder for fluent configuration
        """
        return CameraBuilder(self, name, location, fov)
    
    def add_audio(self, asset_path: str, start_time: float = 0.0,
                  duration: float = None, volume: float = 1.0) -> 'MovieBuilder':
        """
        Add an audio track to the sequence.
        
        Args:
            asset_path: Unreal asset path (e.g., "/Game/Audio/MySound.MySound")
            start_time: Start time in seconds
            duration: Duration in seconds (None = full length)
            volume: Volume multiplier (1.0 = 100%)
        
        Returns:
            Self for chaining
        """
        if not hasattr(self, '_audio_tracks'):
            self._audio_tracks = []
        
        self._audio_tracks.append({
            "asset_path": asset_path,
            "start_time": start_time,
            "duration": duration,
            "volume": volume
        })
        return self
    
    def add_floor(self, actor_name: str,
                  location: Tuple[float, float, float] = (0, 0, -0.5),
                  scale: float = 1000.0) -> 'MovieBuilder':
        """
        Add a floor plane.
        
        Args:
            actor_name: Unique floor name
            location: Floor position (x, y, z)
            scale: Floor size scaling
        
        Returns:
            Self for chaining
        """
        if not hasattr(self, '_scene_commands'):
            self._scene_commands = []
        
        self._scene_commands.append({
            "command": "add_floor",
            "actor": actor_name,
            "location": list(location),
            "scale": scale
        })
        return self
    
    
    def add_group_target(self, name: str, members: List[str] = None, 
                        location: Tuple[float, float, float] = (0, 0, 0)) -> 'GroupTargetBuilder':
        """
        Add a Group Target actor that tracks multiple members.
        
        Args:
            name: Unique identifier
            members: List of actor names to track
            location: Initial location (before calculation)
            
        Returns:
            GroupTargetBuilder for fluent configuration
        """
        builder = GroupTargetBuilder(self, name, members)
        # Set initial location
        builder.actor.initial_state["location"] = list(location)
        builder.actor.transform.add_keyframe(0, location[0], location[1], location[2])
        return builder

    # --- Light Methods (Enum-based) ---
    
    def add_light_point(self, name: str, location: Tuple[float, float, float]) -> 'LightBuilder':
        """
        Add a Point Light (bulb, fire, etc.).
        
        Args:
            name: Unique light identifier
            location: Position (x, y, z) in centimeters
        
        Returns:
            LightBuilder for fluent configuration
        """
        return LightBuilder(self, name, LightType.POINT, location)
        
    def add_light_directional(self, name: str) -> 'LightBuilder':
        """
        Add a Directional Light (sun, moon).
        Location is ignored for directional lights.
        
        Args:
            name: Unique light identifier
        
        Returns:
            LightBuilder for fluent configuration
        """
        return LightBuilder(self, name, LightType.DIRECTIONAL, (0, 0, 0))
        
    def add_light_spot(self, name: str, location: Tuple[float, float, float]) -> 'LightBuilder':
        """
        Add a Spot Light (flashlight, stage light).
        
        Args:
            name: Unique light identifier
            location: Position (x, y, z) in centimeters
        
        Returns:
            LightBuilder for fluent configuration
        """
        return LightBuilder(self, name, LightType.SPOT, location)
        
    def add_light_rect(self, name: str, location: Tuple[float, float, float]) -> 'LightBuilder':
        """
        Add a Rect Light (TV screen, softbox, window).
        
        Args:
            name: Unique light identifier
            location: Position (x, y, z) in centimeters
        
        Returns:
            LightBuilder for fluent configuration
        """
        return LightBuilder(self, name, LightType.RECT, location)
        
    def add_light_sky(self, name: str) -> 'LightBuilder':
        """
        Add a Sky Light (ambient environment lighting).
        Location is ignored for sky lights.
        
        Args:
            name: Unique light identifier
        
        Returns:
            LightBuilder for fluent configuration
        """
        return LightBuilder(self, name, LightType.SKY, (0, 0, 0))
    
    def for_camera(self, camera_name: str) -> 'CameraCommandBuilder':
        """
        Get a command builder for an existing camera.
        
        Usage:
            with movie.for_camera("Camera1") as cam:
                cam.look_at("Runner1")
                cam.wait(5.0)
        
        Args:
            camera_name: Name of previously added camera
        
        Returns:
            CameraCommandBuilder context manager
        """
        if camera_name not in self.actors:
            raise ValueError(f"Camera '{camera_name}' not found. Add it first with add_camera()")
        return CameraCommandBuilder(self, camera_name)
    
    # -------------------------------------------------------------------------
    # Context Managers
    # -------------------------------------------------------------------------
    
    def for_actor(self, actor_name: str) -> 'ActorBuilder':
        """
        Get a builder context for an actor.
        Uses Actor's Local Time (resumes where they left off).
        
        Usage:
            with movie.for_actor("Runner1") as r1:
                r1.move_straight()...
        """
        if actor_name not in self.actors:
            raise ValueError(f"Actor '{actor_name}' not found. Call add_actor() first.")
        
        track_set = self.actors[actor_name]
        start_time = track_set.current_time
        
        return ActorBuilder(self, actor_name, start_time=start_time)
    
    def for_camera(self, camera_name: str) -> 'CameraCommandBuilder':
        """
        Get a builder context for a camera.
        Uses Camera's Local Time.
        """
        if camera_name not in self.actors:
            raise ValueError(f"Camera '{camera_name}' not found. Call add_camera() first.")
        
        track_set = self.actors[camera_name]
        start_time = track_set.current_time
        
        return CameraCommandBuilder(self, camera_name, start_time=start_time)
    
    def simultaneous(self) -> 'SimultaneousContext':
        """
        Create a context where multiple actors can be scripted in parallel.
        
        Usage:
            with movie.simultaneous():
                with movie.for_actor("Runner1") as r1: ...
                with movie.for_actor("Runner2") as r2: ...
        
        Returns:
            SimultaneousContext manager
        """
        return SimultaneousContext(self)
    
    def at_time(self, time_sec: float) -> 'TimelineBuilder':
        """
        Set global timeline cursor and return builder for time-based commands.
        
        Args:
            time_sec: Time in seconds
        
        Returns:
            TimelineBuilder for camera cuts, etc.
        """
        self.current_time = time_sec
        return TimelineBuilder(self, time_sec)
    
    # -------------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------------
    
    def save_to_tracks(self, output_folder: str = "dist/") -> 'MovieBuilder':
        """
        Save all tracks to folder structure.
        
        Creates:
            output_folder/movie_name/
            ├── meta.json
            ├── Actor1/
            │   ├── transform.json
            │   └── animation.json
            └── Camera1/
                ├── transform.json
                ├── settings.json
                ├── focal_length.json (if frame_subject used)
                └── focus_distance.json (if focus_on used)
        
        Args:
            output_folder: Base output directory
        
        Returns:
            Self for chaining
        """
        # 0. Pre-computation Pass (Group Targets)
        # Must run before saving so the tracks are populated
        for actor in list(self.actors.values()):
            if hasattr(actor, "compute_track"):
                actor.compute_track(self)
        
        # 1. Validation Pass - Check camera look-at ordering
        actor_names = list(self.actors.keys())
        for idx, actor_name in enumerate(actor_names):
            track_set = self.actors[actor_name]
            if track_set.actor_type == "camera" and track_set.camera_timelines:
                # Check look_at timeline
                if track_set.camera_timelines["look_at"]:
                    for segment in track_set.camera_timelines["look_at"]:
                        target_name = segment[2]  # actor name is 3rd element
                        if target_name not in self.actors:
                            raise ValueError(
                                f"Camera '{actor_name}' is configured to look_at '{target_name}', "
                                f"but '{target_name}' was never added to the movie."
                            )
                        target_idx = actor_names.index(target_name)
                        if target_idx > idx:
                            print(f"[WARN] WARNING: Camera '{actor_name}' (position {idx}) is configured to look_at '{target_name}' (position {target_idx}). "
                                  f"The camera is added BEFORE its target, which may cause initial rotation issues. "
                                  f"Consider adding '{target_name}' before '{actor_name}' in your script.")
                
                # Check focus_on timeline
                if track_set.camera_timelines["focus_on"]:
                    for segment in track_set.camera_timelines["focus_on"]:
                        target_name = segment[2]  # actor name is 3rd element
                        if target_name not in self.actors:
                            raise ValueError(
                                f"Camera '{actor_name}' is configured to focus_on '{target_name}', "
                                f"but '{target_name}' was never added to the movie."
                            )
                
                # Check frame_subject timeline
                if track_set.camera_timelines["frame_subject"]:
                    for segment in track_set.camera_timelines["frame_subject"]:
                        target_name = segment[2]  # actor name is 3rd element
                        if target_name not in self.actors:
                            raise ValueError(
                                f"Camera '{actor_name}' is configured to frame_subject '{target_name}', "
                                f"but '{target_name}' was never added to the movie."
                            )
        
        # 2. Validation Pass - Check for rotation keyframes when auto-tracking is enabled
        for actor_name, track_set in self.actors.items():
            if track_set.actor_type == "camera" and track_set.camera_timelines:
                # Check if any auto-tracking is enabled
                has_look_at = bool(track_set.camera_timelines["look_at"])
                has_focus = bool(track_set.camera_timelines["focus_on"])
                has_frame_subject = bool(track_set.camera_timelines["frame_subject"])
                
                if has_look_at or has_focus or has_frame_subject:
                    # Check if there are rotation keyframes
                    if len(track_set.transform.keyframes) > 0:
                        # Check if any keyframe has non-zero rotation
                        for kf in track_set.transform.keyframes:
                            has_rotation = (kf.data.get('roll', 0) != 0 or 
                                          kf.data.get('pitch', 0) != 0 or 
                                          kf.data.get('yaw', 0) != 0)
                            if has_rotation:
                                raise ValueError(
                                    f"❌ CONFLICT DETECTED: Camera '{actor_name}' has auto-tracking enabled "
                                    f"(look_at/focus_on/frame_subject) but also has rotation keyframes. "
                                    f"Auto-tracking controls rotation automatically. "
                                    f"Remove rotation keyframes or disable auto-tracking."
                                )
                    
                    # CRITICAL FIX: Remove rotation from all keyframes for cameras with auto-tracking
                    for kf in track_set.transform.keyframes:
                        kf.data['roll'] = 0
                        kf.data['pitch'] = 0
                        kf.data['yaw'] = 0
                    
                    print(f"[OK] Camera '{actor_name}': Auto-tracking enabled, rotation keyframes cleared")



        movie_folder = os.path.join(output_folder, self.name)
        os.makedirs(movie_folder, exist_ok=True)
        
        # Save meta.json
        meta = {
            "name": self.name,
            "fps": self.fps,
            "create_new_level": self.create_new_level,
            "duration": self.current_time,
            "actors": list(self.actors.keys())
        }
        meta_path = os.path.join(movie_folder, "meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)
        
        # Save each actor's tracks
        for actor_name, track_set in self.actors.items():
            track_set.save(movie_folder)
        
        # Generate camera keyframes from timelines (AFTER actor tracks are saved)
        import motion_planner
        for camera_name, track_set in self.actors.items():
            if track_set.actor_type == "camera" and track_set.camera_timelines:
                # Check if any timelines have data
                has_look_at = bool(track_set.camera_timelines["look_at"])
                has_frame_subject = bool(track_set.camera_timelines["frame_subject"])
                has_focus = bool(track_set.camera_timelines["focus_on"])
                
                if has_look_at or has_frame_subject or has_focus:
                    # Generate keyframes (focal length and focus only - look_at handled in Unreal)
                    keyframes = motion_planner.generate_camera_keyframes(
                        movie_folder,
                        camera_name,
                        track_set.camera_timelines["look_at"],
                        track_set.camera_timelines["frame_subject"],
                        track_set.camera_timelines["focus_on"],
                        self.fps,
                        camera_location=tuple(track_set.initial_state["location"])
                    )
                    
                    # Save Initial Rotation/Location keyframe (transform.json)
                    # This only contains 1 keyframe to set initial state correctly
                    # (Rest is handled by Unreal's LookAt tracking)
                    if keyframes["rotation"]:
                        camera_folder = os.path.join(movie_folder, camera_name)
                        transform_path = os.path.join(camera_folder, "transform.json")
                        with open(transform_path, 'w', encoding='utf-8') as f:
                            json.dump(keyframes["rotation"], f, indent=2)
                    
                    # NOTE: focus_distance keyframes NOT saved - Tracking Focus handled in run_scene.py
                    # using Unreal's built-in FocusSettings.TrackingFocusSettings.ActorToTrack
                    
                    # Save focal length keyframes
                    if keyframes["focal_length"]:
                        camera_folder = os.path.join(movie_folder, camera_name)
                        focal_path = os.path.join(camera_folder, "focal_length.json")
                        with open(focal_path, 'w', encoding='utf-8') as f:
                            json.dump(keyframes["focal_length"], f, indent=2)
        
        # Save camera cuts if any
        if hasattr(self, '_camera_cuts') and self._camera_cuts:
            cuts_path = os.path.join(movie_folder, "camera_cuts.json")
            with open(cuts_path, 'w', encoding='utf-8') as f:
                json.dump(self._camera_cuts, f, indent=2)
        
        # Save audio tracks if any
        if hasattr(self, '_audio_tracks') and self._audio_tracks:
            audio_path = os.path.join(movie_folder, "audio.json")
            with open(audio_path, 'w', encoding='utf-8') as f:
                json.dump(self._audio_tracks, f, indent=2)
        
        # Save scene commands if any (floors, lights, etc.)
        if hasattr(self, '_scene_commands') and self._scene_commands:
            scene_path = os.path.join(movie_folder, "scene.json")
            with open(scene_path, 'w', encoding='utf-8') as f:
                json.dump(self._scene_commands, f, indent=2)
        
        self._output_folder = movie_folder
        print(f"Movie tracks saved to: {movie_folder}")
        return self
    
    def run(self, to_unreal: bool = False) -> 'MovieBuilder':
        """
        Execute the movie.
        
        Args:
            to_unreal: If True, trigger via Remote Control API
        
        Returns:
            Self for chaining
        """
        if to_unreal:
            from trigger_movie import trigger_movie
            if self._output_folder:
                trigger_movie(self._output_folder)
            else:
                print("Warning: No movie folder saved yet. Call save_to_tracks() first.")
        return self


# =============================================================================
# COMMAND BUILDERS
# =============================================================================

class ActorBuilder:
    """
    Fluent builder for actor commands within a movie context.
    
    Provides methods like move_straight(), stay(), face() that
    generate keyframes on the actor's tracks.
    """
    
    def __init__(self, movie_builder: MovieBuilder, actor_name: str, start_time: float = 0.0):
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


class CameraBuilder:
    """
    Builder for initial camera setup.
    
    Usage:
        movie.add_camera("Cam1", location=(0, 0, 500))
            .orient(face_yaw=Direction.NORTH, tilt_pitch=Tilt.DOWN, tilt_pitch_offset=45)
            .look_at("Runner1")
            .add()
    """
    
    def __init__(self, movie_builder: MovieBuilder, name: str, 
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
    
    def add(self) -> MovieBuilder:
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
    
    def __init__(self, movie_builder: MovieBuilder, camera_name: str, start_time: float = 0.0):
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
        self.auto_focus_subject(actor_name, height_pct=focus_pct)
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


class SimultaneousContext:
    """
    Context manager for parallel actor scripting.
    
    All actors scripted within this context start at the same time.
    The context exits when the longest actor timeline completes.
    """
    
    def __init__(self, movie_builder: MovieBuilder):
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


class TimelineBuilder:
    """
    Builder for time-based global commands (camera cuts, markers).
    """
    
    def __init__(self, movie_builder: MovieBuilder, time_sec: float):
        self.mb = movie_builder
        self.time_sec = time_sec
    
    def camera_cut(self, camera_name: str) -> 'TimelineBuilder':
        """Insert a camera cut at this time."""
        # Store camera cut metadata
        if not hasattr(self.mb, '_camera_cuts'):
            self.mb._camera_cuts = []
        self.mb._camera_cuts.append({
            "time": self.time_sec,
            "camera": camera_name
        })
        return self


class GroupTargetBuilder:
    """
    Builder for GroupTargetActor configuration.
    """
    def __init__(self, movie_builder: MovieBuilder, name: str, members: List[str]):
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
