"""
Rotation & Movement Test Movie
Phase 1 (0-8s): 4 turns watched by Overhead Camera (Static check)
Phase 2 (8-24s): 4 moves watched by Tracking Camera (Motion check)
Values are adjusted to use explicit face() + move_straight() pattern.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    """Define rotation and movement test sequence"""
    
    with MovieBuilder("Rotation Test", fps=60) as movie:
        from motion_builder import TimeSpan
        
        # Add actor (Facing North/0 by default)
        movie.add_actor("TestActor", location=(0, 0, 0), yaw_offset=-90, radius=0.5, height=1.8)
        
        with movie.for_actor("TestActor") as a:
            # Phase 1: 4 turns (0-8s) - Spins in place
            a.face("East", duration=2.0, anim="Jog_Fwd")
            a.face("South", duration=2.0, anim="Jog_Fwd")
            a.face("West", duration=2.0, anim="Jog_Fwd")
            a.face("North", duration=2.0, anim="Jog_Fwd")
            
            # Phase 2: 4 path segments (8-24s)
            # We must face the direction FIRST, then move forward.
            
            # Segment 1: Move North (Already facing North from Phase 1)
            a.move_straight().direction("North").anim("Jog_Fwd").distance_in_time(10.0, 5.0)
            
            # Segment 2: Turn East then Move East
            a.face("East", duration=2.0)
            a.move_straight().direction("East").anim("Jog_Fwd").distance_in_time(10.0, 5.0)
            
            # Segment 3: Turn South then Move South
            a.face("South", duration=2.0)
            a.move_straight().direction("South").anim("Jog_Fwd").distance_in_time(10.0, 5.0)
            
            # Segment 4: Turn West then Move West
            a.face("West", duration=2.0)
            a.move_straight().direction("West").anim("Jog_Fwd").distance_in_time(10.0, 5.0)
            
            # Terminal State: Stay until the end of the shot
            a.stay().anim("Idle").till_end()

        # --- Camera Setup ---
        
        # Camera 1: Overhead (Static, proof of no sliding during turns)
        movie.add_camera("OverheadCam", location=(0, 0, 800)).add()
        with movie.for_camera("OverheadCam") as cam:
            cam.look_at("TestActor", height_pct=0.0) 
            cam.wait(8.0)

        # Camera 2: Tracking (Shows the movement phase)
        movie.add_camera("TrackingCam", location=(-800, -800, 500)).add()
        with movie.for_camera("TrackingCam") as cam:
            cam.look_at("TestActor", height_pct=0.7)
            cam.focus_on("TestActor", height_pct=0.7)
            cam.wait(TimeSpan.from_seconds(26.0)) # Extend camera slightly to test till_end

        # Camera Cuts
        movie.at_time(0.0).camera_cut("OverheadCam")
        movie.at_time(8.0).camera_cut("TrackingCam")
        
    movie.save_to_json("dist/test_turns.json")
    movie.run(to_unreal=True)
    return movie.build()

if __name__ == "__main__":
    define_movie()
    print("Enhanced Rotation & Movement Test Built (Forward-Only Movement).")
