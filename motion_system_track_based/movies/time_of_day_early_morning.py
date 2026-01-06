"""Early Morning - Soft dawn light with misty fog"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("Early Morning", fps=30)
    
    # Early morning atmosphere - light fog, cool blue tones
    movie.add_atmosphere(
        fog_density="light",
        fog_color=(0.7, 0.8, 1.0),  # Cool blue morning fog
        volumetric=True,
        volumetric_scattering=1.0,
        volumetric_albedo=(0.9, 0.95, 1.0),  # Slight blue tint
        fog_height_falloff=0.15
    )
    
    # Soft dawn sun - low angle, cool color
    movie.add_light_directional("DawnSun")\
        .rotation(pitch=-10, yaw=90)\
        .intensity(5.0)\
        .color((1.0, 0.9, 0.85))\
        .use_as_atmospheric_sun(True)\
        .cast_volumetric_shadow(True)
    
    # Add visual sun sphere in the sky
    sphere_path = "/Engine/BasicShapes/Sphere.Sphere"
    movie.add_actor("Sun", location=(15000, 0, -2500), mesh_path=sphere_path)
    
    # Character doing morning jog
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Runner", location=(0, 0, 0), yaw_offset=-90, mesh_path=belica_path)
    
    with movie.for_actor("Runner") as runner:
        runner.stay().anim("Idle").for_time(1.0)
        runner.move_straight().anim("Jog_Fwd").direction(Direction.NORTH).distance_at_speed(3000.0, 4.0)
        runner.stay().anim("Idle").for_time(1.0)
    
    # Wide tracking camera
    movie.add_camera("MainCam", location=(1500, -1000, 250), fov=80)\
         .look_at_subject("Runner", height_pct=0.6)\
         .add()
    
    with movie.for_camera("MainCam") as cam:
        cam.wait(12.0)
    
    movie.at_time(0.0).camera_cut("MainCam")
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
