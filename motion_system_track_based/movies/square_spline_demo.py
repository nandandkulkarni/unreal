import sys
import os
import math

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from motion_builder import MovieBuilder

def build_square_demo():
    print("Building Square Spline Demo with Motion Matching...")
    
    # 1. Define Square Points (10m x 10m)
    # Center at 0,0
    half_size = 500.0 # 500cm = 5m
    height = 0.0 # On ground
    
    # Order: Bottom-Left -> Top-Left -> Top-Right -> Bottom-Right -> Close
    points = [
        (-half_size, -half_size, height),
        ( half_size, -half_size, height),
        ( half_size,  half_size, height),
        (-half_size,  half_size, height)
    ]
    
    with MovieBuilder("SquareSplineDemo", fps=30) as movie:
        
        # 2. Add the Spline
        # Closed loop, Linear tension (sharp corners?) or standard Catmull-Rom
        # For a true square with sharp corners, splines are tricky unless points are doubled up.
        # But we'll just use a low tension for now.
        movie.add_spline("SquarePath", points=points, closed=True) \
             .color("Red") \
             .thickness(5.0) \
             .tension(0.0) # 0.0 = sharp/linear lines usually implies less curve
             
        # 3. Add Character
        movie.add_actor("Runner", location=(-half_size, -half_size, height))
        
        # 4. Command Character to run along spline using Motion Matching
        with movie.for_actor("Runner") as actor:
            actor.move_along_spline("SquarePath") \
                 .speed(4.0) \
                 .use_motion_match() \
                 .run()
                 
        # 5. Add Camera
        movie.add_camera("Cam1", location=(0, -800, 600), fov=90).add()
        with movie.for_camera("Cam1") as cam:
            cam.look_at_subject("Runner")
            cam.wait(10.0) # Watch for 10 seconds (approx full loop at 4m/s for 40m path)

        # 6. Save and Run
        output_dir = os.path.join(os.path.dirname(current_dir), "dist")
        movie.save_to_tracks(output_dir)
        movie.run(to_unreal=True)

    print("Square Spline Demo Build Complete!")
    print(f"Output saved to: {output_dir}/SquareSplineDemo")

if __name__ == "__main__":
    build_square_demo()
