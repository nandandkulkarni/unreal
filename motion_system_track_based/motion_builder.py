"""
Track-Based Motion Builder

This module provides a fluent API for defining motion sequences that are
stored in a track-based file structure (one JSON file per actor per property).

Now supports Splines for curved path definition.

Architecture:
    MovieBuilder
    ├── ActorTrackSet (per actor)
    ├── SplineActor (per path) [NEW]
    └── ...

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
import os
import json

import motion_includes.assets  # Kept for compatibility if needed, though used in structs
import motion_math

# Re-export enums and constants
from motion_structs.enums import Direction, Tilt, DistanceUnit, LightType, LightColor, LightUnit, TimeUnit, SpeedUnit
from motion_structs.constants import CHARACTER_HEIGHT, MARKER_HEIGHT

# Import Data Structures
from motion_structs.actor_data import ActorTrackSet, SplineActor, GroupTargetActor
from motion_structs.tracks import Keyframe, Track, TransformTrack, AnimationTrack, CameraSettingsTrack, AttachTrack

# Import Command Builders
from motion_cmds.lights import LightBuilder
from motion_cmds.splines import SplineBuilder, SplineMotionCommandBuilder
from motion_cmds.cameras import CameraBuilder, CameraCommandBuilder
from motion_cmds.actions import ActorBuilder, MotionCommandBuilder, StayCommandBuilder
from motion_cmds.timeline import TimelineBuilder
from motion_cmds.groups import GroupTargetBuilder, SimultaneousContext


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
    
    def __init__(self, name: str, fps: int = 60, create_new_level: bool = True, character: str = "belica"):
        """
        Initialize a new movie builder.
        
        Args:
            name: Movie name (also output folder name)
            fps: Frame rate for keyframe calculations
            create_new_level: Whether to create new Unreal level
            character: Character type for motion matching ("belica" or "manny")
        """
        self.name = name
        self.fps = fps
        self.create_new_level = create_new_level
        self.character = character.lower()  # Store character for motion matching
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
    
    # --- Spline Methods ---
    
    def add_spline(self, name: str, points: List[Tuple[float, float, float]], closed: bool = False) -> 'SplineBuilder':
        """
        Add a Spline Path.
        
        Args:
            name: Unique spline name
            points: List of (x, y, z) 3D points
            closed: Whether the path loops
            
        Returns:
            SplineBuilder for configuration
        """
        return SplineBuilder(self, name, points, closed)

    # --- Atmosphere Methods ---
    
    def add_atmosphere(self, fog_density="medium", fog_height_falloff=0.2, fog_color="atmospheric",
                      volumetric=True, volumetric_scattering=1.0, volumetric_albedo=(0.9, 0.9, 0.9),
                      start_distance=0, fog_max_opacity=1.0) -> 'MovieBuilder':
        """
        Add exponential height fog with atmospheric effects.
        
        Args:
            fog_density: Density preset ("clear", "light", "medium", "heavy", "dense") or numeric value
            fog_height_falloff: Height falloff coefficient (default: 0.2)
            fog_color: Color preset or RGB tuple (default: "atmospheric")
            volumetric: Enable volumetric fog (default: True)
            volumetric_scattering: Scattering intensity 0-2 (default: 1.0)
            volumetric_albedo: RGB tuple for fog particle color 0-1 (default: (0.9, 0.9, 0.9))
            start_distance: Distance where fog starts in cm (default: 0)
            fog_max_opacity: Maximum fog opacity 0-1 (default: 1.0)
        
        Returns:
            Self for chaining
        """
        self._scene_commands.append({
            "command": "add_atmosphere",
            "fog_density": fog_density,
            "fog_height_falloff": fog_height_falloff,
            "fog_color": fog_color,
            "volumetric": volumetric,
            "volumetric_scattering": volumetric_scattering,
            "volumetric_albedo": volumetric_albedo,
            "start_distance": start_distance,
            "fog_max_opacity": fog_max_opacity
        })
        return self
    
    def animate_fog(self, target_density=None, target_color=None, duration=5.0) -> 'MovieBuilder':
        """
        Animate fog density and/or color over time.
        
        Args:
            target_density: Target density preset or numeric value
            target_color: Target color preset or RGB tuple
            duration: Animation duration in seconds
        
        Returns:
            Self for chaining
        """
        cmd = {
            "command": "animate_fog",
            "actor": "_AtmosphereFog",
            "duration": duration
        }
        if target_density is not None:
            cmd["target_density"] = target_density
        if target_color is not None:
            cmd["target_color"] = target_color
        self._scene_commands.append(cmd)
        return self
    
    def configure_light_shafts(self, light_actor, enable_light_shafts=True, bloom_scale="cinematic",
                               bloom_threshold=8.0, occlusion_mask_darkness=0.5, cast_volumetric_shadow=True) -> 'MovieBuilder':
        """
        Configure light shafts (god rays) on a directional light.
        
        Args:
            light_actor: Name of the directional light actor
            enable_light_shafts: Enable light shaft bloom (default: True)
            bloom_scale: Bloom intensity preset ("subtle", "cinematic", "dramatic") or numeric value
            bloom_threshold: Brightness threshold for bloom (default: 8.0)
            occlusion_mask_darkness: Shadow darkness 0-1 (default: 0.5)
            cast_volumetric_shadow: Cast shadows in volumetric fog (default: True)
        
        Returns:
            Self for chaining
        """
        self._scene_commands.append({
            "command": "configure_light_shafts",
            "actor": light_actor,
            "enable_light_shafts": enable_light_shafts,
            "bloom_scale": bloom_scale,
            "bloom_threshold": bloom_threshold,
            "occlusion_mask_darkness": occlusion_mask_darkness,
            "cast_volumetric_shadow": cast_volumetric_shadow
        })
        return self
    
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
        
        # Note: ActorBuilder is imported from motion_cmds.actions
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
                        if target_name in actor_names:
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
            "character": self.character,  # For motion matching
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
