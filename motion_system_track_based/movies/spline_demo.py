import sys
import os

# Helper to ensure paths are reachable if running directly from Editor
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add parent directory (motion_system_track_based) to sys.path
sys.path.append(os.path.dirname(current_dir))

try:
    import unreal
except ImportError:
    print("This script must be run inside Unreal Engine to use Motion Matching.")
    sys.exit(1)

from motion_builder import MovieBuilder, Direction

def build_demo():
    print("Building Spline Demo Movie...")
    
    # 3D Mountain Path (Points in cm)
    # Scaled up for visibility and movement duration
    points = [
        (0, 0, 0),          # Start
        (500, 0, 0),        # 5m Flat Run
        (1000, 0, 200),     # 5m Uphill (Rise 2m) -> Slope ~21 deg
        (1500, 0, 200),     # 5m Flat at height
        (2000, 0, 600),     # 5m Steep Climb (Rise 4m) -> Slope ~38 deg
        (2500, 0, 600),     # 5m Flat Summit
        (3000, 0, 0)        # 5m Steep Descent
    ]

    with MovieBuilder("SplineDemo", fps=30) as movie:
        # Define Spline
        movie.add_spline("MountainPath", points=points, closed=False) \
             .color("Red") \
             .thickness(10.0) \
             .tension(0.5)

        # Add Actor
        movie.add_actor("Climber", location=(0,0,0))
        
        # Add a Camera to follow
        movie.add_camera("FollowCam", location=(-300, -300, 100))
        with movie.for_camera("FollowCam") as cam:
            cam.look_at("Climber")

        # Command Actor
        with movie.for_actor("Climber") as actor:
            # Move along the spline using Motion Matching to pick animations
            # Speed 300 cm/s = 3 m/s (Jog)
            actor.move_along_spline("MountainPath") \
                 .speed(3.0) \
                 .use_motion_match() \
                 .run()

        # Save output
        # Output to dist/ relative to project root usually
        output_dir = os.path.join(os.path.dirname(current_dir), "dist")
        movie.save_to_tracks(output_dir)
        
    print("Spline Demo Build Complete!")
    print(f"Output saved to: {output_dir}/SplineDemo")

if __name__ == "__main__":
    build_demo()
