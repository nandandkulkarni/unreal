import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motion_builder import MovieBuilder

def define_movie():
    # Create movie with 60fps
    movie = MovieBuilder("SimpleMannequinTest_V2", fps=60)
    
    # Add a single actor
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("MyMannequin_01", location=(0, 0, 0), mesh_path=belica_path)
    
    # Add a camera
    movie.add_camera("Camera", location=(200, 0, 100)).add()
    
    with movie.for_camera("Camera") as cam:
        cam.look_at("MyMannequin_01")
    
    # Define simple behavior (just stay)
    with movie.for_actor("MyMannequin_01") as m:
        m.stay().for_time(5.0).anim("Idle")
        
    # Add initial camera cut
    movie.at_time(0).camera_cut("Camera")
        
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
