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

from typing import List, Dict, Any, Optional, Union, Tuple
from enum import Enum
import math
import os
import json
import motion_math


# =============================================================================
# ENUMS
# =============================================================================

class Direction(Enum):
    """Cardinal and diagonal directions for movement and facing."""
    FORWARD = "Forward"
    BACKWARD = "Backward"
    LEFT = "Left"
    RIGHT = "Right"
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
        self.initial_state = {
            "location": [0, 0, 0],
            "rotation": [0, 0, 0],  # [roll, pitch, yaw]
            "properties": {}       # radius, height, mesh_path, etc.
        }
    
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
        if self.settings:
            self.settings.save(actor_folder)


# =============================================================================
# BUILDER CLASSES
# =============================================================================

class LightBuilder:
    """
    Fluent API for configuring a light source.
    """
    def __init__(self, movie_builder: 'MovieBuilder', name: str, light_type: LightType, location: Tuple[float, float, float]):
        self._movie_builder = movie_builder
        self._light_data = {
            "command": "add_light",
            "actor": name,
            "type": light_type.value,
            "location": list(location),
            "intensity": 5000.0, # Default intensity
            "color": LightColor.WHITE.value,
            "rotation": [0, 0, 0], # Default rotation [roll, pitch, yaw]
            "attenuation_radius": 1000.0, # Default for point/spot
            "source_radius": 0.0, # Default for rect/spot
            "source_length": 0.0, # Default for rect/spot
            "barn_door_angle": 90.0, # Default for rect
            "barn_door_length": 50.0, # Default for rect
            "inner_cone_angle": 0.0, # Default for spot
            "outer_cone_angle": 44.0, # Default for spot
            "cast_shadows": True,
            "use_as_atmospheric_sun": False # Only for directional
        }
        if not hasattr(self._movie_builder, '_scene_commands'):
            self._movie_builder._scene_commands = []
        self._movie_builder._scene_commands.append(self._light_data)

    def intensity(self, value: float, unit: LightUnit = LightUnit.LUMENS) -> 'LightBuilder':
        """Set the light's intensity."""
        self._light_data["intensity"] = value
        self._light_data["intensity_unit"] = unit.name # Store unit name for backend
        return self

    def color(self, color: Union[LightColor, Tuple[float, float, float]]) -> 'LightBuilder':
        """Set the light's color."""
        if isinstance(color, LightColor):
            self._light_data["color"] = color.value
        else:
            self._light_data["color"] = list(color)
        return self

    def rotation(self, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> 'LightBuilder':
        """Set the light's rotation (degrees)."""
        self._light_data["rotation"] = [roll, pitch, yaw]
        return self

    def attenuation_radius(self, radius: float) -> 'LightBuilder':
        """Set the light's attenuation radius (cm). Relevant for Point/Spot."""
        self._light_data["attenuation_radius"] = radius
        return self
    
    def cast_shadows(self, enable: bool) -> 'LightBuilder':
        """Enable or disable shadow casting for the light."""
        self._light_data["cast_shadows"] = enable
        return self

    # Specific properties for different light types
    def source_radius(self, radius: float) -> 'LightBuilder':
        """Set the source radius (cm). Relevant for Rect/Spot."""
        self._light_data["source_radius"] = radius
        return self

    def source_length(self, length: float) -> 'LightBuilder':
        """Set the source length (cm). Relevant for Rect."""
        self._light_data["source_length"] = length
        return self
    
    def barn_door_angle(self, angle: float) -> 'LightBuilder':
        """Set the barn door angle (degrees). Relevant for Rect."""
        self._light_data["barn_door_angle"] = angle
        return self
    
    def barn_door_length(self, length: float) -> 'LightBuilder':
        """Set the barn door length (cm). Relevant for Rect."""
        self._light_data["barn_door_length"] = length
        return self_

    def inner_cone_angle(self, angle: float) -> 'LightBuilder':
        """Set the inner cone angle (degrees). Relevant for Spot."""
        self._light_data["inner_cone_angle"] = angle
        return self

    def outer_cone_angle(self, angle: float) -> 'LightBuilder':
        """Set the outer cone angle (degrees). Relevant for Spot."""
        self._light_data["outer_cone_angle"] = angle
        return self
    
    def use_as_atmospheric_sun(self, enable: bool) -> 'LightBuilder':
        """Set whether this directional light acts as the atmospheric sun."""
        if self._light_data["type"] == LightType.DIRECTIONAL.value:
            self._light_data["use_as_atmospheric_sun"] = enable
        else:
            print(f"Warning: 'use_as_atmospheric_sun' is only applicable to Directional lights. Ignoring for {self._light_data['type']} light.")
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
        track_set.initial_state = {
            "location": list(location),
            "rotation": [0, yaw_offset, 0],  # [roll, pitch, yaw]
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
    
    def add_directional_light(self, actor_name: str,
                              direction_from: str = "west",
                              angle: str = "low",
                              intensity: str = "bright",
                              color: str = "golden",
                              atmosphere_sun: bool = True) -> 'MovieBuilder':
        """
        Add a directional light (sun).
        
        Args:
            actor_name: Unique light name
            direction_from: "north", "south", "east", "west"
            angle: "low", "medium", "high"
            intensity: "dim", "normal", "bright"
            color: "white", "golden", "blue"
            atmosphere_sun: Whether to use as atmospheric sun
        
        Returns:
            Self for chaining
        """
        if not hasattr(self, '_scene_commands'):
            self._scene_commands = []
        
        self._scene_commands.append({
            "command": "add_directional_light",
            "actor": actor_name,
            "direction_from": direction_from,
            "angle": angle,
            "intensity": intensity,
            "color": color,
            "atmosphere_sun": atmosphere_sun
        })
        return self
    
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
        
        Usage:
            with movie.for_actor("Runner1") as r1:
                r1.move_straight()...
        
        Args:
            actor_name: Name of previously added actor
        
        Returns:
            ActorBuilder context manager
        """
        if actor_name not in self.actors:
            raise ValueError(f"Actor '{actor_name}' not found. Call add_actor() first.")
        return ActorBuilder(self, actor_name)
    
    def for_camera(self, camera_name: str) -> 'CameraCommandBuilder':
        """
        Get a builder context for a camera.
        
        Args:
            camera_name: Name of previously added camera
        
        Returns:
            CameraCommandBuilder context manager
        """
        if camera_name not in self.actors:
            raise ValueError(f"Camera '{camera_name}' not found. Call add_camera() first.")
        return CameraCommandBuilder(self, camera_name)
    
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
                └── settings.json
        
        Args:
            output_folder: Base output directory
        
        Returns:
            Self for chaining
        """
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
    
    def __init__(self, movie_builder: MovieBuilder, actor_name: str):
        self.mb = movie_builder
        self.actor_name = actor_name
        self.track_set = movie_builder.actors.get(actor_name)
        self._current_time = 0.0  # Local timeline cursor
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Update global time to this actor's end time."""
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
        target_yaw = motion_math.get_cardinal_angle(direction.value)
        if target_yaw is None:
            raise ValueError(f"Invalid direction: {direction}")
        
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
        self._direction = Direction.FORWARD
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
        """Terminal: Move distance in time (calculates speed)."""
        # Handle unit tuples
        m_val = meters
        if isinstance(meters, tuple):
            m_val = meters[1] * meters[0].value
        
        s_val = seconds
        if isinstance(seconds, tuple):
            s_val = seconds[1] * seconds[0].value
        
        # Generate keyframes
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
        # For now, just use a large duration
        # TODO: Implement proper till_end resolution
        duration = 100.0 # Default fallback
        if self.ab.mb.duration > 0:
            duration = max(0, self.ab.mb.duration - self.start_time)
            
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
    
    def look_at(self, actor_name: str, height_pct: float = 0.7) -> 'CameraBuilder':
        """Enable look-at tracking for an actor."""
        self._look_at_actor = actor_name
        self._look_at_height_pct = height_pct
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
                "look_at_height_pct": getattr(self, '_look_at_height_pct', 0.7)
            }
        }
        self.mb.actors[self.name] = track_set
        return self.mb


class CameraCommandBuilder:
    """
    Builder for camera commands during movie (zoom, pan, focus changes).
    """
    
    def __init__(self, movie_builder: MovieBuilder, camera_name: str):
        self.mb = movie_builder
        self.camera_name = camera_name
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def look_at(self, actor_name: str, height_pct: float = 0.7) -> 'CameraCommandBuilder':
        """Switch look-at target."""
        # TODO: Implement keyframe for look-at change
        return self
    
    def wait(self, duration: float) -> 'CameraCommandBuilder':
        """Hold current settings for duration."""
        # TODO: Implement
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
