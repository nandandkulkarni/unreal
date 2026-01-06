"""
Mystical Forest Demo

Demonstrates:
- Dense mystical fog with greenish tint
- Strong height falloff for ground fog effect
- Animated fog color transition
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("Mystical Forest", fps=30)
    
    # Mystical ground fog
    movie.add_atmosphere(
        fog_density="medium",
        fog_color="mystical",
        fog_height_falloff=0.5,  # Strong falloff for ground fog
        volumetric=True,
        volumetric_scattering=1.2
    )
    
    # Moonlight through trees
    movie.add_light_directional("Moonlight")\
        .rotation(pitch=-60, yaw=0)\
        .intensity(8.0)\
        .color((0.6, 0.7, 1.0))\
        .use_as_atmospheric_sun(True)\
        .cast_volumetric_shadow(True)\
        .light_shafts("subtle")
    
    # Wanderer character
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Wanderer", location=(-1000, 0, 0), yaw_offset=-90, mesh_path=belica_path)
    
    with movie.for_actor("Wanderer") as wanderer:
        wanderer.move_straight().anim("Walk_Fwd").direction(Direction.EAST).distance_at_speed(3000.0, 1.5)
        wanderer.stay().anim("Idle").for_time(2.0)
    
    # Following camera
    movie.add_camera("FollowCam", location=(-500, -600, 150), fov=70)\
         .look_at_subject("Wanderer", height_pct=0.7)\
         .add()
    
    with movie.for_camera("FollowCam") as cam:
        cam.auto_focus_subject("Wanderer", height_pct=0.7)
        cam.wait(22.0)
    
    movie.at_time(0.0).camera_cut("FollowCam")
    
    # Transition fog to forest green
    movie.animate_fog(
        target_color="forest",
        duration=6.0
    )
    
    return movie


if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
