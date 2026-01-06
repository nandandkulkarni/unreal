"""
Test Atmosphere Integration - Verify atmosphere system works with motion builder
"""
from motion_builder import MovieBuilder

# Build a simple test scene with atmosphere
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

# Save
movie.save_to_tracks()
print("✓ Test atmosphere integration movie saved")

