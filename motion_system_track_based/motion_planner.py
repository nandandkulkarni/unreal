"""
Track-Based Motion Planner

This module processes track-based motion data and generates Unreal Sequencer content.
It reads from a movie folder with per-actor track files.

Input Structure:
    dist/movie_name/
    ├── meta.json           # {name, fps, duration, actors: [...]}
    ├── ActorName/
    │   ├── transform.json  # [{frame, x, y, z, roll, pitch, yaw}, ...]
    │   └── animation.json  # [{start_frame, end_frame, name, speed}, ...]
    └── CameraName/
        ├── transform.json
        └── settings.json

Processing Flow:
    1. Load meta.json
    2. For each actor, load and process tracks
    3. Generate Unreal Sequencer keyframes
    4. Apply to sequence via keyframe_applier
"""

import os
import json
import math
from typing import Dict, List, Any, Optional

# Unreal imports (only available inside Unreal Python)
try:
    import unreal
    IN_UNREAL = True
except ImportError:
    IN_UNREAL = False
    unreal = None

# Local imports
import motion_math


# =============================================================================
# LOGGING
# =============================================================================

def log(message: str):
    """Log message to both console and Unreal log if available."""
    print(message)
    if IN_UNREAL:
        unreal.log(message)


# =============================================================================
# TRACK LOADERS
# =============================================================================

def load_movie(folder_path: str) -> Dict[str, Any]:
    """
    Load a complete movie from folder structure.
    
    Args:
        folder_path: Path to movie folder (e.g., dist/runners_overhead/)
    
    Returns:
        Dict with keys:
            - meta: Movie metadata
            - actors: Dict[actor_name, Dict[track_name, track_data]]
    
    Example:
        {
            "meta": {"name": "MyMovie", "fps": 60, "duration": 10.0, ...},
            "actors": {
                "Runner1": {
                    "transform": [...keyframes...],
                    "animation": [...segments...]
                },
                "Camera1": {
                    "transform": [...],
                    "settings": [...]
                }
            }
        }
    """
    # Load meta.json
    meta_path = os.path.join(folder_path, "meta.json")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"meta.json not found in {folder_path}")
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    # Load tracks for each actor
    actors = {}
    for actor_name in meta.get("actors", []):
        actor_folder = os.path.join(folder_path, actor_name)
        if not os.path.exists(actor_folder):
            continue
        
        # Load all tracks for this actor
        tracks = {}
        for track_file in os.listdir(actor_folder):
            if track_file.endswith('.json'):
                track_name = track_file[:-5]  # Remove .json
                tracks[track_name] = load_track(folder_path, actor_name, track_name)
        
        actors[actor_name] = tracks
    
    return {
        "meta": meta,
        "actors": actors
    }


