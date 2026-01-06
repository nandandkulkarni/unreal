"""Mid Afternoon - Bright sun, clear skies, minimal fog"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("Mid Afternoon", fps=30)
    
    # Clear afternoon atmosphere - very light fog, warm tones
    movie.add_atmosphere(
        fog_density="clear",
        fog_color=(1.0, 0.95, 0.85),  # Warm clear atmosphere
        volumetric=True,
        volumetric_scattering=0.5,
        volumetric_albedo=(1.0, 0.98, 0.95),
        fog_height_falloff=0.3
    )
    
    # Bright overhead sun
    movie.add_light_directional("AfternoonSun")\
        .rotation(pitch=-60, yaw=135)\
        .intensity(10.0)\
        .color((1.0, 0.95, 0.9))\
        .use_as_atmospheric_sun(True)\
        .cast_volumetric_shadow(True)
    
    # Add visual sun sphere high in the sky
    sphere_path = "/Engine/BasicShapes/Sphere.Sphere"
    movie.add_actor("Sun", location=(-8000, -8000, 15000), mesh_path=sphere_path)
    
    # Character walking casually
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Walker", location=(-1000, 0, 0), yaw_offset=-90, mesh_path=belica_path)
    
    with movie.for_actor("Walker") as walker:
        walker.stay().anim("Idle").for_time(1.0)
        walker.move_straight().anim("Walk_Fwd").direction(Direction.EAST).distance_at_speed(2500.0, 2.5)
        walker.stay().anim("Idle").for_time(0.5)
        walker.move_straight().anim("Walk_Fwd").direction(Direction.NORTH).distance_at_speed(1500.0, 2.5)
        walker.stay().anim("Idle").for_time(1.0)
    
    # Close follow camera
    movie.add_camera("FollowCam", location=(500, -300, 180), fov=75)\
         .look_at_subject("Walker", height_pct=0.65)\
         .add()
    
    with movie.for_camera("FollowCam") as cam:
        cam.wait(15.0)
    
    movie.at_time(0.0).camera_cut("FollowCam")
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
