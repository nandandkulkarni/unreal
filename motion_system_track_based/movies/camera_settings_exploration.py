"""
Camera Settings Exploration
One character, one camera, distant framing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, DistanceUnit, SpeedUnit, CHARACTER_HEIGHT
from motion_includes.assets import Characters, Shapes

# Explorations Settings
FOCAL_LENGTH = 1662.0  # [EDITABLE_FOCAL_LENGTH]
SET_HEIGHT = 1.9  # [EDITABLE_SET_HEIGHT]
CHARACTER_DATA = Characters.BELICA  # [EDITABLE_CHARACTER]


def define_movie(char_data=CHARACTER_DATA):
    """Define a simple camera exploration scene"""
    
    movie = MovieBuilder("Camera Settings Exploration", fps=60)
    
    # Configuration
    PERSON = "Subject"
    CAM = "ExplorerCam"
    REF_MARKER = "ReferenceMarker"
    
    # 1. Add Subject at Origin
    # Use object properties
    # Note: SET_HEIGHT is used for scaling the marker, but for actor height we might want the data's height?
    # However, exploration often wants to override/experiment. Let's keep SET_HEIGHT but allow char_data usage.
    movie.add_actor(PERSON, location=(0, 0, 0), mesh_path=char_data.path, height=SET_HEIGHT, yaw_offset=char_data.initial_yaw)
    
    # 2. Add Reference Cylinder behind and to the side
    # Belica facing -90 yaw (Negative Y). Behind her is Positive Y.
    # Height in meters, so conversion to scale (Unreal basic cylinder is 1m)
    cube_height_cm = SET_HEIGHT * 100
    movie.add_group_target(REF_MARKER, location=(0, 100, 0)) \
         .shape("Cylinder") \
         .mesh_scale(1, 1, SET_HEIGHT) \
         .color("Red")
    
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
        cam.look_at_subject(PERSON, height_pct=0.9)
        cam.auto_focus_subject(PERSON, height_pct=0.9)
        cam.set_focal_length(FOCAL_LENGTH)
        cam.wait(10.0)
    
    # Camera cuts
    movie.at_time(0).camera_cut(CAM)
    
    return movie

if __name__ == "__main__":
    movie = define_movie(CHARACTER_DATA)
    movie.save_to_tracks().run(to_unreal=True)
