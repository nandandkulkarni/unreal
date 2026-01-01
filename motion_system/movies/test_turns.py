"""
Rotation Test Movie
Performs 4 turns, each 90 degrees, taking 2 seconds per turn.
Used to debug why actor rotations might not be applying.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    """Define rotation test sequence"""
    
    with MovieBuilder("Rotation Test", fps=60) as movie:
        # Add actor (Facing North/0 by default)
        movie.add_actor("TestActor", location=(0, 0, 0), yaw_offset=0, radius=0.5, height=1.8)
        
        with movie.for_actor("TestActor") as a:
            # 4 turns: East, South, West, North (Complete circle)
            a.face("East", duration=2.0)
            a.face("South", duration=2.0)
            a.face("West", duration=2.0)
            a.face("North", duration=2.0)

        # Basic Camera to watch the rotation
        movie.add_camera("Observer", location=(-300, 0, 150)).add()
        with movie.for_camera("Observer") as cam:
            cam.look_at("TestActor", height_pct=0.7)
            cam.wait(10.0)

        movie.at_time(0.0).camera_cut("Observer")
        
        movie.save_to_json("dist/test_turns.json")
    
    movie.run(to_unreal=True)
    return movie.build()

if __name__ == "__main__":
    define_movie()
    print("Rotation Test Movie Built.")
