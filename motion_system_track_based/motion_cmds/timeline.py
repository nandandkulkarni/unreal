from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from motion_builder import MovieBuilder

class TimelineBuilder:
    """
    Builder for time-based global commands (camera cuts, markers).
    """
    
    def __init__(self, movie_builder: 'MovieBuilder', time_sec: float):
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
