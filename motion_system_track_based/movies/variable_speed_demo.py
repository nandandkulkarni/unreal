import sys
import os

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from motion_builder import MovieBuilder

def build_variable_speed_demo():
    print("Building Variable Speed Demo...")
    
    # Create 4 separate paths for 4 different speeds
    # Each path is 5 meters long
    
    with MovieBuilder("VariableSpeedDemo", fps=30) as movie:
        
        # Path 1: Walk speed test (1.5 m/s)
        movie.add_spline("Path1", points=[(0, 0, 0), (500, 0, 0)], closed=False) \
             .color("Green") \
             .thickness(3.0)
        
        # Path 2: Medium speed test (2.5 m/s)
        movie.add_spline("Path2", points=[(0, -200, 0), (500, -200, 0)], closed=False) \
             .color("Yellow") \
             .thickness(3.0)
        
        # Path 3: Jog speed test (3.5 m/s)
        movie.add_spline("Path3", points=[(0, -400, 0), (500, -400, 0)], closed=False) \
             .color("Orange") \
             .thickness(3.0)
        
        # Path 4: Fast jog test (4.5 m/s)
        movie.add_spline("Path4", points=[(0, -600, 0), (500, -600, 0)], closed=False) \
             .color("Red") \
             .thickness(3.0)
             
        # Runner 1: Walk speed (1.5 m/s) - Should use walk animation
        movie.add_actor("Walker", location=(0, 0, 0))
        with movie.for_actor("Walker") as actor:
            actor.move_along_spline("Path1") \
                 .speed(1.5) \
                 .use_motion_match() \
                 .run()
        
        # Runner 2: Medium speed (2.5 m/s)
        movie.add_actor("MediumRunner", location=(0, -200, 0))
        with movie.for_actor("MediumRunner") as actor:
            actor.move_along_spline("Path2") \
                 .speed(2.5) \
                 .use_motion_match() \
                 .run()
        
        # Runner 3: Jog speed (3.5 m/s) - Should use jog animation
        movie.add_actor("Jogger", location=(0, -400, 0))
        with movie.for_actor("Jogger") as actor:
            actor.move_along_spline("Path3") \
                 .speed(3.5) \
                 .use_motion_match() \
                 .run()
        
        # Runner 4: Fast jog (4.5 m/s)
        movie.add_actor("FastJogger", location=(0, -600, 0))
        with movie.for_actor("FastJogger") as actor:
            actor.move_along_spline("Path4") \
                 .speed(4.5) \
                 .use_motion_match() \
                 .run()
                 
        # Add Camera - positioned to see all 4 runners
        movie.add_camera("Cam1", location=(250, -1200, 600), fov=90).add()
        with movie.for_camera("Cam1") as cam:
            cam.look_at_subject("Jogger")  # Focus on middle runner
            cam.wait(10.0)

        # Save and Run
        output_dir = os.path.join(os.path.dirname(current_dir), "dist")
        movie.save_to_tracks(output_dir)
        movie.run(to_unreal=True)

    print("Variable Speed Demo Build Complete!")
    print(f"Output saved to: {output_dir}/VariableSpeedDemo")
    print("\nSpeed Test:")
    print("  Green path  (top):    1.5 m/s - Walk")
    print("  Yellow path:          2.5 m/s - Medium")
    print("  Orange path:          3.5 m/s - Jog")
    print("  Red path    (bottom): 4.5 m/s - Fast Jog")

if __name__ == "__main__":
    build_variable_speed_demo()
