"""
400m Dash Race - Movie Definition

6 runners with staggered starts, lane adherence for first 100m,
then breaking to inside lane.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

# Runner names
RUNNER1 = "Runner1"
RUNNER2 = "Runner2"
RUNNER3 = "Runner3"
RUNNER4 = "Runner4"
RUNNER5 = "Runner5"
RUNNER6 = "Runner6"

# Track constants (in meters)
LANE_WIDTH = 1.22
STRAIGHT_LENGTH = 84.39
CURVE_RADIUS = 36.5

# Staggered start offsets (in meters) for fair 400m race
# Outer lanes start ahead to compensate for longer curve distance
STAGGER_OFFSETS = [
    0.0,    # Lane 1 (inside)
    7.04,   # Lane 2
    14.68,  # Lane 3
    22.85,  # Lane 4
    31.52,  # Lane 5
    40.70   # Lane 6 (outside)
]

def define_movie():
    """Define 400m dash choreography"""
    
    with MovieBuilder("400m Dash Race", create_new_level=True, fps=60) as movie:
        
        # Environment setup
        movie.delete_lights(["DirectionalLight", "SkyLight"])
        movie.delete_all_floors()
        movie.add_floor("Track", location=(0, 0, -0.5), scale=3000)
        movie.add_directional_light("SunLight", direction_from="east", angle="high", 
                                   intensity="bright", color="white", atmosphere_sun=True)
        
        # Add 6 runners with staggered starts
        runners = [RUNNER1, RUNNER2, RUNNER3, RUNNER4, RUNNER5, RUNNER6]
        
        for i, runner_name in enumerate(runners):
            lane_y = i * LANE_WIDTH * 100  # Convert to cm for Unreal
            start_x = -STAGGER_OFFSETS[i] * 100  # Convert to cm, negative for behind start line
            
            movie.add_actor(
                runner_name,
                location=(start_x, lane_y, 0),
                yaw_offset=0,  # Facing forward (+X)
                mesh_path="/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
            )
        
        # Race choreography - all runners move simultaneously
        with movie.simultaneous() as group:
            
            for i, runner_name in enumerate(runners):
                with group.for_actor(runner_name) as runner:
                    # Sprint animation
                    runner.animation("Sprint_Fwd")
                    
                    # Phase 1: Stay in lane for first 100m (acceleration phase)
                    # Speed profile: 0 → 9.5-10.0 m/s
                    runner.move_for_seconds(
                        seconds=10.5,  # ~10.5s to cover 100m with acceleration
                        direction="forward",
                        speed_mtps=9.5 + (i * 0.1),  # Slight speed variation
                        acceleration=3.0  # 3 m/s² acceleration
                    )
                    
                    # Phase 2: Break to inside lane (lane 1)
                    # Gradual move from current lane to lane 1
                    if i > 0:  # Lane 1 is already inside
                        target_y = 0  # Lane 1 position
                        current_x = 100 * 100  # 100m in cm
                        
                        # Move diagonally to inside lane while continuing forward
                        runner.move_to_location(
                            target=(current_x + 5000, target_y, 0),  # 50m forward while moving in
                            speed_mtps=9.5 + (i * 0.1)
                        )
                    
                    # Phase 3: Continue on inside lane to finish (remaining ~250m)
                    runner.move_for_seconds(
                        seconds=26,  # ~26s for remaining 250m at 9.5 m/s
                        direction="forward",
                        speed_mtps=9.5 + (i * 0.1)
                    )
        
        # Camera setup
        movie.add_camera(
            "StartCam",
            location=(-1000, 300, 200),
            rotation=(0, 0, 0),
            fov=70,
            look_at_actor=f"{RUNNER1}, {RUNNER2}, {RUNNER3}, {RUNNER4}, {RUNNER5}, {RUNNER6}",
            offset=(0, 0, 100)
        )
        
        movie.add_camera(
            "FinishCam",
            location=(40000, 0, 200),  # 400m mark
            rotation=(0, 180, 0),
            fov=70
        )
        
        # Camera cuts
        movie.at_time(0.0).camera_cut("StartCam")
        movie.at_time(35.0).camera_cut("FinishCam")
    
    return movie.build()


# Export movie data
MOVIE = define_movie()


if __name__ == "__main__":
    # Print movie summary
    print("400m Dash Race - Movie Definition")
    print("=" * 60)
    print(f"Runners: 6")
    print(f"FPS: {MOVIE['fps']}")
    print(f"Commands: {len(MOVIE['plan'])}")
    print()
    print("Staggered Starts:")
    for i, offset in enumerate(STAGGER_OFFSETS):
        print(f"  Lane {i+1}: {offset:.2f}m ahead")
    print()
    print("Race Phases:")
    print("  1. 0-100m: Stay in lane (acceleration)")
    print("  2. 100-150m: Break to inside lane")
    print("  3. 150-400m: Sprint to finish on inside lane")
