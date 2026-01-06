"""Evening/Dusk - Warm orange sunset light with golden hour fog"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction

def define_movie():
    movie = MovieBuilder("Evening Dusk", fps=30)
    
    # Golden hour atmosphere - medium fog, warm orange/red tones
    movie.add_atmosphere(
        fog_density="medium",
        fog_color=(1.0, 0.5, 0.3),  # Warm orange/red sunset fog
        volumetric=True,
        volumetric_scattering=2.5,
        volumetric_albedo=(1.0, 0.85, 0.7),  # Golden glow
        fog_height_falloff=0.08
    )
    
    # Low sunset sun with god rays
    movie.add_light_directional("SunsetSun")\
        .rotation(pitch=-8, yaw=270)\
        .intensity(9.0)\
        .color((1.0, 0.6, 0.35))\
        .use_as_atmospheric_sun(True)\
        .cast_volumetric_shadow(True)\
        .light_shafts("dramatic")
    
    # Add visual sun sphere at horizon (west)
    sphere_path = "/Engine/BasicShapes/Sphere.Sphere"
    movie.add_actor("Sun", location=(25000, 0, -3000), mesh_path=sphere_path)
    
    # Add moonlight (faint, opposite side)
    movie.add_light_directional("RisingMoon")\
        .rotation(pitch=-20, yaw=90)\
        .intensity(1.5)\
        .color((0.8, 0.85, 1.0))\
        .cast_volumetric_shadow(False)
    
    # Add visual moon sphere (east, rising)
    movie.add_actor("Moon", location=(-18000, 0, 5000), mesh_path=sphere_path)
    
    # Character walking into the sunset
    belica_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    movie.add_actor("Wanderer", location=(0, -1500, 0), yaw_offset=0, mesh_path=belica_path)
    
    with movie.for_actor("Wanderer") as wanderer:
        wanderer.stay().anim("Idle").for_time(1.5)
        wanderer.move_straight().anim("Walk_Fwd").direction(Direction.WEST).distance_at_speed(3500.0, 2.0)
        wanderer.stay().anim("Idle").for_time(2.0)
    
    # Cinematic side camera capturing silhouette
    movie.add_camera("CinematicCam", location=(200, -800, 200), fov=70)\
         .look_at_subject("Wanderer", height_pct=0.7)\
         .add()
    
    with movie.for_camera("CinematicCam") as cam:
        cam.wait(14.0)
    
    movie.at_time(0.0).camera_cut("CinematicCam")
    
    return movie

if __name__ == "__main__":
    movie = define_movie()
    movie.save_to_tracks()
    movie.run(to_unreal=True)
