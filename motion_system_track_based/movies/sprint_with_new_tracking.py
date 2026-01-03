"""
100m Sprint with Tracking Camera - Track-Based
Migrated from old motion_system to new track-based architecture.

Demonstrates camera look_at functionality with two runners.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, DistanceUnit, SpeedUnit

def define_movie():
    """Define 100m sprint with tracking camera"""
    
    movie = MovieBuilder("Sprint With Camera Track", fps=60)
    
    # Add runners with explicit mesh path
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    
    # Runner 1 - Lane 3 (Y=305cm from center)
    movie.add_actor("Runner1", location=(0, 0, 0), yaw_offset=-90, mesh_path=belica_path)
    
    # Runner 2 - Lane 2 (Y=183cm from center)
    movie.add_actor("Runner2", location=(0, -100, 0), yaw_offset=-90, mesh_path=belica_path)
    
    # Run runners in parallel
    with movie.simultaneous():
        # Runner 1 - Standard sprint north
        with movie.for_actor("Runner1") as r1:
            r1.face(Direction.NORTH)
            r1.move_straight() \
                .direction(Direction.NORTH) \
                .anim("Jog_Fwd") \
                .distance_at_speed((DistanceUnit.Meters, 100), (SpeedUnit.MetersPerSecond, 10))
            r1.stay().till_end().anim("Idle")
        
       
    
    # Front/Finish Camera - positioned past finish line, centered between lanes
    # 11000cm = 110m, 244cm = midpoint between lanes
    movie.add_camera("FrontCam", location=(11000, -50, 200)) \
         .look_at_subject("Runner1", height_pct=0.7) \
         .add()
    
    # Camera cuts
    movie.at_time(0).camera_cut("FrontCam")
    
    # Camera commands (switching focus between runners)
    with movie.for_camera("FrontCam") as cam:
        # 0-4s: Focus on Runner1
        cam.look_at_subject("Runner1", height_pct=0.7)
        cam.auto_zoom_subject("Runner1", coverage=0.7)
        cam.auto_focus_subject("Runner1", height_pct=0.7)
        cam.wait(4.0)
        
        # # 4-8s: Switch to Runner2
        # cam.look_at_subject("Runner2", height_pct=0.7)
        # cam.auto_zoom_subject("Runner2", coverage=0.7)
        # cam.auto_focus_subject("Runner2", height_pct=0.7)
        # cam.wait(4.0)
        
        # 8s+: Switch back to Runner1
        cam.look_at_subject("Runner1", height_pct=0.7)
        cam.auto_zoom_subject("Runner1", coverage=0.7)
        cam.auto_focus_subject("Runner1", height_pct=0.7)
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
