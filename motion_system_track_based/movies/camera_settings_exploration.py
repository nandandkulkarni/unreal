"""
Camera Settings Exploration
One character, one camera, distant framing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, DistanceUnit, SpeedUnit, CHARACTER_HEIGHT

def define_movie():
    """Define a simple camera exploration scene"""
    
    movie = MovieBuilder("Camera Settings Exploration", fps=60)
    
    # Configuration
    PERSON = "Subject"
    CAM = "ExplorerCam"
    
    # 1. Add Subject at Origin
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor(PERSON, location=(0, 0, 0), mesh_path=belica_path, height=1.8, yaw_offset=-90)
    
    with movie.for_actor(PERSON) as p:
        p.stay().for_time(10.0).anim("Idle")
    
    # 2. Add Camera 100m away (X=10,000)
    # Looking at the person from the front
    movie.add_camera(CAM, location=(10000, 0, 150)) \
         .look_at_subject(PERSON, height_pct=0.9) \
         .add()
    
    # 3. Dynamic Camera Commands
    with movie.for_camera(CAM) as cam:
        # Track at 90% height, Focus at 90% height
        # Using focus_zoom_track for convenience
        # focus_pct (Focus height) = 0.9
        # track_pct (LookAt height) = 0.9
        # zoom_pct (Coverage) = 0.8 (fill 80% of frame)
        cam.focus_zoom_track(PERSON, focus_pct=0.9, zoom_pct=0.8, track_pct=0.9)
        cam.wait(10.0)
    
    # Camera cuts
    movie.at_time(0).camera_cut(CAM)
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks().run(to_unreal=True)
