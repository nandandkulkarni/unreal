"""
100m Sprint with Tracking Camera - Track-Based
Migrated from old motion_system to new track-based architecture.

Demonstrates camera look_at functionality with two runners.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, DistanceUnit, SpeedUnit
from motion_includes.assets import Characters, Animations

# Character/Actor Name Constants
RUNNER_1 = "Runner1"
RUNNER_2 = "Runner2"
RUNNER_3 = "Runner3"
FOCUS_TARGET = "FocusTarget"
FRONT_CAM = "FrontCam"

def define_movie():
    """Define 100m sprint with tracking camera"""
    
    movie = MovieBuilder("Sprint With Camera Track", fps=60)
    
    # Configuration
    race_distance = 300  # Increased for longer duration
    target_duration = 30.0 # seconds (Finish time)
    r2_delay = 5.0         # seconds
    
    # NEW: Height Variables
    # Use Belica as reference
    char_data = Characters.BELICA
    char_height = char_data.height      # meters
    marker_height = char_height * 100    # cm
    
    # Calculate speeds for synchronized finish
    r1_speed = race_distance / target_duration
    r2_run_duration = target_duration - r2_delay
    
    if r2_run_duration <= 0:
        raise ValueError("Runner 2 cannot catch up! Delay is too long relative to target duration.")

    # Add runners with explicit mesh path
    # belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    
    # Runner 1 - Lane 3 (Y=305cm from center)
    movie.add_actor(RUNNER_1, location=(0, 0, 0), yaw_offset=char_data.initial_yaw, mesh_path=char_data.path, height=char_height)

    with movie.for_actor(RUNNER_1) as r1:
        r1.face(Direction.NORTH)
        r1.move_straight() \
            .direction(Direction.NORTH) \
            .anim("Jog_Fwd") \
            .distance_at_speed((DistanceUnit.Meters, race_distance), (SpeedUnit.MetersPerSecond, r1_speed))
        r1.stay().till_end().anim("Idle")
        
    movie.add_actor(RUNNER_2, location=(0, -50, 0), yaw_offset=char_data.initial_yaw, mesh_path=char_data.path, height=char_height)
    
    with movie.for_actor(RUNNER_2) as r2:
        # Idle for delay
        r2.stay().for_time(r2_delay).anim("Idle")

        r2.face(Direction.NORTH)

        # Start running (Sprint) to finish at same time
        r2.move_straight().direction(Direction.NORTH) \
            .anim("Jog_Fwd") \
            .distance_in_time((DistanceUnit.Meters, race_distance), r2_run_duration)
            
        r2.stay().till_end().anim("Idle")

    # Runner 3 - Lane 1 (Y=50cm)
    char_3_data = Characters.PIA
    movie.add_actor(RUNNER_3, location=(0, 50, 0), yaw_offset=char_3_data.initial_yaw, mesh_path=char_3_data.path, height=char_3_data.height)
    
    with movie.for_actor(RUNNER_3) as r3:
        # Simple run, start immediately (slower jog?)
        # Let's match Runner 1 timing for simplicity but with the new animation
        r3.face(Direction.NORTH)
        r3.move_straight().direction(Direction.NORTH) \
            .anim(Animations.PIA_JOG_FWD) \
            .distance_at_speed((DistanceUnit.Meters, race_distance), (SpeedUnit.MetersPerSecond, r1_speed))
        r3.stay().till_end().anim("Idle")
    
    
    # Focus Target (Midpoint Tracker)
    # Using new GroupTarget API to automatically track midpoint of runners
    movie.add_group_target(FOCUS_TARGET, members=[RUNNER_1, RUNNER_2, RUNNER_3], location=(0, -25, 0)) \
         .color("Blue") \
         .shape("Cylinder") \
         .height(marker_height) \
         .radius(10) \
         .interval(500)
    
    movie.add_camera(FRONT_CAM, location=(35000, -50, 200)) \
         .look_at_subject(RUNNER_1, height_pct=0.85) \
         .debug_visible(True) \
         .add()
    
    # Camera cuts
    movie.at_time(0).camera_cut(FRONT_CAM)
    
    # Helper for pan sequence
    def pan_runner(cam, runner_name, duration=5.0):
        """Pan up and down on a runner"""
        # Head -> Feet (2.5s)
        cam.focus_zoom_track(runner_name, focus_pct=0.85, zoom_pct=0.85, track_pct=0.85)
        cam.wait(duration/2)
        # Feet -> Head (2.5s)
        cam.focus_zoom_track(runner_name, focus_pct=0.15, zoom_pct=0.85, track_pct=0.15)
        cam.wait(duration/2)

    # Camera commands (Choreographed Sequence)
    # Total duration: 25s (5s x 5 stages)
    with movie.for_camera(FRONT_CAM) as cam:
        # 1. Track Runner 1 (5s)
        cam.focus_zoom_track(RUNNER_1, focus_pct=0.85, zoom_pct=0.85, track_pct=0.85)
        cam.wait(5.0)
        
        # 2. Track Runner 2 (5s)
        cam.focus_zoom_track(RUNNER_2, focus_pct=0.85, zoom_pct=0.85, track_pct=0.85)
        cam.wait(5.0)
        
        # 3. Pan Runner 1 (5s)
        pan_runner(cam, RUNNER_1, duration=5.0)
        
        # 4. Pan Runner 2 (5s)
        pan_runner(cam, RUNNER_2, duration=5.0)
        
        # 5. Track Both (FocusTarget) (5s)
        # cam.focus_zoom_track(FOCUS_TARGET, focus_pct=0.0, zoom_pct=0.9, track_pct=0.0) # Height irrelevant for marker
        # cam.wait(5.0)
        
        # Hold remaining time
        cam.wait(max(0, target_duration - 25.0))
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