def load_track(folder_path: str, actor_name: str, track_name: str) -> List[Dict[str, Any]]:
    """
    Load a single track file.
    
    Args:
        folder_path: Path to movie folder
        actor_name: Actor name (subfolder name)
        track_name: Track name without extension (e.g., "transform")
    
    Returns:
        List of keyframe/segment dictionaries
    """
    track_path = os.path.join(folder_path, actor_name, f"{track_name}.json")
    if not os.path.exists(track_path):
        return []
    
    with open(track_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# MATH UTILITIES
# =============================================================================

def orient_to_rotation(face_yaw: str, face_yaw_offset: float,
                       tilt_pitch: str, tilt_pitch_offset: float) -> Dict[str, float]:
    """
    Convert human-readable orientation to Unreal rotation.
    
    Args:
        face_yaw: Cardinal direction string (e.g., "North", "South_East")
        face_yaw_offset: Additional yaw rotation in degrees
        tilt_pitch: Vertical preset ("Up", "Down", "Level")
        tilt_pitch_offset: Additional pitch in degrees
    
    Returns:
        Dict with roll, pitch, yaw in degrees
    
    Examples:
        orient_to_rotation("North", 0, "Level", 0)  -> {roll: 0, pitch: 0, yaw: 0}
        orient_to_rotation("North", 0, "Down", 90) -> {roll: 0, pitch: 90, yaw: 0}
        orient_to_rotation("East", 0, "Level", 0)   -> {roll: 0, pitch: 0, yaw: 90}
    """
    # TODO: Implement using motion_math.get_cardinal_angle()
    raise NotImplementedError()


# =============================================================================
# TRACK PROCESSORS
# =============================================================================

def process_transform_track(track_data: List[Dict], 
                            actor_state: Dict,
                            fps: int) -> Dict[str, List]:
    """
    Process transform track into Unreal keyframes.
    
    Args:
        track_data: List of transform keyframes from JSON
        actor_state: Mutable state dict for this actor
        fps: Frames per second
    
    Returns:
        Dict with "location" and "rotation" keyframe lists ready for applier
    """
    location_keys = []
    rotation_keys = []
    
    for kf in track_data:
        frame = kf.get("frame", 0)
        location_keys.append({
            "frame": frame,
            "x": kf.get("x", 0),
            "y": kf.get("y", 0),
            "z": kf.get("z", 0)
        })
        rotation_keys.append({
            "frame": frame,
            "roll": kf.get("roll", 0),
            "pitch": kf.get("pitch", 0),
            "yaw": kf.get("yaw", 0)
        })
    
    return {
        "location": location_keys,
        "rotation": rotation_keys
    }


def process_animation_track(track_data: List[Dict],
                             actor_state: Dict,
                             fps: int) -> List[Dict]:
    """
    Process animation track into Unreal animation sections.
    
    Args:
        track_data: List of animation segments from JSON
        actor_state: Mutable state dict for this actor
        fps: Frames per second
    
    Returns:
        List of animation segment dicts ready for applier
    """
    # Animation track data is already in the correct format
    # Just return it as-is for the applier
    return track_data


def process_camera_settings_track(track_data: List[Dict],
                                   camera_state: Dict,
                                   fps: int) -> Dict[str, List]:
    """
    Process camera settings track into Unreal keyframes.
    
    Args:
        track_data: List of camera settings keyframes
        camera_state: Mutable state dict for this camera
        fps: Frames per second
    
    Returns:
        Dict with focal_length, focus_distance, look_at_target keyframe lists
    """
    # For now, just pass through the settings
    # TODO: Implement look_at_target keyframe processing
    return {}
    


# =============================================================================
# MAIN PLANNING FUNCTION
# =============================================================================

def plan_motion(movie_folder: str) -> Dict[str, Any]:
    """
    Main entry point: Process movie folder and generate Unreal-ready keyframes.
    
    Args:
        movie_folder: Path to movie folder (e.g., dist/runners_overhead/)
    
    Returns:
        Dict with:
            - meta: Movie metadata
            - actors: Dict[actor_name, keyframe_data]
            - camera_cuts: List of camera cut events
    
    This is called by run_scene.py after loading the movie data.
    """
    log(f"=== Planning Motion from: {movie_folder} ===")
    
    # Load movie data
    movie_data = load_movie(movie_folder)
    meta = movie_data["meta"]
    actors_tracks = movie_data["actors"]
    
    fps = meta.get("fps", 60)
    
    # Process each actor's tracks
    actors_keyframes = {}
    for actor_name, tracks in actors_tracks.items():
        log(f"Processing actor: {actor_name}")
        
        actor_state = {}
        keyframes = {"keyframes": {}, "waypoints": []}
        
        # Process transform track
        if "transform" in tracks:
            transform_data = process_transform_track(tracks["transform"], actor_state, fps)
            keyframes["keyframes"].update(transform_data)
        
        # Process animation track
        if "animation" in tracks:
            anim_data = process_animation_track(tracks["animation"], actor_state, fps)
            keyframes["keyframes"]["animations"] = anim_data
        
        # Process camera settings track
        if "settings" in tracks:
            settings_data = process_camera_settings_track(tracks["settings"], actor_state, fps)
            keyframes["keyframes"].update(settings_data)
        
        actors_keyframes[actor_name] = keyframes
    
    # Load camera cuts if present
    camera_cuts = []
    cuts_path = os.path.join(movie_folder, "camera_cuts.json")
    if os.path.exists(cuts_path):
        with open(cuts_path, 'r', encoding='utf-8') as f:
            camera_cuts = json.load(f)
    
    return {
        "meta": meta,
        "actors": actors_keyframes,
        "camera_cuts": camera_cuts
    }


# =============================================================================
# UNREAL INTEGRATION
# =============================================================================

def apply_to_sequence(keyframe_data: Dict[str, Any], sequence, fps: int):
    """
    Apply processed keyframes to an Unreal LevelSequence.
    
    Args:
        keyframe_data: Output from plan_motion()
        sequence: Unreal LevelSequence object
        fps: Frames per second
    
    This delegates to motion_includes/keyframe_applier.py
    """
    # TODO: Implement
    raise NotImplementedError()


# =============================================================================
# STANDALONE TESTING
# =============================================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = plan_motion(sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python motion_planner.py <movie_folder>")
