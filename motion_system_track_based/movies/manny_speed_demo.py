import sys
import os

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from motion_builder import MovieBuilder

# ============================================================================
# ANIMATION DATABASE CONFIGURATION
# ============================================================================
# Specify which animation database to use for motion matching
# Now using the specialized Unarmed database
ANIM_DB = "manny_unarmed"

def build_manny_speed_demo():
    print("Building Manny Variable Speed Demo (Unarmed)...")
    
    with MovieBuilder("MannySpeedDemo", fps=30) as movie:
        
        # Single long path for variable speed test
        # We will change speed dynamically along the path? 
        # The current system sets speed PER SEGMENT.
        # So we can chain multiple move commands on the same spline? NO, one move command per spline.
        # But we can split the spline into sections?
        # OR we can just keep the parallel tracks but just spawn ONE character actor and have him run one track.
        # But the point of speed demo is to see different speeds.
        # Let's keep the parallel tracks for now but use the new DB.
        # User said "Lets just use one character". Maybe implies just one TYPE of character?
        # "Lets just use one character" singular.
        # I will interpret this as ONE SINGLE ACTOR in the scene.
        # So I will make him run at different speeds sequentially?
        # Or just pick one speed?
        # "use that db in the speed demo"
        # I'll make a single path that loops or zig-zags and changes speed?
        # SplineMotionCommandBuilder sets speed for the whole move.
        # To change speed, we need multiple move commands.
        # Can we chain move commands on the SAME spline?
        # "actor.move_along_spline(Path1).speed(1.5)... .run()"
        # If we run again, does it continue?
        # The current implementation of move_along_spline takes start/end distance.
        # So we CAN chain them!
        
        path_name = "VariableSpeedPath"
        movie.add_spline(path_name, points=[
            (0, 0, 0),    (400, 0, 0),    # Leg 1
            (400, 400, 0), (0, 400, 0),   # Leg 2 & 3
            (0, 0, 0)                     # Leg 4 (Loop)
        ], closed=True).color("Cyan")
        
        movie.add_actor("Manny", location=(0, 0, 0), mesh_path="/Game/Characters/Mannequins/Meshes/SKM_Manny")
        
        with movie.for_actor("Manny") as actor:
            # Walk (1.5 m/s) - First Leg
            actor.move_along_spline(path_name) \
                 .range(0, 400) \
                 .speed(1.5) \
                 .use_motion_match(anim_db=ANIM_DB) \
                 .run()
                 
            # Jog (3.5 m/s) - Second Leg
            actor.move_along_spline(path_name) \
                 .range(400, 800) \
                 .speed(3.5) \
                 .use_motion_match(anim_db=ANIM_DB) \
                 .run()
                 
            # Segment 3: Fast Run (6.0 m/s)
            # 10m segment
            actor.move_along_spline(path_name) \
                 .range(800, 1200) \
                 .speed(6.0) \
                 .use_motion_match(anim_db=ANIM_DB) \
                 .run()
                 
            # Slow Walk (1.0 m/s) - Fourth Leg
            actor.move_along_spline(path_name) \
                 .range(1200, 1600) \
                 .speed(1.0) \
                 .use_motion_match(anim_db=ANIM_DB) \
                 .run()
                 
        # Camera
        movie.add_camera("Cam1", location=(600, 600, 800), fov=90).add()
        with movie.for_camera("Cam1") as cam:
            cam.look_at_subject("Manny")
            cam.wait(20.0)

        # Save and Run
        output_dir = os.path.join(os.path.dirname(current_dir), "dist")
        movie.save_to_tracks(output_dir)
        movie.run(to_unreal=True)
    
    print("Manny Unarmed Demo Build Complete!")
    print(f"Output saved to: {output_dir}/MannySpeedDemo")

if __name__ == "__main__":
    build_manny_speed_demo()
