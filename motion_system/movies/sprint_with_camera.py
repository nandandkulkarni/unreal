"""
100m Sprint with Tracking Camera

Demonstrates the Fluent Camera API with look_at_actor functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    """Define 100m sprint with tracking camera"""
    
    with MovieBuilder("Sprint With Camera", fps=60) as movie:
        #movie.add_floor("Track", location=(0, 0, -0.5), scale=2000)
        
        # Add runners
        movie.add_actor("Runner1", location=(0, 305, 0), yaw_offset=-90, radius=0.5)
        movie.add_actor("Runner2", location=(0, 183, 0), yaw_offset=-90, radius=0.5)
        
        # Runner 1 (Standard Sprint)
        with movie.for_actor("Runner1") as r:
            r.animation("Jog_Fwd")
            r.move().by_distance(100.0).speed(10.0).in_corridor(2.44, 3.66)

        # Runner 2 (Standard Sprint)
        with movie.for_actor("Runner2") as r:
            r.animation("Jog_Fwd")
            r.move().by_distance(100.0).speed(10.5).in_corridor(1.22, 2.44)
            
        # --- Camera Setup ---
        
        # Front/Finish Camera (Locked to Runner1)
        # Positioned past the finish line (110m), looking back
        movie.add_camera("FrontCam", location=(11000, 244, 200))\
             .look_at("Runner1")\
             .fov(90)\
             .add()

        # Cut plan
        movie.at_time(0.0).camera_cut("FrontCam")
        
        movie.save_to_json("dist/sprint_with_camera.json")
    
    movie.run(to_unreal=True)
    return movie.build()

MOVIE = define_movie()

if __name__ == "__main__":
    print("Movie built.")
