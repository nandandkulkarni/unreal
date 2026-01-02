"""
Simple 100m Walk with Attached Side Camera
Person moves 100 meters with a camera attached at face level.
No animations - just transform movement.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("100m Side Camera", fps=60)
    
    # Person starting at origin
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Person", location=(0, 0, 0), mesh_path=belica_path)
    
    # Camera attached to person, on their side at face level
    # Offset: 100cm to the right (Y), face height ~160cm (Z)
    movie.add_camera("SideCam", location=(0, 100, 160)) \
         .attach_to("Person") \
         .rotation((0, 0, -90)) \
         .add()
    
    # Camera cut to side cam
    movie.at_time(0).camera_cut("SideCam")
    
    # Person moves 100 meters forward (no animation)
    with movie.for_actor("Person") as p:
        p.face(Direction.NORTH)
        p.move_straight() \
            .direction(Direction.FORWARD) \
            .distance_in_time(100, 10)  # 100 meters in 10 seconds
        
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
