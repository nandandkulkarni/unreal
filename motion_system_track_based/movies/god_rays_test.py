"""
Simple God Rays Test - Directional light with volumetric shadows and light shafts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, LightType

def define_movie():
    movie = MovieBuilder("God Rays Test", fps=30)
    
    # Add fog for volumetric effects
    movie.add_atmosphere(
        fog_density="light",
        fog_color="white",
        volumetric=True,
        volumetric_scattering=1.5
    )
    
    # Add directional light with god rays
    movie.add_light_directional("SunLight")\
        .rotation(pitch=-45, yaw=45)\
        .intensity(10.0)\
        .color((1.0, 0.95, 0.85))\
        .use_as_atmospheric_sun(True)\
        .cast_volumetric_shadow(True)\
        .light_shafts(bloom_scale=0.5, enable_occlusion=True)
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
