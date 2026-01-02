"""
Test Attached Camera Scene
Verifies the attach_to() API with a camera attached to a moving actor.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, LightColor

def define_movie():
    movie = MovieBuilder("Test Attached Camera", fps=60)
    
    # 1. Main character who will move
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Runner", location=(0, 0, 0), mesh_path=belica_path)
    
    # 2. Camera attached to character (follows automatically)
    movie.add_camera("HeadCam", location=(0, 0, 50)) \
         .attach_to("Runner", socket="head") \
         .add()
    
    # 3. Spotlight on character's hand socket
    movie.add_light_spot("HandLight", location=(0, 0, 0)) \
         .attach_to("Runner", socket="hand_r") \
         .intensity(2000) \
         .color(LightColor.WARM_WHITE) \
         .radius(500)
    
    # 4. Static overview camera (not attached)
    movie.add_camera("Overview", location=(500, -500, 300)) \
         .look_at("Runner") \
         .add()
    
    # Camera cuts
    movie.at_time(0).camera_cut("HeadCam")  # Start with attached camera
    movie.at_time(3).camera_cut("Overview")  # Switch to overview
    
    # Actor movement
    with movie.for_actor("Runner") as r:
        r.face(Direction.NORTH)
        r.move_straight() \
            .direction(Direction.FORWARD) \
            .anim("Jog_Fwd") \
            .distance_at_speed(20, 3)  # 20 meters at 3 m/s
        r.stay().for_time(2.0).anim("Idle")
        
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
