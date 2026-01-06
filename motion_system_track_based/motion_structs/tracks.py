from __future__ import annotations
import os
import json
from typing import Dict, List, Any, Tuple

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
