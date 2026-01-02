
"""
Test Lights Scene
Verifies the Light API implementation with Enums and chaining.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, LightColor, LightUnit

def define_movie():
    movie = MovieBuilder("Test Lights API", fps=60)
    
    # Floor for shadows
    # movie.add_floor("Floor", scale=1000) # Assuming add_floor works or we use Mannequin on ground
    
    # 1. Directional Light (Moonlight)
    movie.add_light_directional("Moon") \
         .intensity(2.0) \
         .color(LightColor.MOONLIGHT) \
         .rotation(pitch=-45, yaw=45, roll=0)
         
    # 2. Point Light (Warm lamp nearby)
    movie.add_light_point("Lamp", location=(100, 100, 200)) \
         .intensity(2000, LightUnit.LUMENS) \
         .color(LightColor.WARM_WHITE) \
         .radius(800) \
         .cast_shadows(True)
         
    # 3. Spot Light (Cyan spotlight on actor)
    movie.add_light_spot("Spot", location=(-200, 0, 300)) \
         .intensity(5000, LightUnit.CANDELAS) \
         .color((0.0, 1.0, 1.0)) \
         .cone(inner=20, outer=40) \
         .rotation(pitch=-60, yaw=0, roll=0) # Pointing down-ish

    # Actor to receive light
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Mannequin", location=(0, 0, 0), mesh_path=belica_path)
    
    # Camera
    movie.add_camera("Cam", location=(300, -300, 200)).look_at("Mannequin").add()
    movie.at_time(0).camera_cut("Cam")

    # Simple actor stay
    with movie.for_actor("Mannequin") as m:
        m.stay().for_time(5.0).anim("Idle")
        
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
