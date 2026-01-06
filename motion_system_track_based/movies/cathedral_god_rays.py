"""
Cathedral God Rays Demo

Demonstrates:
- Light atmosphere with volumetric fog
- Multiple light sources with dramatic god rays
- Indoor lighting simulation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("Cathedral God Rays", fps=60)
    # Light atmospheric fog for god rays
    movie.add_atmosphere(
        fog_density="light",
        fog_color="warm_haze",
        volumetric=True,
        volumetric_scattering=2.0
    )
    
    # Main window light (dramatic god rays)
    movie.add_light_directional("WindowLight")\
        .rotation(pitch=-45, yaw=-90)\
        .intensity(12.0)\
        .color((1.0, 0.95, 0.9))\
        .cast_volumetric_shadow(True)\
        .light_shafts("dramatic")
    
    # Secondary fill light (subtle)
    movie.add_light_directional("FillLight")\
        .rotation(pitch=-75, yaw=90)\
        .intensity(4.0)\
        .color((0.7, 0.8, 1.0))\
        .cast_volumetric_shadow(False)\
        .light_shafts("subtle")
    
    # Add two characters
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Priest", location=(-500, 0, 0), yaw_offset=-90, mesh_path=belica_path)
    movie.add_actor("Visitor", location=(500, 0, 0), yaw_offset=90, mesh_path=belica_path)
    
    with movie.for_actor("Priest") as priest:
        priest.stay().anim("Idle").for_time(12.0)
    
    with movie.for_actor("Visitor") as visitor:
        visitor.stay().anim("Idle").for_time(2.0)
        visitor.face(Direction.WEST, duration=1.0)
        visitor.move_straight().anim("Walk_Fwd").direction(Direction.WEST).distance_in_time(800.0, 8.0)
        visitor.stay().anim("Idle").for_time(1.0)
    
    # Cinematic camera
    movie.add_camera("WideCam", location=(0, -1500, 400), fov=60)\
         .look_at_subject("Visitor", height_pct=0.7)\
         .add()
    
    with movie.for_camera("WideCam") as cam:
        cam.wait(12.0)
    
    movie.at_time(0.0).camera_cut("WideCam")
    
    return movie


if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
