from __future__ import annotations
import os
import json
from typing import Dict, List, Any, Tuple
from motion_structs.tracks import TransformTrack, AnimationTrack, CameraSettingsTrack, AttachTrack

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

        # Save focal length keyframes if present
        if hasattr(self, "focal_length_keyframes") and self.focal_length_keyframes:
            focal_path = os.path.join(actor_folder, "focal_length.json")
            with open(focal_path, 'w', encoding='utf-8') as f:
                json.dump(self.focal_length_keyframes, f, indent=2)


class GroupTargetActor(ActorTrackSet):
    """
    Actor that dynamically tracks the midpoint of other actors.
    """
    def __init__(self, name: str, members: List[str] = None):
        super().__init__(name, actor_type="marker")  # Use marker type, not mannequin
        self.members = members or []
        self.computation_interval_ms = 1000.0 # Default 1s
    
    def compute_track(self, movie_builder):
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


class SplineActor(ActorTrackSet):
    """
    Represents a Spline Path.
    Stores control points for interpolation.
    """
    def __init__(self, name: str, points: List[Tuple[float, float, float]], closed: bool = False):
        super().__init__(name, actor_type="spline")
        self.points = points
        self.closed = closed
        self.tension = 0.5
        
        # Properties for visualization
        self.initial_state["properties"] = {
            "points": self.points,
            "closed": self.closed,
            "tension": self.tension,
            "color": "Green",
            "thickness": 5.0,
            "show_debug": True
        }
    
    def save(self, base_folder: str):
        # Override to ensure properties are updated before saving settings
        self.initial_state["properties"]["points"] = self.points
        self.initial_state["properties"]["closed"] = self.closed
        self.initial_state["properties"]["tension"] = self.tension
        super().save(base_folder)
