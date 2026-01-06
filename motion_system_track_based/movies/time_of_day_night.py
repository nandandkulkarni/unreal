"""Night - Moonlight with dark blue atmosphere"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("Night", fps=30)
    
    # Night atmosphere - light fog, cool blue/purple tones
    movie.add_atmosphere(
        fog_density="light",
        fog_color=(0.3, 0.4, 0.7),  # Cool blue/purple night fog
        volumetric=True,
        volumetric_scattering=1.2,
        volumetric_albedo=(0.6, 0.65, 0.8),  # Cool moonlight scatter
        fog_height_falloff=0.2
    )
    
    # Moonlight - cool, dim
    movie.add_light_directional("Moonlight")\
        .rotation(pitch=-45, yaw=200)\
        .intensity(3.0)\
        .color((0.7, 0.8, 1.0))\
        .use_as_atmospheric_sun(True)\
        .cast_volumetric_shadow(True)
    
    # Add visual moon sphere in the sky
    sphere_path = "/Engine/BasicShapes/Sphere.Sphere"
    movie.add_actor("Moon", location=(-10000, 12000, 12000), mesh_path=sphere_path)
    
    # Character moving stealthily at night
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("NightWalker", location=(0, 0, 0), yaw_offset=-45, mesh_path=belica_path)
    
    with movie.for_actor("NightWalker") as walker:
        walker.stay().anim("Idle").for_time(1.0)
        walker.move_straight().anim("Walk_Fwd").direction(Direction.NORTH_EAST).distance_at_speed(2000.0, 1.8)
        walker.stay().anim("Idle").for_time(0.5)
        walker.move_straight().anim("Walk_Fwd").direction(Direction.SOUTH_EAST).distance_at_speed(1800.0, 1.8)
        walker.stay().anim("Idle").for_time(2.0)
    
    # Atmospheric wide shot
    movie.add_camera("NightCam", location=(1200, -1200, 300), fov=85)\
         .look_at_subject("NightWalker", height_pct=0.6)\
         .add()
    
    with movie.for_camera("NightCam") as cam:
        cam.wait(14.0)
    
    movie.at_time(0.0).camera_cut("NightCam")
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
