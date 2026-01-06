import sys
import os
import math

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from motion_builder import MovieBuilder

def build_circle_demo():
    print("Building Circular Spline Demo...")
    
    # Generate Circle Points
    radius = 500.0 # 5 meters
    height = 200.0 # 2 meters up
    num_points = 16
    points = []
    
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y, height))
    
    # Create the movie
    with MovieBuilder("CircularSplineDemo", fps=30) as movie:
        
        # Add the Spline
        movie.add_spline("CirclePath", points=points, closed=True) \
             .color("Green") \
             .thickness(10.0) \
             .tension(0.5)
             
        # Add a Camera to see it
        # Positioned back and up
        movie.add_camera("OverviewCam", location=(-1000, 0, 800), fov=90).add()
        with movie.for_camera("OverviewCam") as cam:
            cam.look_at_subject("CirclePath") # Will look at origin/root of spline actor
            cam.wait(5.0) # Just hold for 5 seconds

        # Save output
        output_dir = os.path.join(os.path.dirname(current_dir), "dist")
        movie.save_to_tracks(output_dir)
        
        # Trigger execution in Unreal
        movie.run(to_unreal=True)
        
    print("Circular Spline Demo Build Complete!")
    print(f"Output saved to: {output_dir}/CircularSplineDemo")

if __name__ == "__main__":
    build_circle_demo()
