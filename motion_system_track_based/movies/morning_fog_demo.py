"""
Atmospheric Demo - Morning Fog Dissipation with God Rays

Demonstrates:
- Exponential height fog with volumetric effects
- Directional light with god rays
- Animated fog dissipation over time
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("Morning Fog Demo", fps=30)
    
    # Add atmospheric fog
    movie.add_atmosphere(
        fog_density="heavy",
        fog_color="atmospheric",
        volumetric=True,
        volumetric_scattering=1.5
    )
    
    # Add sun with god rays
    movie.add_light_directional("SunLight")\
        .rotation(pitch=-15, yaw=90)\
        .intensity(8.0)\
        .color((1.0, 0.85, 0.7))\
        .use_as_atmospheric_sun(True)\
        .cast_volumetric_shadow(True)\
        .light_shafts("cinematic")
    
    # Add a character to walk through the fog
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Walker", location=(0, 0, 0), yaw_offset=-90, mesh_path=belica_path)
    
    with movie.for_actor("Walker") as walker:
        walker.stay().anim("Idle").for_time(2.0)
        walker.move_straight().anim("Walk_Fwd").direction(Direction.NORTH).distance_at_speed(2000.0, 2.0)
        walker.stay().anim("Idle").for_time(2.0)
    
    # Add camera to observe
    movie.add_camera("MainCam", location=(1000, -800, 200), fov=75)\
         .look_at_subject("Walker", height_pct=0.6)\
         .add()
    
    with movie.for_camera("MainCam") as cam:
        cam.wait(12.0)
    
    # Camera cut
    movie.at_time(0.0).camera_cut("MainCam")
    
    # Animate fog dissipation after 3 seconds
    movie.animate_fog(
        target_density="light",
        duration=8.0
    )
    
    return movie


if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
