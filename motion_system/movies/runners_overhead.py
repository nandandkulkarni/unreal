"""
Overhead Runners Scene
Two runners moving North, tracked by a high-angle front camera.
Uses Typed Units and Direction Enum.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motion_builder import MovieBuilder, Direction, DistanceUnit, SpeedUnit, TimeUnit

def define_movie():
    with MovieBuilder("Overhead Runners", fps=60) as movie:
        #movie.add_floor("Track", location=(0, 0, -0.5), scale=2000)
        #movie.add_directional_light("Sun", intensity="bright")

        # Two runners starting at origin, slightly offset in Y
        # Facing North (Positive X)
        movie.add_actor("Runner1", location=(0, -150, 0), yaw_offset=-90)
        movie.add_actor("Runner2", location=(0, 150, 0), yaw_offset=-90)

        # Overhead Camera (Front-High)
        # Runners run towards +X (North).
        # Camera is positioned far North (+X) and High (+Z), looking back.
        # We start looking at Runner1.
        movie.add_camera("OverheadFrontCam", location=(4000, 0, 1500)) \
             .look_at("Runner1") \
             .add()

        movie.at_time(0).camera_cut("OverheadFrontCam")

        with movie.simultaneous():
            with movie.for_actor("Runner1") as r1:
                # Runner 1 (West side) runs NORTH_EAST
                r1.move_straight().direction(Direction.NORTH_EAST).anim("Jog_Fwd") \
                  .distance_at_speed((DistanceUnit.Meters, 100), (SpeedUnit.MetersPerSecond, 6))
                r1.stay().till_end().anim("Idle")

            with movie.for_actor("Runner2") as r2:
                # Runner 2 (East side) runs NORTH_WEST
                # Start delay allows them to cross paths without collision
                r2.stay().for_time(2.0).anim("Idle")
                r2.move_straight().direction(Direction.NORTH_WEST).anim("Jog_Fwd") \
                  .distance_at_speed((DistanceUnit.Meters, 100), (SpeedUnit.MetersPerSecond, 6))
                r2.stay().till_end().anim("Idle")

        movie.save_to_json("dist/runners_overhead.json")

    movie.run(to_unreal=True)

if __name__ == "__main__":
    define_movie()
