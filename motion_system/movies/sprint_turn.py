"""
Corridor Turn/Shift Test

Demonstrates a runner maintaining a straight 'forward' heading 
while the corridor boundaries shift to the right.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    with MovieBuilder("Corridor Turn", fps=60) as movie:
        movie.delete_all_floors()
        movie.add_floor("Track", location=(0, 0, -0.5), scale=3000)
        
        # Start in Lane 1 Center (61cm)
        movie.add_actor("Runner1", location=(0, 61, 0), radius=0.35)
        
        with movie.for_actor("Runner1") as r:
            r.animation("Sprint_Fwd")
            
            # 1. Start Straight in Corridor 1 (Lane 1)
            r.move() \
                .by_distance(30.0) \
                .speed(8.0) \
                .in_corridor(left=0.0, right=1.22) \
              .move() \
                .by_distance(10.0) \
                .speed(8.0) \
                .in_corridor(left=6.10, right=7.32) \
              .move() \
                .by_distance(40.0) \
                .speed(8.0) \
                .in_corridor(left=6.10, right=7.32)
            
        movie.add_camera("TopView", location=(4000, 300, 2000), rotation=(-90, 0, 0))
        movie.at_time(0).camera_cut("TopView")
        
        movie.save_to_json("dist/sprint_turn.json")
        
    return movie.build()

MOVIE = define_movie()

if __name__ == "__main__":
    print(f"Movie built. Runner1 will shift from Y=0.61 to Y=6.71 while moving X+.")
