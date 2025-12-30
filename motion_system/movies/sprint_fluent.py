"""
100m Sprint - Fluent API Demonstration

Uses chained .move() commands, velocity ramping, and corridor constraints.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    """Define 100m sprint using Fluent API"""
    
    with MovieBuilder("Fluent Sprint", fps=60) as movie:
        
        movie.delete_all_floors()
        movie.add_floor("Track", location=(0, 0, -0.5), scale=2000)
        
        # Add runner at start (305cm is the center of the 2.44m-3.66m corridor)
        movie.add_actor("Runner1", location=(0, 305, 0), yaw_offset=0)
        
        # Fluent Chained Choreography
        with movie.for_actor("Runner1") as r:
            r.animation("Sprint_Fwd")
            
            r.move() \
                .by_distance(20.0) \
                .velocity(to=10.0, start_from=0.0) \
                .in_corridor(left=2.44, right=3.66) \
                .with_radius(0.5) \
              .move() \
                .by_distance(80.0) \
                .speed(10.0) \
                .in_corridor(left=2.44, right=3.66) \
              .move() \
                .for_seconds(3.0) \
                .velocity(to=0.0) \
                .in_corridor(left=2.44, right=3.66)
            
        movie.add_camera("SideView", location=(5000, -1000, 200), rotation=(0, 90, 0))
        movie.at_time(0).camera_cut("SideView")
        
    return movie.build()

MOVIE = define_movie()

if __name__ == "__main__":
    print(f"Movie built with {len(MOVIE['plan'])} commands")
    for i, cmd in enumerate(MOVIE['plan']):
        if "command" in cmd:
            print(f"{i}: {cmd['command']} (Actor: {cmd.get('actor', 'N/A')})")
