"""
100m Sprint - Fluent API Demonstration

Uses chained .move_straight() commands, velocity ramping, and corridor constraints.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    """Define 100m sprint using Fluent API"""
    
    with MovieBuilder("Fluent Sprint", fps=60) as movie:
        
        ##movie.delete_all_floors()
        ##movie.add_floor("Track", location=(0, 0, -0.5), scale=2000)
        
        # Add runners (radius is set here and stays with the actor)
        movie.add_actor("Runner1", location=(0, 305, 0), yaw_offset=-90, radius=0.5)
        movie.add_actor("Runner2", location=(0, 183, 0), yaw_offset=-90, radius=0.5)
        
        # Runner Choreography in Parallel
        with movie.simultaneous():
            # Runner 1 (Lane 3)
            with movie.for_actor("Runner1") as r:
                r.animation("Jog_Fwd")
                r.move_straight() \
                    .by_distance(20.0).velocity(to=10.0, start_from=0.0).in_corridor(2.44, 3.66) \
                    .move_straight() \
                    .by_distance(80.0).speed(10.0).in_corridor(2.44, 3.66) \
                    .move_straight() \
                    .for_seconds(3.0).velocity(to=0.0).in_corridor(2.44, 3.66)
                r.stay().till_end()

            # Runner 2 (Lane 2)
            with movie.for_actor("Runner2") as r:
                r.animation("Jog_Fwd")
                r.move_straight() \
                    .by_distance(22.0).velocity(to=10.5, start_from=0.0).in_corridor(1.22, 2.44) \
                    .move_straight() \
                    .by_distance(78.0).speed(10.5).in_corridor(1.22, 2.44) \
                    .move_straight() \
                    .for_seconds(3.0).velocity(to=0.0).in_corridor(1.22, 2.44)
                r.stay().till_end()
            
        movie.add_camera("SideView", location=(5000, -1000, 200)).rotation((0, 90, 0)).add()
        movie.at_time(0).camera_cut("SideView")
        
        # Standardize export path
        movie.save_to_json("dist/sprint_fluent.json")
    movie.run(to_unreal=True)
        
    return movie.build()

MOVIE = define_movie()

if __name__ == "__main__":
    print(f"Movie built with {len(MOVIE['plan'])} commands")
    for i, cmd in enumerate(MOVIE['plan']):
        if "command" in cmd:
            print(f"{i}: {cmd['command']} (Actor: {cmd.get('actor', 'N/A')})")
