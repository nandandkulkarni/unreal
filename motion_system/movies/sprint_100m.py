"""
100m Sprint - Simple Movie Definition

Single runner on a straight 100m track.
Used for testing visualizer and basic mechanics.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    """Define 100m sprint choreography"""
    
    with MovieBuilder("100m Sprint", create_new_level=True, fps=60) as movie:
        
        # Environment
        movie.delete_all_floors()
        movie.add_floor("Track", location=(0, 0, -0.5), scale=2000)
        
        # Lane 1 runner at start line (0,0)
        movie.add_actor("Runner1", location=(0, 0, 0), yaw_offset=0)
        
        # Lane 6 runner (last track) at y=6.1 (5 * 1.22m)
        movie.add_actor("Runner2", location=(0, 6.1, 0), yaw_offset=0)
        
        # Race choreography
        with movie.simultaneous() as group:
            with group.for_actor("Runner1") as r1:
                r1.animation("Sprint_Fwd")
                r1.move_for_seconds(
                    seconds=15.0,
                    direction="forward",
                    speed_mtps=10.0,
                    acceleration=2.0
                )
            
            with group.for_actor("Runner2") as r2:
                r2.animation("Sprint_Fwd")
                r2.move_for_seconds(
                    seconds=15.0,
                    direction="forward",
                    speed_mtps=10.5, # Slightly faster
                    acceleration=2.2  # Slightly better start
                )
            
        movie.add_camera("SideView", location=(5000, -1000, 200), rotation=(0, 90, 0))
        movie.at_time(0).camera_cut("SideView")
        
    return movie.build()

MOVIE = define_movie()

if __name__ == "__main__":
    print(f"Movie built with {len(MOVIE['plan'])} commands")
