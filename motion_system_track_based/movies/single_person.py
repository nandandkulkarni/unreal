"""
Single Person Motion Sequence
Derived from Sprint with Tracking Camera.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    """Define single person sequence"""
    
    with MovieBuilder("Single Person Test", fps=60) as movie:
        # Add actor
        movie.add_actor("Runner1", location=(0, 0, 0), yaw_offset=-90)
        
        # Runner 1 (Standard Sprint)
        with movie.for_actor("Runner1") as r:
            # Face South
            r.face(Direction.SOUTH)
            r.move_straight().direction(Direction.SOUTH).distance_in_time(2.0, 1.0)
            r.face(Direction.NORTH)
            r.move_straight().direction(Direction.NORTH).distance_in_time(2.0, 1.0)
            r.face(Direction.NORTH)
            r.move_straight().anim("Jog_Fwd").by_distance(75.0).speed(10.0).in_corridor(2.44, 3.66)
        # --- Camera Setup ---
        
        # Front/Finish Camera
        movie.add_camera("FrontCam", location=(11000, 244, 200)).add()
        
        with movie.for_camera("FrontCam") as cam:
            # Focus on Runner1 throughout
            cam.frame_subject("Runner1", coverage=0.7)
            cam.look_at("Runner1", height_pct=0.7, interp_speed=5.0)
            cam.focus_on("Runner1", height_pct=0.7)
            cam.wait(10.0)

        # Cut plan
        movie.at_time(0.0).camera_cut("FrontCam")
        
        movie.save_to_json("dist/single_person.json")
    
    movie.run(to_unreal=True)
    return movie.build()

# QA Metadata
QA = {
    "frames": [0, 300, 600],
    "description": "Verify tracking of single actor",
    "expectations": {
        "subject": "Runner1",
        "coverage": 0.7
    }
}

MOVIE = define_movie()

if __name__ == "__main__":
    print("Movie built.")
