"""
100m Sprint with Tracking Camera

Demonstrates the Fluent Camera API with look_at_actor functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, DistanceUnit, SpeedUnit, TimeUnit

def define_movie():
    """Define 100m sprint with tracking camera"""
    
    with MovieBuilder("Sprint With Camera", fps=60) as movie:
        #movie.add_floor("Track", location=(0, 0, -0.5), scale=2000)
        
        # Add runners
        movie.add_actor("Runner1", location=(0, 305, 0), yaw_offset=-90, radius=0.5, height=1.8)
        movie.add_actor("Runner2", location=(0, 183, 0), yaw_offset=-90, radius=0.5, height=1.8)
        
        # Run runners in parallel
        with movie.simultaneous():
            # Runner 1 (Standard Sprint)
            with movie.for_actor("Runner1") as r:
                r.move_straight().direction(Direction.FORWARD).in_corridor(2.44, 3.66).anim("Jog_Fwd").distance_at_speed((DistanceUnit.Meters, 100.0), (SpeedUnit.MetersPerSecond, 10.0))
                r.stay().anim("Idle").till_end()

            # Runner 2 (Walk then Run)
            with movie.for_actor("Runner2") as r:
                # Face South and move South (running forward while facing South)
                r.face(Direction.SOUTH, duration=0.1)
                r.move_straight().direction(Direction.SOUTH).anim("Jog_Fwd").distance_in_time((DistanceUnit.Meters, 21.0), (TimeUnit.Seconds, 7.0))
                
                # Turn to face North and continue moving North
                r.face(Direction.NORTH, duration=2.0)
                r.move_straight().direction(Direction.NORTH).anim("Jog_Fwd").distance_in_time((DistanceUnit.Meters, 79.0), (TimeUnit.Seconds, 8.0))
                r.stay().till_end().anim("Idle")
            
        # --- Camera Setup ---
        
        # Front/Finish Camera (Positioned between lanes, switches focus every 4s)
        # Positioned past the finish line (110m), centered between lanes
        movie.add_camera("FrontCam", location=(11000, 244, 200)).add()
        
        with movie.for_camera("FrontCam") as cam:
            # 0-4s: Focus on Runner1 with auto-zoom
            cam.frame_subject("Runner1", coverage=0.7)
            cam.look_at("Runner1", height_pct=0.7, interp_speed=5.0)
            cam.focus_on("Runner1", height_pct=0.7)
            cam.wait(4.0)
            
            # 4-8s: Switch to Runner2 with auto-zoom
            cam.frame_subject("Runner2", coverage=0.7)
            cam.look_at("Runner2", height_pct=0.7, interp_speed=5.0)
            cam.focus_on("Runner2", height_pct=0.7)
            cam.wait(4.0)
            
            # 8-10s: Switch back to Runner1 with auto-zoom
            cam.frame_subject("Runner1", coverage=0.7)
            cam.look_at("Runner1", height_pct=0.7, interp_speed=5.0)
            cam.focus_on("Runner1", height_pct=0.7)
            cam.stay().till_end()

        # Cut plan
        movie.add_audio(asset_path="/Game/MyAudio/Sopranos_-_High_Quality.Sopranos_-_High_Quality", start_time=0.0)
        movie.at_time(0.0).camera_cut("FrontCam")
        
        movie.save_to_json("dist/sprint_with_camera.json")
    
    movie.run(to_unreal=True)
    return movie.build()

# QA Metadata (optional, declarative)
QA = {
    "frames": [0, 300, 600],
    "description": "Verify auto-framing: start (telephoto), middle (medium), end (wide)",
    "expectations": {
        "subject": "Runner1",
        "coverage": 0.7
    }
}

MOVIE = define_movie()

if __name__ == "__main__":
    print("Movie built.")
