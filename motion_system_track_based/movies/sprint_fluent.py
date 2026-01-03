"""
100m Sprint - Track-Based API
Migrated from old motion_system to new track-based architecture.

Two runners sprinting 100m with acceleration/deceleration phases.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, SpeedUnit, DistanceUnit

def define_movie():
    """Define 100m sprint using track-based Fluent API"""
    
    movie = MovieBuilder("Sprint Fluent Track", fps=60)
    
    # Add runners with explicit mesh path
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    
    # Runner 1 - Lane 3 (Y=305cm from center)
    movie.add_actor("Runner1", location=(0, 305, 0), mesh_path=belica_path)
    
    # Runner 2 - Lane 2 (Y=183cm from center)
    movie.add_actor("Runner2", location=(0, 183, 0), mesh_path=belica_path)
    
    # Camera - Side view
    movie.add_camera("SideView", location=(5000, -1000, 200)) \
         .rotation((0, 0, 90)) \
         .add()
    
    movie.at_time(0).camera_cut("SideView")
    
    # Runner choreography using simultaneous block
    with movie.simultaneous():
        # Runner 1 (Lane 3) - 100m sprint
        with movie.for_actor("Runner1") as r1:
            r1.face(Direction.NORTH)
            
            # Phase 1: Acceleration (0-20m, 0-10 m/s)
            r1.move_straight() \
                .direction(Direction.FORWARD) \
                .anim("Jog_Fwd") \
                .distance_at_speed((DistanceUnit.Meters, 20), (SpeedUnit.MetersPerSecond, 5))
            
            # Phase 2: Top speed (20-100m, constant 10 m/s)
            r1.move_straight() \
                .direction(Direction.FORWARD) \
                .anim("Jog_Fwd") \
                .distance_at_speed((DistanceUnit.Meters, 80), (SpeedUnit.MetersPerSecond, 10))
            
            # Phase 3: Deceleration (3 seconds to stop)
            r1.move_straight() \
                .direction(Direction.FORWARD) \
                .anim("Jog_Fwd") \
                .distance_in_time(15, 3)  # Slow down over 3 seconds
            
            # Stay at finish
            r1.stay().till_end().anim("Idle")
        
        # Runner 2 (Lane 2) - Slightly faster
        with movie.for_actor("Runner2") as r2:
            r2.face(Direction.NORTH)
            
            # Phase 1: Acceleration (0-22m)
            r2.move_straight() \
                .direction(Direction.FORWARD) \
                .anim("Jog_Fwd") \
                .distance_at_speed((DistanceUnit.Meters, 22), (SpeedUnit.MetersPerSecond, 5.5))
            
            # Phase 2: Top speed (22-100m, 10.5 m/s)
            r2.move_straight() \
                .direction(Direction.FORWARD) \
                .anim("Jog_Fwd") \
                .distance_at_speed((DistanceUnit.Meters, 78), (SpeedUnit.MetersPerSecond, 10.5))
            
            # Phase 3: Deceleration
            r2.move_straight() \
                .direction(Direction.FORWARD) \
                .anim("Jog_Fwd") \
                .distance_in_time(15, 3)
            
            # Stay at finish
            r2.stay().till_end().anim("Idle")
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
