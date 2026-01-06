"""
Twilight Atmosphere Demo

A serene twilight scene showcasing:
- Cool blue/purple atmospheric fog
- Fading sun near horizon with subtle god rays
- Volumetric atmospheric scattering
- Transition to night
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("Twilight Atmosphere", fps=30)
    
    # Cool twilight fog with blue/purple tones
    movie.add_atmosphere(
        fog_density="medium",
        fog_color="blue",
        fog_height_falloff=0.25,
        volumetric=True,
        volumetric_scattering=1.5,
        fog_max_opacity=0.85
    )
    
    # Fading sun near horizon with cool twilight color
    movie.add_light_directional("TwilightSun")\
        .rotation(pitch=-5, yaw=180)\
        .intensity(3.0)\
        .color((0.8, 0.6, 0.7))\
        .use_as_atmospheric_sun(True)\
        .cast_volumetric_shadow(True)\
        .light_shafts(bloom_scale=0.4, enable_occlusion=True)
    
    # Dominant sky light for twilight ambiance
    movie.add_light_directional("SkyTwilight")\
        .rotation(pitch=60, yaw=90)\
        .intensity(4.0)\
        .color((0.3, 0.4, 0.7))\
        .cast_shadows(False)
    
    # Add a wanderer silhouette
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Wanderer", location=(0, 0, 0), yaw_offset=90, mesh_path=belica_path)
    
    with movie.for_actor("Wanderer") as wanderer:
        # Walk toward the sunset (toward X+)
        wanderer.move_straight().anim("Walk_Fwd").direction(Direction.EAST).distance_at_speed(1000.0, 0.8)
        wanderer.stay().anim("Idle").for_time(3.0)
    
    # Camera positioned behind wanderer, looking toward sunset at X+
    movie.add_camera("SunsetCam", location=(-600, -300, 120), fov=75)\
         .look_at_subject("Wanderer", height_pct=0.6)\
         .add()
    
    with movie.for_camera("SunsetCam") as cam:
        cam.auto_focus_subject("Wanderer", height_pct=0.6)
        cam.wait(22.0)
    
    movie.at_time(0.0).camera_cut("SunsetCam")
    
    # Transition fog to deeper purple (twilight to night)
    movie.animate_fog(
        target_color="purple",
        duration=10.0
    )
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
