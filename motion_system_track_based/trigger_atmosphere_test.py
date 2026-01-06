"""
Trigger test_atmosphere_integration movie
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder

# Define the test movie
movie = MovieBuilder("test_atmosphere_integration", fps=30)

# Add atmosphere first
movie.add_atmosphere(
    fog_density=0.2,  # Dense reddish fog (highly visible)
    fog_color=(1.0, 0.4, 0.3),  # Reddish like twilight
    volumetric=True,
    volumetric_scattering=2.0,
    volumetric_albedo=(1.0, 0.96, 0.92),  # Warm silver lining
    fog_height_falloff=0.05
)

# Add a directional light as atmospheric sun
movie.add_light_directional("sun")\
    .rotation(pitch=-10, yaw=180, roll=0)\
    .intensity(8.0)\
    .color((1.0, 0.7, 0.4))\
    .cast_volumetric_shadow(True)\
    .use_as_atmospheric_sun(True)

# Add a simple camera
movie.add_camera("main_cam", location=(0, -500, 200), fov=90)\
    .rotation((-10, 0, 0))\
    .add()

# Save and run
movie.save_to_tracks()
movie.run(to_unreal=True)
print("✓ Triggered atmosphere test in Unreal")
