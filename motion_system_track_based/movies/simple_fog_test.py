"""
Simple Fog Test - No actors, just atmosphere
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

def define_movie():
    movie = MovieBuilder("Simple Fog Test", fps=30)
    
    # Just add fog
    movie.add_atmosphere(
        fog_density="medium",
        fog_color="blue",
        fog_height_falloff=0.2,
        volumetric=True,
        volumetric_scattering=1.0
    )
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
