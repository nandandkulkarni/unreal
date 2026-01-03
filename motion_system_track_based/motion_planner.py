"""
Motion Planner for Track-Based System
Generates camera keyframes from timelines (look_at, frame_subject, focus_on)
"""

import json
import math
import os
from typing import Dict, List, Tuple, Any


def euclidean_distance_3d(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
    """Calculate 3D Euclidean distance between two points."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)


def calculate_focal_length(camera_pos: Tuple[float, float, float], 
                          subject_pos: Tuple[float, float, float],
                          subject_height: float = 180.0,  # cm
                          coverage: float = 0.7,
                          sensor_height: float = 24.0) -> float:
    """
    Calculate required focal length to frame subject at desired coverage.
    
    Args:
        camera_pos: (x, y, z) camera location in cm
        subject_pos: (x, y, z) subject location in cm
        subject_height: Height of subject in cm (default 180cm for human)
        coverage: 0.0-1.0, how much of frame height subject should fill
        sensor_height: Camera sensor height in mm (default 24mm full frame)
    
    Returns:
        focal_length in mm
    """
    # Calculate distance in meters
    distance = euclidean_distance_3d(camera_pos, subject_pos) / 100.0
    
    # Avoid division by zero
    if distance < 0.1:
        distance = 0.1
    
    # Convert subject height to meters
    subject_height_m = subject_height / 100.0
    
    # Calculate required frame height for desired coverage
    frame_height_needed = subject_height_m / coverage if coverage > 0 else subject_height_m
    
    # Calculate FOV needed
    fov_height_radians = 2 * math.atan(frame_height_needed / (2 * distance))
    
    # Calculate focal length
    # focal_length = sensor_height / (2 * tan(fov/2))
    focal_length = sensor_height / (2 * math.tan(fov_height_radians / 2))
    
    return focal_length


def calculate_look_at_rotation(camera_pos: Tuple[float, float, float],
                               target_pos: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate rotation (roll, pitch, yaw) for camera to look at target.
    
    Args:
        camera_pos: (x, y, z) camera location in cm
        target_pos: (x, y, z) target location in cm
    
    Returns:
        (roll, pitch, yaw) in degrees
    """
    # Vector from camera to target
    dx = target_pos[0] - camera_pos[0]
    dy = target_pos[1] - camera_pos[1]
    dz = target_pos[2] - camera_pos[2]
    
    # Calculate yaw (horizontal rotation)
    # atan2(dy, dx) gives angle in XY plane
    yaw = math.degrees(math.atan2(dy, dx))
    
    # Calculate pitch (vertical rotation)
    # Distance in XY plane
    horizontal_dist = math.sqrt(dx*dx + dy*dy)
    pitch = -math.degrees(math.atan2(dz, horizontal_dist))  # Negative for Unreal convention
    
    # Roll is typically 0 for cameras
    roll = 0.0
    
    return (roll, pitch, yaw)


def load_actor_transform(movie_folder: str, actor_name: str) -> List[Dict]:
    """Load actor's transform.json keyframes."""
    transform_path = os.path.join(movie_folder, actor_name, "transform.json")
    if not os.path.exists(transform_path):
        return []
    
    with open(transform_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_position_at_frame(keyframes: List[Dict], frame: int) -> Tuple[float, float, float]:
    """
    Get interpolated position at a specific frame.
    Uses linear interpolation between keyframes.
    """
    if not keyframes:
        return (0, 0, 0)
    
    # If before first keyframe, use first
    if frame <= keyframes[0]["frame"]:
        kf = keyframes[0]
        return (kf["x"], kf["y"], kf["z"])
    
    # If after last keyframe, use last
    if frame >= keyframes[-1]["frame"]:
        kf = keyframes[-1]
        return (kf["x"], kf["y"], kf["z"])
    
    # Find surrounding keyframes
    for i in range(len(keyframes) - 1):
        kf1 = keyframes[i]
        kf2 = keyframes[i + 1]
        
        if kf1["frame"] <= frame <= kf2["frame"]:
            # Linear interpolation
            t = (frame - kf1["frame"]) / (kf2["frame"] - kf1["frame"])
            x = kf1["x"] + t * (kf2["x"] - kf1["x"])
            y = kf1["y"] + t * (kf2["y"] - kf1["y"])
            z = kf1["z"] + t * (kf2["z"] - kf1["z"])
            return (x, y, z)
    
    return (0, 0, 0)


def generate_camera_keyframes(movie_folder: str, camera_name: str, 
                              look_at_timeline: List[Tuple], 
                              frame_subject_timeline: List[Tuple],
                              focus_timeline: List[Tuple],
                              fps: int = 60,
                              camera_location: Tuple[float, float, float] = None) -> Dict[str, List]:
    """
    Generate all camera keyframes from timelines.
    
    Args:
        movie_folder: Path to dist/MovieName folder
        camera_name: Name of camera
        look_at_timeline: [(start_time, end_time, actor_name, height_pct, interp_speed)]
        frame_subject_timeline: [(start_time, end_time, actor_name, coverage)]
        focus_timeline: [(start_time, end_time, actor_name, height_pct)]
        fps: Frames per second
        camera_location: Optional explicit camera location (x, y, z)
    
    Returns:
        {
            "rotation": [...],  # For transform.json
            "focal_length": [...],  # For focal_length.json
            "focus_distance": [...]  # For focus_distance.json
        }
    """
    rotation_keyframes = []
    focal_length_keyframes = []
    focus_distance_keyframes = []
    
    # Load camera's static position
    camera_pos = camera_location
    if not camera_pos:
        camera_transform = load_actor_transform(movie_folder, camera_name)
        if camera_transform:
            camera_pos = (camera_transform[0]["x"], camera_transform[0]["y"], camera_transform[0]["z"])
        else:
            camera_pos = (0, 0, 0)  # Default
    
    # Process look_at timeline for rotation keyframes
    # We only generate ONE initial keyframe for the transform track
    # to ensure the camera starts with the correct orientation.
    # The rest is handled by Unreal's LookAt tracking.
    if look_at_timeline:
        segment = look_at_timeline[0]
        start_time, end_time, actor_name, height_pct, interp_speed = segment
        
        if start_time <= 0:
             # Load subject's transform at frame 0
            subject_keyframes = load_actor_transform(movie_folder, actor_name)
            if subject_keyframes:
                # Find frame 0
                target_pos = None
                for kf in subject_keyframes:
                    if kf["frame"] == 0:
                        target_pos = (kf["x"], kf["y"], kf["z"])
                        break
                
                if target_pos:
                    # Adjust for height
                    target_pos_adj = (target_pos[0], target_pos[1], target_pos[2] + (180 * height_pct))
                    
                    # Calculate rotation
                    roll, pitch, yaw = calculate_look_at_rotation(camera_pos, target_pos_adj)
                    
                    # Add single keyframe at frame 0
                    rotation_keyframes.append({
                        "frame": 0,
                        "x": camera_pos[0],
                        "y": camera_pos[1],
                        "z": camera_pos[2],
                        "roll": roll,
                        "pitch": pitch,
                        "yaw": yaw
                    })
    
    # Process frame_subject timeline for focal length keyframes
    for segment in frame_subject_timeline:
        start_time, end_time, actor_name, coverage = segment
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps) if end_time else 99999
        
        subject_keyframes = load_actor_transform(movie_folder, actor_name)
        if not subject_keyframes:
            continue
        
        # Generate focal length keyframes (sample with threshold to reduce keyframes)
        last_focal_length = None
        change_threshold = 0.10  # 10% change (reduced from 5% to minimize keyframes)
        
        for frame in range(start_frame, min(end_frame + 1, 10000), 1):
            subject_pos = get_position_at_frame(subject_keyframes, frame)
            focal_length = calculate_focal_length(camera_pos, subject_pos, coverage=coverage)
            
            # Only add keyframe if significant change
            if last_focal_length is None or abs(focal_length - last_focal_length) / last_focal_length > change_threshold:
                focal_length_keyframes.append({
                    "frame": frame,
                    "value": focal_length
                })
                last_focal_length = focal_length
    
    # Process focus timeline for focus distance keyframes
    for segment in focus_timeline:
        start_time, end_time, actor_name, height_pct = segment
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps) if end_time else 99999
        
        subject_keyframes = load_actor_transform(movie_folder, actor_name)
        if not subject_keyframes:
            continue
        
        # Generate focus distance keyframes
        last_focus_dist = None
        change_threshold = 0.10  # 10% change (reduced from 5% to minimize keyframes)
        
        for frame in range(start_frame, min(end_frame + 1, 10000), 1):
            subject_pos = get_position_at_frame(subject_keyframes, frame)
            subject_pos = (subject_pos[0], subject_pos[1], subject_pos[2] + 180.0 * height_pct)
            focus_dist = euclidean_distance_3d(camera_pos, subject_pos) / 100.0  # Convert to meters
            
            if last_focus_dist is None or abs(focus_dist - last_focus_dist) / last_focus_dist > change_threshold:
                focus_distance_keyframes.append({
                    "frame": frame,
                    "value": focus_dist
                })
                last_focus_dist = focus_dist
    
    return {
        "rotation": rotation_keyframes,
        "focal_length": focal_length_keyframes,
        "focus_distance": focus_distance_keyframes
    }
