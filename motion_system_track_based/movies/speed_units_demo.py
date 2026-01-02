"""
Speed Units Demo - Demonstrating at_mph, at_mps, at_kph

Shows different ways to specify speed in the fluent API.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    """Demonstrate speed unit methods"""
    
    with MovieBuilder("Speed Units Demo", fps=60) as movie:
        movie.add_floor("Track", location=(0, 0, -0.5), scale=2000)
        
        # Add three runners at different speeds
        movie.add_actor("Jogger", location=(0, 500, 0), yaw_offset=-90, radius=0.5)
        movie.add_actor("Runner", location=(0, 300, 0), yaw_offset=-90, radius=0.5)
        movie.add_actor("Sprinter", location=(0, 100, 0), yaw_offset=-90, radius=0.5)
        
        # Jogger: 6 mph (typical jogging pace)
        with movie.for_actor("Jogger") as r:
            r.animation("Jog_Fwd")
            r.move().by_distance(100).at_mph(6)
        
        # Runner: 12 km/h (moderate running pace)
        with movie.for_actor("Runner") as r:
            r.animation("Jog_Fwd")
            r.move().by_distance(100).at_kph(12)
        
        # Sprinter: 10 m/s (Usain Bolt territory!)
        with movie.for_actor("Sprinter") as r:
            r.animation("Jog_Fwd")
            r.move().by_distance(100).at_mps(10)
        
        # Camera
        movie.add_camera("SideView", location=(5000, -1000, 200))\
             .rotation((0, 90, 0))\
             .add()
        
        movie.at_time(0).camera_cut("SideView")
        
        movie.save_to_json("dist/speed_units_demo.json")
    
    movie.run(to_unreal=True)
    return movie.build()

MOVIE = define_movie()

if __name__ == "__main__":
    print("Speed Units Demo:")
    print("  Jogger: 6 mph")
    print("  Runner: 12 km/h")
    print("  Sprinter: 10 m/s")
